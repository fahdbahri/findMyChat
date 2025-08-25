from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from google import genai
import os
import logging
from services.vault_encryption import batch_decrypt

router = APIRouter()
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    user_id: str
    query: str


class SearchResponse(BaseModel):
    answer: str
    context: list[str]


es = Elasticsearch("http://elasticsearch:9200")
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@router.post("/search", response_model=SearchResponse)
async def rag_search(request: SearchRequest):
    try:
        query_vec = model.encode([request.query])[0].tolist()

        search_body = {
            "knn": {
                "field": "embeddings",
                "query_vector": query_vec,
                "k": 5,
                "num_candidates": 20,
            },
            "query": {
                "bool": {
                    "filter": [{"term": {"user_id": request.user_id}}],
                }
            },
        }

        response = es.search(index="messages", body=search_body)
        hits = response["hits"]["hits"]

        if not hits:
            return SearchResponse(answer="No relevant messages found.", context=[])

        ciphertexts = [hit["_source"]["encrypted_message"] for hit in hits]
        decrypted_texts = batch_decrypt(ciphertexts, "chat-msg")

        context_text = "\n".join(decrypted_texts)
        # threshold for summarization
        if len(context_text) > 500:
            prompt = f"""
            You are a retrieval assistant. 
            User query: "{request.query}"

            Here are relevant chat messages:
                {context_text}

            - Only use the given messages to answer.
            - If you find the answer, summarize or quote it.
            - If it's not in the messages, say "No relevant info found."
            """

            gemini_response = genai_client.models.generate_content(
                model="gemini-1.5-flash", contents=prompt
            )

            answer = gemini_response.text.strip()
        else:
            answer = context_text

        return SearchResponse(answer=answer, context=decrypted_texts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
