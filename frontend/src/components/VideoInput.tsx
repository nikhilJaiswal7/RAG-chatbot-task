"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface VideoInputProps {
  onAnalyze: (ytUrl: string, igUrl: string) => Promise<void>;
  isLoading: boolean;
}

export default function VideoInput({ onAnalyze, isLoading }: VideoInputProps) {
  const [ytUrl, setYtUrl] = useState("");
  const [igUrl, setIgUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ytUrl && igUrl) {
      onAnalyze(ytUrl, igUrl);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto p-6 bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl shadow-xl"
    >
      <h2 className="text-2xl font-bold text-white mb-6 text-center">Analyze Video Performance</h2>
      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-gray-300">YouTube URL</label>
          <input
            type="url"
            required
            placeholder="https://youtube.com/watch?v=..."
            value={ytUrl}
            onChange={(e) => setYtUrl(e.target.value)}
            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
          />
        </div>
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-gray-300">Instagram Reel URL</label>
          <input
            type="url"
            required
            placeholder="https://instagram.com/reel/..."
            value={igUrl}
            onChange={(e) => setIgUrl(e.target.value)}
            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-pink-500 transition-all"
          />
        </div>
        <div className="flex items-end pb-1">
          <button
            type="submit"
            disabled={isLoading || !ytUrl || !igUrl}
            className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze"
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
