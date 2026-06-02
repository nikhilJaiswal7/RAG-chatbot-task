"use client";

import { useState } from "react";
import VideoInput from "@/components/VideoInput";
import VideoCard from "@/components/VideoCard";
import ChatPanel from "@/components/ChatPanel";
import { motion, AnimatePresence } from "framer-motion";
import { AppMetadata } from "@/types";
import { Sparkles } from "lucide-react";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [metadata, setMetadata] = useState<AppMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (ytUrl: string, igUrl: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: ytUrl, instagram_url: igUrl }),
      });

      if (!response.ok) throw new Error("Failed to analyze videos. Verify URLs and try again.");

      const data = await response.json();
      setMetadata({ video_a: data.video_a, video_b: data.video_b });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white selection:bg-purple-500/30 overflow-x-hidden">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-900/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-pink-900/20 blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>
      
      <div className="relative z-10 container mx-auto px-6 py-16 space-y-16">
        <header className="text-center space-y-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center gap-3 mb-2"
          >
            <div className="p-2 bg-gradient-to-tr from-purple-500 to-pink-500 rounded-lg">
              <Sparkles className="text-white" size={24} />
            </div>
            <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50">
              SOCIAL<span className="text-purple-500">RAG</span>
            </h1>
          </motion.div>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-gray-400 max-w-2xl mx-auto text-lg font-medium leading-relaxed"
          >
            Deep AI analysis and comparative insights for YouTube and Instagram. 
            Powered by GPT-4o-mini & Groq Whisper.
          </motion.p>
        </header>

        <VideoInput onAnalyze={handleAnalyze} isLoading={isLoading} />

        <AnimatePresence mode="wait">
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="max-w-2xl mx-auto p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-center font-bold"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {metadata && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-16"
            >
              <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                <VideoCard data={metadata.video_a} platform="youtube" />
                <VideoCard data={metadata.video_b} platform="instagram" />
              </div>

              <div className="max-w-5xl mx-auto pt-8 border-t border-white/5">
                <ChatPanel metadata={metadata} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
