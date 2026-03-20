import os
from utils.embedder import Embedder
from utils.vector_store import VectorStore


class RAG:
    def __init__(self, collection_name: str = "project_code"):
        self.embedder = Embedder()
        self.vector_store = VectorStore(collection_name)

    def is_empty(self) -> bool:
        try:
            results = self.vector_store.collection.get(limit=1)
            return len(results.get("ids", [])) == 0
        except Exception:
            return True

    def _file_already_indexed(self, path: str) -> bool:
        try:
            results = self.vector_store.collection.get(where={"source": path}, limit=1)
            return len(results.get("ids", [])) > 0
        except Exception:
            return False

    def index_files(self, file_paths: list):
        files_to_index = [
            path for path in file_paths if not self._file_already_indexed(path)
        ]
        if not files_to_index:
            return

        all_chunks = []
        all_ids = []
        all_metadatas = []

        for path in files_to_index:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = self._split(content)
                for i, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    all_ids.append(f"{path}_chunk_{i}")
                    all_metadatas.append({"source": path, "chunk_index": i})
            except Exception:
                continue

        if all_chunks:
            embeddings = self.embedder.embed_many(all_chunks)
            self.vector_store.add(
                texts=all_chunks,
                embeddings=embeddings,
                ids=all_ids,
                metadatas=all_metadatas,
            )

    def update_file(self, path: str):
        try:
            self.vector_store.collection.delete(where={"source": path})
        except Exception:
            pass

        if os.path.exists(path):
            self.index_files([path])

    def scan_and_index(self, directories: list, extensions: list, exclude: list = []):
        file_paths = []
        for directory in directories:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in exclude]
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_paths.append(os.path.join(root, file))
        if file_paths:
            self.index_files(file_paths)

    def query(self, question: str, n_results: int = 5) -> str:
        embedding = self.embedder.embed(question)
        results = self.vector_store.query(embedding, n_results=n_results)
        return "\n\n---\n\n".join(results)

    def _split(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list:
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
