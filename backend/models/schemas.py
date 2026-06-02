from pydantic import BaseModel
from typing import Optional, List

class IngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str

class VideoMetadata(BaseModel):
    video_id: str # 'A' or 'B'
    platform: str
    views: int
    likes: int
    comments: int
    creator: str
    follower_count: Optional[int] = None
    upload_date: str
    duration: float
    engagement_rate: float
    hashtags: List[str] = []

class IngestResponse(BaseModel):
    video_a: VideoMetadata
    video_b: VideoMetadata
    message: str
