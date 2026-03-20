import requests
from config import CONFIG


class Embedder:
    def __init__(self):
        self.base_url = CONFIG["ollama"]["base_url"]
        self.model = "nomic-embed-text:latest"

    def embed(self, text: str) -> list:
        resp = requests.post(
            f"{self.base_url}/api/embed", json={"model": self.model, "input": text}
        )
        return resp.json()["embeddings"][0]

    def embed_many(self, texts: list) -> list:
        resp = requests.post(
            f"{self.base_url}/api/embed", json={"model": self.model, "input": texts}
        )
        return resp.json()["embeddings"]
