from fastapi import APIRouter, HTTPException
import asyncio
from models.schemas import IngestRequest, IngestResponse, VideoMetadata
from services.extractor import extractor
from services.qdrant_store import store_transcript

router = APIRouter()

import logging

# Configure logging
logger = logging.getLogger(__name__)

async def safe_extract(coro, default_value, label):
    try:
        async with asyncio.timeout(45): # Increased to 45s
            return await coro
    except Exception as e:
        logger.error(f"Task {label} failed or timed out: {e}")
        return default_value

@router.post("/ingest", response_model=IngestResponse)
async def ingest_videos(request: IngestRequest):
    """
    Phase 1: Backend Ingestion & Extraction
    Asynchronously extracts metadata and transcripts from YouTube and Instagram.
    Uses ultra-resilient graceful degradation.
    """
    try:
        logger.info(f"Starting ingestion for YT: {request.youtube_url} and IG: {request.instagram_url}")
        
        # Step 1 & 2: Run all extraction tasks in parallel with individual safe wrappers
        meta_a_task = safe_extract(
            extractor.get_metadata(request.youtube_url, "youtube", "A"),
            VideoMetadata(video_id="A", platform="youtube", views=0, likes=0, comments=0, creator="Unknown", upload_date="Unknown", duration=0.0, engagement_rate=0.0),
            "Metadata A"
        )
        meta_b_task = safe_extract(
            extractor.get_metadata(request.instagram_url, "instagram", "B"),
            VideoMetadata(video_id="B", platform="instagram", views=0, likes=0, comments=0, creator="Unknown", upload_date="Unknown", duration=0.0, engagement_rate=0.0),
            "Metadata B"
        )
        transcript_a_task = safe_extract(extractor.extract_transcript(request.youtube_url, "youtube"), "", "Transcript A")
        transcript_b_task = safe_extract(extractor.extract_transcript(request.instagram_url, "instagram"), "", "Transcript B")
        
        logger.info("Executing extraction tasks...")
        meta_a, meta_b, transcript_a, transcript_b = await asyncio.gather(
            meta_a_task, meta_b_task, transcript_a_task, transcript_b_task
        )

        logger.info("Extraction phase complete. Processing results...")
        
        # Step 3: Chunk, Embed, and Store in Qdrant
        # We handle storage errors internally in store_transcript
        loop = asyncio.get_event_loop()
        await asyncio.gather(
            loop.run_in_executor(None, store_transcript, transcript_a, "A", "youtube"),
            loop.run_in_executor(None, store_transcript, transcript_b, "B", "instagram"),
            return_exceptions=True # Don't let one storage failure stop the other
        )
        
        return IngestResponse(
            video_a=meta_a,
            video_b=meta_b,
            message="Successfully processed videos (Partial success if some sources were unavailable)."
        )
    except Exception as e:
        logger.error(f"Ingestion pipeline fatal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
