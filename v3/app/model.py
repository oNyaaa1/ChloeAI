import httpx
from .config import settings

class OllamaError(RuntimeError):
    pass

async def chat(messages: list[dict[str, str]], system: str | None = None) -> str:
    payload_messages = ([{"role": "system", "content": system}] if system else []) + messages
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json={"model": settings.ollama_chat_model, "messages": payload_messages, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise OllamaError(f"Could not get a response from Ollama: {exc}") from exc

async def embed(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/embed",
                json={"model": settings.ollama_embed_model, "input": text},
            )
            response.raise_for_status()
            vectors = response.json()["embeddings"]
            if not vectors or not vectors[0]:
                raise OllamaError("Ollama returned an empty embedding")
            return vectors[0]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise OllamaError(f"Could not create embedding with Ollama: {exc}") from exc
