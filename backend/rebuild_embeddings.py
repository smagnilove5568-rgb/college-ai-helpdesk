from rag.vector_store import create_vector_store

print("Rebuilding embeddings...")
vector_store = create_vector_store()
print("Embeddings created successfully!")