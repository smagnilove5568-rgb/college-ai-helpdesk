# test_loader.py

from rag.loader import load_documents

docs = load_documents()

print("Number of documents:", len(docs))
print("\nFirst document content:\n")
print(docs[0].page_content[:500])