from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

def load_documents():

    loader = DirectoryLoader(
        "data/docs/",
        glob="*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} pages from PDF")

    return documents