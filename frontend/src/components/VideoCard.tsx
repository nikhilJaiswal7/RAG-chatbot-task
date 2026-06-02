import { motion } from "framer-motion";
import { Video, Smartphone, Users, Heart, MessageCircle, Eye, TrendingUp } from "lucide-react";
import { VideoMetadata } from "@/types";

interface VideoCardProps {
  data: VideoMetadata;
  platform: "youtube" | "instagram";
}

export default function VideoCard({ data, platform }: VideoCardProps) {
  const isYouTube = platform === "youtube";
  
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US', { notation: "compact", compactDisplay: "short" }).format(num);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className={`p-6 rounded-3xl border bg-white/5 backdrop-blur-xl shadow-2xl relative overflow-hidden group ${
        isYouTube ? "border-red-500/20" : "border-pink-500/20"
      }`}
    >
      {/* Dynamic Background Glow */}
      <div className={`absolute -top-24 -right-24 w-48 h-48 blur-3xl opacity-20 transition-opacity group-hover:opacity-40 rounded-full ${
        isYouTube ? "bg-red-500" : "bg-pink-500"
      }`} />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className={`p-4 rounded-2xl ${isYouTube ? 'bg-red-500/20 text-red-400' : 'bg-pink-500/20 text-pink-400'}`}>
              {isYouTube ? <Video size={28} /> : <Smartphone size={28} />}
            </div>
            <div>
              <h3 className="text-xl font-bold text-white tracking-tight">{data.creator}</h3>
              <p className="text-gray-400 text-sm flex items-center gap-1 font-medium">
                <Users size={14} /> {data.follower_count ? formatNumber(data.follower_count) : 'N/A'}
              </p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
            isYouTube ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-pink-500/10 text-pink-400 border border-pink-500/20"
          }`}>
            {platform}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <StatBox label="Views" value={formatNumber(data.views)} icon={<Eye size={14}/>} />
          <StatBox label="Likes" value={formatNumber(data.likes)} icon={<Heart size={14}/>} />
          <StatBox label="Comments" value={formatNumber(data.comments)} icon={<MessageCircle size={14}/>} />
          
          <motion.div 
            whileHover={{ scale: 1.02 }}
            className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-4 rounded-2xl border border-purple-500/30 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1">
              <p className="text-gray-300 text-[10px] font-bold uppercase tracking-widest">Engagement</p>
              <TrendingUp size={12} className="text-purple-400" />
            </div>
            <p className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 leading-none">
              {data.engagement_rate.toFixed(2)}%
            </p>
          </motion.div>
        </div>

        {data.hashtags && data.hashtags.length > 0 && (
          <div className="mt-6 flex flex-wrap gap-2">
            {data.hashtags.slice(0, 6).map((tag, i) => (
              <span key={i} className="px-2 py-1 rounded-lg bg-white/5 border border-white/10 text-[10px] text-gray-400 font-bold uppercase tracking-tight">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

function StatBox({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) {
  return (
    <div className="bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
      <p className="text-gray-400 text-[10px] font-bold uppercase tracking-widest mb-1 flex items-center gap-1.5">
        {icon} {label}
      </p>
      <p className="text-xl font-bold text-white leading-none">{value}</p>
    </div>
  );
}
