from dotenv import load_dotenv
load_dotenv()

from langchain_community.chat_models import ChatOpenAI
from rag.vector_store import create_vector_store
from rewriter import rewrite_query

# Hybrid Search and Loader initialization
from hybrid_search import HybridSearch
from rag.loader import load_documents

# Intent and State Management imports
from intent_detector import detect_intent
from state_manager import update_state


# ---------------------------
# INITIALIZE COMPONENTS
# ---------------------------

documents = load_documents()
hybrid_search = HybridSearch(documents)
vector_store = create_vector_store()

# Initialize LLM once (better performance)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)


# ---------------------------
# MAIN QA FUNCTION
# ---------------------------

def answer_question(question: str, history=None, state=None) -> str:

    # 1. INITIALIZE STATE
    if state is None:
        state = {}

    # 2. INTENT DETECTION
    intent = detect_intent(question)

    if intent == "greeting":
        return "Hey there! I'm your SAGE Digital Ambassador. How can I help you explore our campus today?"

    if intent == "admission":
        return "I'd be happy to help with admissions! Which specific program are you interested in, like BCA, B.Tech, or MBA?"

    # 3. UPDATE CONVERSATION STATE
    state = update_state(state, intent, question)

    # 4. HANDLE SLOT FILLING (missing program info)
    if state.get("intent") == "fees" and "program" not in state:
        return "I can definitely help with fee details! Which program's fee would you like to know? (e.g., BCA, B.Tech, or MBA)"

    # 5. QUERY ENRICHMENT
    search_query = question

    if state.get("program"):
        search_query = f"{state['program']} {question}"

    # 6. QUERY REWRITE USING HISTORY
    if history:
        search_query = rewrite_query(search_query, history)

    # 7. HYBRID RETRIEVAL
    vector_docs = vector_store.similarity_search(search_query, k=4)
    keyword_docs = hybrid_search.keyword_search(search_query, k=3)

    docs = list({doc.page_content: doc for doc in vector_docs + keyword_docs}.values())

    if len(docs) == 0:
        return "I'm sorry, I couldn't find those specific details in my records. Could you tell me which department or program you're asking about so I can look closer?"

    context = "\n\n".join([doc.page_content for doc in docs])

    # 8. PROCESS CHAT HISTORY
    chat_context = ""

    if history:
        for msg in history[-4:]:
            chat_context += f"{msg['role']}: {msg['content']}\n"

    # 9. DIGITAL AMBASSADOR PROMPT
    prompt = f"""
You are the SAGE University Digital Ambassador. Your goal is to talk like a helpful senior student or a friendly mentor—not a marketing brochure.

### YOUR VOICE
- **Real Talk:** Avoid words like "unyielding dedication," "shining star," or "strategic growth."
- **Focus on 'You':** Instead of saying "The university provides...", say "You'll get access to..."
- **Summarize & Simplify:** If the context is long, pick the 2-3 most exciting parts.
- **Natural Flow:** Use occasional transitions like "Actually," "Beyond that," or "One of the coolest things is..."
- **The "Brochure" Ban:** Strictly do not copy-paste full sentences. Rephrase everything into a spoken-style response.

### GUIDELINES
- Limit your response to 3-5 sentences.
- Use the context provided below for accuracy. 
- If the info isn't there, just say: "I don't have the specifics on that right now. It's best to check with the admissions office directly!"

### CONTEXT
{context}

### CHAT HISTORY
{chat_context}

### USER QUESTION
{question}

Final Answer (Casual, friendly, and helpful):

Final Answer (Respond as a friendly ambassador):
"""

    # 10. LLM RESPONSE
    response = llm.invoke(prompt)

    return response.content