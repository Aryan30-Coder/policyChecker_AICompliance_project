from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def load_document(doc_path: str):
    """Loads PDF, DOCX, or TXT documents into LangChain format."""
    if doc_path.endswith(".pdf"):
        loader = PyPDFLoader(doc_path)
    elif doc_path.endswith(".docx"):
        loader = Docx2txtLoader(doc_path)
    elif doc_path.endswith(".txt"):
        loader = TextLoader(doc_path)
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

    documents = loader.load()
    return documents


def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Splits documents into smaller overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)
    return chunks


def store_vector(chunks, db_type = "docs"):
    """Stores the chucks generated in the VectorDB."""
    embedder = HuggingFaceEmbeddings(model = "all-MiniLM-L6-v2")
    persist_directory = f"data/ChromaDB_{db_type}"
    vectordb = Chroma.from_documents(
        documents = chunks,
        embedding = embedder,
        persist_directory = persist_directory
    )
    
    vectordb.persist()
    print(f"✅ Stored {len(chunks)} chunks in Chroma at {persist_directory}")
    
    return vectordb
