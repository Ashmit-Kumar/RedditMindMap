import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str) -> list[float]:
    """
    Use Gemini's embedding-001 model to convert text into a vector.

    Returns
    -------
    list[float]
        A 1536-dimensional embedding vector.
    """
    model = genai.EmbeddingModel(model_name="models/embedding-001")

    try:
        result = model.embed_content(
            content=text,
            task_type="RETRIEVAL_QUERY",  # or "RETRIEVAL_DOCUMENT"
            title="Reddit Persona"
        )
        return result["embedding"]
    except Exception as e:
        print("[!] Error generating embedding:", e)
        return []
