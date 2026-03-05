from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from .loader import load_documents
from .splitter import split_documents


def create_vector_store():
    documents = load_documents()
    chunks = split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store