export interface VideoMetadata {
  video_id: string;
  platform: string;
  views: number;
  likes: number;
  comments: number;
  creator: string;
  follower_count: number | null;
  upload_date: string;
  duration: number;
  engagement_rate: number;
}

export interface AppMetadata {
  video_a: VideoMetadata;
  video_b: VideoMetadata;
}
