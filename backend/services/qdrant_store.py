from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

qdrant = QdrantClient(settings.QDRANT_URL)
COLLECTION_NAME = "video_transcripts"

# Use local embeddings to resolve 429 quota issues
logger.info("Initializing local HuggingFace embeddings (all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def init_qdrant():
    try:
        qdrant.get_collection(COLLECTION_NAME)
    except:
        # MiniLM size is 384
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

init_qdrant()

import logging

logger = logging.getLogger(__name__)

def store_transcript(transcript: str, video_id: str, platform: str):
    if not transcript:
        logger.info(f"No transcript available for video {video_id} ({platform}). Skipping storage.")
        return
        
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(transcript)
        
        if not chunks:
            return
            
        logger.info(f"Embedding {len(chunks)} chunks for video {video_id}...")
        vectors = embeddings.embed_documents(chunks)
        
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "video_id": video_id,
                    "platform": platform,
                    "text": chunk,
                    "chunk_id": i
                }
            )
            for i, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Successfully stored {len(points)} points in Qdrant for video {video_id}")
    except Exception as e:
        logger.error(f"Error storing transcript in Qdrant for video {video_id}: {e}")
        raise # Re-raise to be caught in the router

def query_qdrant(query: str, video_id: str, top_k: int = 3) -> list:
    query_vector = embeddings.embed_query(query)
    
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue
    
    # Use query_points which is confirmed to exist in this version
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="video_id",
                    match=MatchValue(value=video_id)
                )
            ]
        ),
        limit=top_k
    )
    
    return [{"text": hit.payload["text"], "chunk_id": hit.payload.get("chunk_id", 0)} for hit in search_result.points]
