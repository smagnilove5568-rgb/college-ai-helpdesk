from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .loader import load_documents
from .splitter import split_documents
import os

INDEX_PATH = "faiss_index"


def create_vector_store():

    embeddings = OpenAIEmbeddings()

    # if index already exists, load it
    if os.path.exists(INDEX_PATH):
        print("Loading existing FAISS index...")
        vector_store = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        return vector_store

    print("Creating new FAISS index...")

    documents = load_documents()
    chunks = split_documents(documents)

    vector_store = FAISS.from_documents(chunks, embeddings)

    vector_store.save_local(INDEX_PATH)

    print("FAISS index created and saved")

    return vector_store