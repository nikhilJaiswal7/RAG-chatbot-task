import asyncio
import os
import tempfile
import yt_dlp
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from groq import AsyncGroq
from core.config import settings
from models.schemas import VideoMetadata

# Configure professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        self.ydl_opts_base = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': True, # Don't follow playlists
            'noplaylist': True,   # Strictly enforce no playlist
            'socket_timeout': 15,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

    def _get_info(self, url: str, retries: int = 2) -> dict:
        """Fetch video info with a retry mechanism for production stability."""
        # Clean URL to prevent playlist extraction
        if "youtube.com" in url or "youtu.be" in url:
            if "&list=" in url:
                url = url.split("&list=")[0]
            if "?list=" in url:
                url = url.split("?list=")[0]

        last_error = None
        for attempt in range(retries):
            try:
                logger.info(f"yt-dlp extracting info for {url} (attempt {attempt + 1})")
                with yt_dlp.YoutubeDL(self.ydl_opts_base) as ydl:
                    info = ydl.extract_info(url, download=False)
                    logger.info(f"yt-dlp successfully extracted info for {url}")
                    return info
            except Exception as e:
                last_error = e
                logger.warning(f"yt-dlp attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(1)
        raise last_error

    async def get_metadata(self, url: str, platform: str, video_id: str) -> VideoMetadata:
        """Asynchronously extract metadata for a video with high resilience."""
        try:
            logger.info(f"Starting metadata extraction for {platform}: {url}")
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._get_info, url)
            
            views = info.get('view_count', 0) or 0
            likes = info.get('like_count', 0) or 0
            comments = info.get('comment_count', 0) or 0
            
            # Instagram often obfuscates view counts in yt-dlp; using likes as a floor heuristic
            if platform == "instagram" and views == 0 and likes > 0:
                views = int(likes * 10) # Conservative floor estimate
            
            engagement_rate = 0.0
            if views > 0:
                engagement_rate = ((likes + comments) / views) * 100

            # Smart Extraction: Tags/Hashtags
            tags = info.get('tags', []) or []
            if not tags and info.get('description'):
                # Extract hashtags from description if tags field is empty
                import re
                tags = re.findall(r"#(\w+)", info.get('description'))

            metadata = VideoMetadata(
                video_id=video_id,
                platform=platform,
                views=views,
                likes=likes,
                comments=comments,
                creator=info.get('uploader', info.get('uploader_id', 'Unknown')),
                follower_count=info.get('channel_follower_count') or info.get('uploader_subscriber_count'),
                upload_date=info.get('upload_date', 'Unknown'),
                duration=float(info.get('duration', 0.0)),
                engagement_rate=engagement_rate,
                hashtags=tags[:10] # Limit to top 10
            )
            logger.info(f"Metadata extraction successful for {platform}")
            return metadata
        except Exception as e:
            logger.error(f"Metadata extraction fatal error [{platform}] for {url}: {e}")
            return VideoMetadata(
                video_id=video_id, platform=platform, views=0, likes=0, comments=0,
                creator="Unknown", upload_date="Unknown", duration=0.0, engagement_rate=0.0
            )

    async def extract_transcript(self, url: str, platform: str) -> str:
        """Fetch transcript based on platform."""
        logger.info(f"Starting transcript extraction for {platform}: {url}")
        if platform == "youtube":
            return await self._get_youtube_transcript(url)
        elif platform == "instagram":
            return await self._get_instagram_transcript(url)
        return ""

    async def _get_youtube_transcript(self, url: str) -> str:
        try:
            # Extract ID
            video_id = None
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            if not video_id:
                info = await asyncio.get_event_loop().run_in_executor(None, self._get_info, url)
                video_id = info.get('id')

            if not video_id:
                return ""
            
            logger.info(f"Fetching YouTube transcript for {video_id}")
            try:
                # The global YouTubeTranscriptApi is imported at the top
                # Try the instance-based fetch first as it's often more reliable in some envs
                api = YouTubeTranscriptApi()
                transcript_list = api.fetch([video_id])
                transcript = transcript_list[0] if transcript_list else []
            except Exception as e:
                logger.warning(f"Instance fetch failed for {video_id}, trying class method: {e}")
                try:
                    # Fallback to class-level list/fetch
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                except Exception as e2:
                    logger.error(f"All transcript methods failed for {video_id}: {e2}")
                    return ""
            
            if not transcript:
                return ""
                
            return " ".join([f"[{int(t['start'])}s]: {t['text']}" for t in transcript])
        except Exception as e:
            logger.error(f"YouTube transcript fatal error for {url}: {e}")
            return ""

    async def _get_instagram_transcript(self, url: str) -> str:
        if not self.groq_client: return "Groq API Key missing"
        
        temp_dir = tempfile.gettempdir()
        temp_filename = f"ig_{os.urandom(4).hex()}"
        output_template = os.path.join(temp_dir, f"{temp_filename}.%(ext)s")
        
        ydl_opts = {
            **self.ydl_opts_base,
            'extract_flat': False, # Need full info for audio download
            'skip_download': False, 
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            loop = asyncio.get_event_loop()
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"

            file_path = await loop.run_in_executor(None, _download)
            
            if not os.path.exists(file_path):
                potential_path = file_path.replace(".mp3", "") + ".mp3"
                if os.path.exists(potential_path): file_path = potential_path
            
            with open(file_path, "rb") as audio_file:
                transcription = await self.groq_client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), audio_file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                )
            
            if os.path.exists(file_path): os.remove(file_path)
            
            return " ".join([f"[{int(s['start'])}s]: {s['text']}" for s in transcription.segments])
        except Exception as e:
            logger.error(f"Instagram transcript error: {e}")
            return ""

extractor = VideoExtractor()
