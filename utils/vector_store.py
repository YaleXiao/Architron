import chromadb


class VectorStore:
    def __init__(self, collection_name: str):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, texts, embeddings, ids, metadatas=None):
        self.collection.add(
            documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas
        )

    def query(self, query_embedding, n_results=5) -> list:
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )
        return results.get("documents", [[]])[0]
