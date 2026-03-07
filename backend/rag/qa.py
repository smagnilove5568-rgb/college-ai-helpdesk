from dotenv import load_dotenv
load_dotenv()

from langchain_community.chat_models import ChatOpenAI
from rag.vector_store import create_vector_store
# Step 2: Import the rewriter function
from rewriter import rewrite_query

vector_store = create_vector_store()

# Step 2: Update function signature to include history
def answer_question(question: str, history=None) -> str:
    # Step 2: Logic to rewrite the query if history exists
    if history:
        question = rewrite_query(question, history)

    # Step 2: Search FAISS with k=5 as shown in the update
    docs = vector_store.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Updated Prompt as per Step 2 screenshot
    prompt = f"""
You are a helpful SAGE University assistant.

Use the context below to answer the question clearly.

Context:
{context}

Question:
{question}

Answer:
"""
    # Step 2: Using gpt-4o-mini as shown in your screenshot
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(prompt)
    return response.content