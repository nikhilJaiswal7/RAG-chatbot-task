"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import { motion } from "framer-motion";
import { AppMetadata } from "@/types";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatPanelProps {
  metadata: AppMetadata;
}

export default function ChatPanel({ metadata }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm ready to compare these two videos. What would you like to know?" }
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsStreaming(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newMessages, // Correctly passing history for memory
          metadata
        }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      setMessages(prev => [...prev, { role: "assistant", content: "" }]);

      let accumulatedResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") break;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                accumulatedResponse += parsed.content;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1].content = accumulatedResponse;
                  return updated;
                });
              }
            } catch (e) {
              // Ignore partial JSON or heartbeats
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: "assistant", content: "⚠️ Connection failed. Ensure backend is running at :8000." }]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto flex flex-col h-[650px] bg-white/[0.02] backdrop-blur-2xl border border-white/10 rounded-[2.5rem] shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)] overflow-hidden"
    >
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide">
        {messages.map((msg, idx) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={idx} 
            className={`flex gap-6 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${
              msg.role === 'user' 
                ? 'bg-gradient-to-tr from-purple-600 to-pink-600' 
                : 'bg-white/5 border border-white/10'
            }`}>
              {msg.role === 'user' ? <User size={24} className="text-white" /> : <Bot size={24} className="text-purple-400" />}
            </div>
            <div className={`max-w-[85%] rounded-[2rem] px-7 py-5 shadow-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-white/10 text-white border border-white/10 rounded-tr-none' 
                : 'bg-white/[0.03] text-gray-200 border border-white/5 rounded-tl-none font-medium'
            }`}>
              <p className="whitespace-pre-wrap">
                {msg.content.split(/(\[Video [A|B], \d+s\])/g).map((part, i) => (
                  part.match(/\[Video [A|B], \d+s\]/) ? (
                    <span key={i} className="px-1.5 py-0.5 rounded-md bg-purple-500/20 text-purple-400 text-xs font-bold border border-purple-500/30 mx-0.5">
                      {part}
                    </span>
                  ) : part
                ))}
              </p>
            </div>
          </motion.div>
        ))}
        {isStreaming && messages[messages.length - 1]?.role === "user" && (
          <div className="flex gap-6">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 bg-white/5 border border-white/10">
              <Bot size={24} className="text-purple-400 animate-pulse" />
            </div>
            <div className="bg-white/[0.03] text-gray-400 border border-white/5 rounded-[2rem] rounded-tl-none px-7 py-5 flex items-center gap-3">
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce"></span>
              </span>
              <span className="text-sm font-semibold tracking-wide uppercase opacity-50">Strategizing</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-6 bg-black/40 border-t border-white/5">
        <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto">
          <div className="flex-1 relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about hook performance or suggest improvements..."
              disabled={isStreaming}
              className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all disabled:opacity-50 pr-14"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="absolute right-2 top-2 bottom-2 px-4 bg-white text-black hover:bg-gray-200 rounded-xl font-bold transition-all disabled:opacity-20 flex items-center justify-center"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
