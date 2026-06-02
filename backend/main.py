from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, chat

app = FastAPI(title="Video RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video RAG Chatbot API"}
