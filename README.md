<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=SocialRAG&fontSize=80&animation=fadeIn&fontAlignY=35&desc=The%20Next-Gen%20Video%20Intelligence%20Platform&descAlignY=60&descSize=20" width="100%" />

  <p align="center">
    <b>Empowering Creators with Deterministic State-Machine RAG.</b>
  </p>

  <p align="center">
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" /></a>
    <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs" /></a>
    <a href="https://langchain.com/"><img src="https://img.shields.io/badge/LangGraph-State_Machine-orange?style=for-the-badge" /></a>
    <a href="https://qdrant.tech/"><img src="https://img.shields.io/badge/Qdrant-Vector_DB-red?style=for-the-badge&logo=qdrant" /></a>
  </p>

  <p align="center">
    <a href="#-the-problem">The Problem</a> •
    <a href="#-the-solution">The Solution</a> •
    <a href="#-technical-blueprint">Architecture</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-power-queries">Power Queries</a>
  </p>
</div>

---

## 📖 Project Description
**SocialRAG** is the first deterministic video intelligence platform built specifically for the high-frequency content economy. While traditional RAG systems struggle with temporal context and fragmented data, SocialRAG introduces a **State-Machine Architecture** that treats video transcripts as living timelines. 

It enables creators to perform "Temporal Comparison"—analyzing how a hook in a 15-second YouTube Short compares to a 60-second Instagram Reel—by grounding every AI response in sub-second transcript segments. By combining **Groq's ultra-low latency inference** with **local vector generation**, SocialRAG delivers a production-grade strategist that is fast, free to scale, and contextually bulletproof.

## 🎬 Project Demo
> [!IMPORTANT]
> **Click the image below** to watch the full technical walkthrough and performance demo of SocialRAG.

[![SocialRAG Demo](https://img.youtube.com/vi/placeholder/0.jpg)](https://www.loom.com/share/your-loom-link-here)

*The demo covers: Side-by-side ingestion, real-time metadata extraction, and multi-turn strategic chat analysis.*

---

## 📉 The Problem
Content creators currently fly blind when comparing platforms. 
- **Fragmented Data**: Metrics for YouTube and Instagram live in different worlds.
- **Surface-Level Insights**: Standard tools show views, but not *why* the views happened.
- **Context Loss**: Linear AI chatbots forget video specifics across long analysis sessions.

## 📈 The Solution: SocialRAG
**SocialRAG** is a high-fidelity intelligence platform that bridges the gap between raw metrics and strategic content shifts.

- **Dual-Platform Ingestion**: One-click analysis for YouTube and Instagram Reels.
- **State-Machine Reasoning**: Uses **LangGraph** to maintain a persistent, evolving understanding of the content.
- **Zero-Quota Failure**: Engineered with local embedding fallbacks to remain functional when cloud APIs hit their limits.

---

## 🏗️ Technical Blueprint

### 1. Resilient Data Lifecycle
The system employs an **Asynchronous Concurrency Model**:
- **Ingest**: Parallel fetching of metadata using `yt-dlp` and `youtube-transcript-api`.
- **Transcribe**: In-memory audio processing routed through **Groq's Whisper-Large-V3** (Sub-second latency).
- **Embed**: Local **MiniLM-L6-v2** vector generation (100% Free, 0ms Network Latency).

### 2. State-Machine Orchestration
Unlike standard RAG, SocialRAG utilizes a **deterministic DAG (Directed Acyclic Graph)**:
1.  **Intent Expansion**: Resolves pronouns and context (e.g., "Tell me more about *that* hook").
2.  **Context Isolation**: Dual-path retrieval ensures Video A context never pollutes Video B analysis.
3.  **Strategic Synthesis**: **Llama-3.3-70B** performs high-signal reasoning, citing sources via **[Xs] Timestamps**.

---

## ✨ Core Features
*   🚀 **Turbo Extraction**: Metrics appear in <10s using `extract_flat` optimizations.
*   🧠 **Smart Query Refinement**: Follow-up questions work perfectly—the AI remembers the context.
*   🕒 **Temporal RAG**: Search and cite specific video segments (e.g., "The hook in the first 5s").
*   🎨 **Premium UI**: 60FPS animations, liquid transitions, and distinct source highlighting.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/) (Free tier works perfectly)

### 1. Backend Power-up
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate # On Windows
pip install -r requirements.txt

# Create .env
echo "GROQ_API_KEY=your_key_here" > .env
echo "OPENAI_API_KEY=optional_key" >> .env

# Run it
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Launch
```bash
cd frontend
npm install
npm run dev
```

---

## 🎯 Power Queries to Try
SocialRAG shines with comparative, multi-turn analysis. Try these:
1.  *"Which video has a higher engagement rate and why?"*
2.  *"Analyze the hooks in the first 10 seconds of both."*
3.  *"Suggest 3 specific script changes for Video B based on Video A's transcript."*
4.  *"Who is the creator of Video B and what hashtags did they use?"*

---

<div align="center">
  <sub>Built for the next generation of creators. Engineering by <b>Principal AI Engineer</b>.</sub>
</div>
