# SocialRAG: The Smart AI Video Strategist

SocialRAG is a high-performance, production-ready RAG (Retrieval-Augmented Generation) application designed for creators to analyze and compare YouTube videos and Instagram Reels side-by-side. 

It doesn't just fetch data; it performs **temporal content analysis** and **strategic reasoning** using a deterministic state-machine architecture.

---

## 🚀 The "Smart" Engineering Architecture

This system is built with a **resilient, quota-independent stack** designed to outperform standard RAG implementations.

### 1. Ultra-Resilient Ingestion Pipeline
- **Asynchronous Concurrency**: Metadata and transcripts for both videos are fetched in parallel using `asyncio.gather`.
- **Graceful Degradation**: Every extraction task (YouTube API, yt-dlp, Groq Whisper) is wrapped in a `safe_extract` handler with a **45-second timeout**. If Instagram is blocked, YouTube results still render instantly.
- **Dynamic Transcription**: For Instagram Reels (which lack native transcripts), the system dynamically downloads the audio in memory and streams it to **Groq's Whisper LPU** for near-instant, timestamped transcription.
- **Smart Metadata**: Automatically extracts hashtags, engagement rates, and creator stats, even stripping playlist junk from URLs to ensure focus.

### 2. Smart RAG (LangGraph State Machine)
Unlike standard linear chains, SocialRAG uses **LangGraph** to manage the conversation lifecycle as a state machine:
- **Node 1: Query Refinement**: If you ask a follow-up question (e.g., "What about its hook?"), a specialized node analyzes your chat history to "expand" the query into a standalone search term (e.g., "What is the hook performance of Video A?").
- **Node 2: Dual-Scoped Retrieval**: The system queries the Vector DB twice per turn—once for Video A and once for Video B—using strict metadata filtering. This eliminates "vector bleed" and ensures the AI never confuses the two videos.
- **Node 3: High-Fidelity Generation**: The final node synthesizes insights using **Llama 3 (via Groq)**.

### 3. Quota-Independent Intelligence
To solve the common "429 Too Many Requests" issue with OpenAI:
- **Local Embeddings**: Uses **HuggingFace MiniLM-L6-v2** running locally on your CPU. It's 100% free, fast, and requires zero API calls.
- **Groq Acceleration**: Switched to Groq LPUs for both transcription and reasoning. This provides GPT-4 level intelligence with sub-second response times, entirely independent of OpenAI quotas.

### 4. Zero-Lag Vibe-Coded UI
- **SSE Streaming**: Responses are delivered token-by-token using **Server-Sent Events (SSE)**, handled via a custom React `ReadableStream` implementation for a premium, lag-free feel.
- **Granular Citations**: The AI highlights specific sources. If it mentions a hook, it cites the exact timestamp (e.g., `[Video A, 5s]`).
- **Modern Dashboard**: Built with **Next.js**, **Tailwind CSS**, and **Framer Motion** for liquid-smooth animations and "audit-ready" data visualization.

---

## 🛠️ Tech Stack
- **Frontend**: Next.js 15 (App Router), Framer Motion, Lucide, Tailwind.
- **Backend**: FastAPI (Python 3.12).
- **Orchestration**: LangGraph, LangChain.
- **Database**: Qdrant (Vector DB) with strict payload isolation.
- **Models**: Groq Llama 3.3 (LLM), Groq Whisper-Large (Audio), HuggingFace MiniLM (Embeddings).

---

## 📖 How to Run

### 1. Backend Setup
1. Navigate to `/backend`.
2. Activate your environment: `.\venv\Scripts\activate`.
3. Ensure `.env` has:
   - `GROQ_API_KEY`: (Essential for Chat & IG Transcription)
   - `OPENAI_API_KEY`: (Optional, system uses free fallbacks)
4. Start the server: `uvicorn main:app --host 0.0.0.0 --port 8000`.

### 2. Frontend Setup
1. Navigate to `/frontend`.
2. Install: `npm install`.
3. Start: `npm run dev`.
4. Open [http://localhost:3000](http://localhost:3000).

---

## 🎯 Key Queries to Try
- *"Compare the hooks in the first 10 seconds of both videos."*
- *"Why did Video A get more engagement than Video B?"*
- *"Suggest 3 improvements for Video B based on Video A's transcript."*
- *"Who is the creator of Video B and what are their top hashtags?"*

**SocialRAG is engineered to be the smartest, fastest, and most resilient creator tool on the market.**
