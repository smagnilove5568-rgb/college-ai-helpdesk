from dotenv import load_dotenv
load_dotenv()

from langchain_community.chat_models import ChatOpenAI
from rag.vector_store import create_vector_store

vector_store = create_vector_store()


def answer_question(question: str) -> str:
    docs = vector_store.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""Use ONLY the following context to answer the question. If the answer is not found in the context, say "I don't know. Please contact the college office."

Context:
{context}

Question: {question}

Answer:"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    response = llm.invoke(prompt)
    return response.content

