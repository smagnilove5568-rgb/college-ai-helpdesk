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
    # Initialize state if missing
    if state is None:
        state = {}

    # Update state before anything else
    state = update_state(state, question)

    # --- USE STATE FOR CLARIFICATION ---
    if state.get("intent") == "fees" and "program" not in state:
        return "Sure! Which program's fee would you like to know? (BCA, B.Tech, MBA, etc.)"

    # --- ADDED: USE STATE IN QUESTION ---
    # This enriches the search query with the stored program context
    if state.get("program"):
        question = f"{state['program']} {question}"

    # Assistant Behavior based on Intent
    intent = detect_intent(question)

    if intent == "greeting":
        return "Hello! I'm the SAGE University AI assistant. How can I help you today?"

    if intent == "admission":
        return "I'd be happy to help with admissions! Which program are you interested in? (BCA, B.Tech, MBA, etc.)"

    # Logic to rewrite the query if history exists
    if history:
        question = rewrite_query(question, history)

    # Hybrid Retrieval logic (Vector + Keyword)
    vector_docs = vector_store.similarity_search(question, k=4)
    keyword_docs = hybrid_search.keyword_search(question, k=3)
    
    # Remove duplicate retrieval results for token efficiency
    docs = list({doc.page_content: doc for doc in vector_docs + keyword_docs}.values())
    
    # Check for empty results
    if len(docs) == 0:
        return "I couldn't find that information in my knowledge base. Could you clarify what program or department you are asking about?"

    context = "\n\n".join([doc.page_content for doc in docs])

    # Processing conversation context for the reasoning prompt
    chat_context = ""
    if history:
        for msg in history[-4:]:
            chat_context += f"{msg['role']}: {msg['content']}\n"
    
    # Reasoning-focused prompt structure
    prompt = f"""
You are an AI assistant for SAGE University Bhopal.

Follow this reasoning process before answering:

1. Identify the user's intent.
2. Check if the answer exists in the provided context.
3. If the context contains the answer, respond clearly and naturally.
4. If the question is vague or missing details, ask a polite clarification question.
5. If the information is not in the context, say you do not have enough information.

Conversation History:
{chat_context}

Context:
{context}

User Question:
{question}

Final Answer:
"""
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(prompt)
    return response.content