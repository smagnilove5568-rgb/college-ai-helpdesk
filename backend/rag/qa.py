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

documents = load_documents()
hybrid_search = HybridSearch(documents)
vector_store = create_vector_store()

def answer_question(question: str, history=None, state=None) -> str:
    # 1. INITIALIZE STATE
    if state is None:
        state = {}

    # 2. INTENT DETECTION (Move to top to catch greetings immediately)
    intent = detect_intent(question)

    if intent == "greeting":
        return "Hey there! I'm your SAGE Digital Ambassador. How can I help you explore our campus today?"

    if intent == "admission":
        return "I'd be happy to help with admissions! Which specific program are you interested in, like BCA, B.Tech, or MBA?"

    # 3. STATE UPDATES
    state = update_state(state, question)

    # --- USE STATE FOR CLARIFICATION ---
    if state.get("intent") == "fees" and "program" not in state:
        return "I can definitely help with fee details! Which program's fee would you like to know? (e.g., BCA, B.Tech, or MBA)"

    # 4. QUERY ENRICHMENT
    # This ensures "What are the placements?" becomes "B.Tech What are the placements?"
    search_query = question
    if state.get("program"):
        search_query = f"{state['program']} {question}"

    # 5. REWRITE QUERY BASED ON HISTORY
    if history:
        search_query = rewrite_query(search_query, history)

    # 6. HYBRID RETRIEVAL
    vector_docs = vector_store.similarity_search(search_query, k=4)
    keyword_docs = hybrid_search.keyword_search(search_query, k=3)
    
    docs = list({doc.page_content: doc for doc in vector_docs + keyword_docs}.values())
    
    # Check for empty results
    if len(docs) == 0:
        return "I'm sorry, I couldn't find those specific details in my records. Could you tell me which department or program you're asking about so I can look closer?"

    context = "\n\n".join([doc.page_content for doc in docs])

    # 7. PROCESSING CONVERSATION HISTORY
    chat_context = ""
    if history:
        for msg in history[-4:]:
            chat_context += f"{msg['role']}: {msg['content']}\n"
    
    # 8. DIGITAL AMBASSADOR PROMPT
    prompt = f"""
You are the SAGE University Digital Ambassador—a helpful, friendly, and knowledgeable guide for students.

### YOUR STYLE GUIDELINES:
- **Be Conversational:** Don't just list facts. Use phrases like "Actually, SAGE has..." or "If you're looking for..."
- **No Copy-Pasting:** Rephrase the context in your own words. Speak like a person, not a database.
- **Connect the Dots:** If a user asks about facilities, explain how they help the student (e.g., "Our 75-acre campus includes advanced labs, which is perfect for the hands-on learning we focus on.")
- **Stay Accurate:** Use the context provided below for your facts. If the information isn't there, suggest they contact the college office.

### KNOWLEDGE CONTEXT:
{context}

### RECENT CHAT HISTORY:
{chat_context}

### USER QUESTION:
{question}

Final Answer (Respond as a friendly ambassador):
"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    response = llm.invoke(prompt)
    return response.content