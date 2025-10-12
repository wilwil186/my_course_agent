# build_index.py
import os
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_DIR = os.getenv("DOCS_DIR", "PDF")  # ajusta si tus docs están en otra carpeta
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "data/faiss_index")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")

def load_documents():
    base = Path(DOCS_DIR)
    if not base.exists():
        print(f"[build_index] No existe el directorio de documentos: {base.resolve()}")
        return []

    docs = []
    # PDFs
    docs += DirectoryLoader(
        DOCS_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True, use_multithreading=True
    ).load()
    # TXT
    docs += DirectoryLoader(
        DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader, show_progress=True, use_multithreading=True
    ).load()
    # MD
    docs += DirectoryLoader(
        DOCS_DIR, glob="**/*.md", loader_cls=TextLoader, show_progress=True, use_multithreading=True
    ).load()

    return docs

def main():
    print("[build_index] Cargando documentos…")
    docs = load_documents()

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    Path(FAISS_INDEX_DIR).mkdir(parents=True, exist_ok=True)

    if not docs:
        print("[build_index] No se encontraron documentos. Creando índice mínimo para evitar errores.")
        vs = FAISS.from_texts([""], embeddings)
        vs.save_local(FAISS_INDEX_DIR, index_name=FAISS_INDEX_NAME)
        print(f"[build_index] Índice vacío creado en {Path(FAISS_INDEX_DIR).resolve()}")
        return

    print(f"[build_index] {len(docs)} documento(s) cargados. Fragmentando…")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    print(f"[build_index] {len(chunks)} fragmentos.")

    print("[build_index] Calculando embeddings y construyendo FAISS…")
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(FAISS_INDEX_DIR, index_name=FAISS_INDEX_NAME)
    print(f"[build_index] ¡Listo! Índice guardado en {Path(FAISS_INDEX_DIR).resolve()}")

if __name__ == "__main__":
    main()
