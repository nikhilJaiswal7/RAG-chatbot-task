from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from services.qdrant_store import query_qdrant
from core.config import settings

class GraphState(TypedDict):
    """
    Phase 2: LangGraph State definition.
    Maintains conversation history and video-specific contexts.
    """
    messages: List[BaseMessage]
    video_a_context: List[str]
    video_b_context: List[str]
    metadata: Dict[str, Any]

# Fallback to Groq if confirmed key is working
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY, streaming=True)

def retrieve_node(state: GraphState):
    """
    Node 1: Smart Retriever
    Uses conversation context to refine the search query, then performs dual scoped searches.
    """
    # Principal Upgrade: Query Refinement
    # If there's history, we want a standalone query that captures the user's intent
    messages = state["messages"]
    last_user_query = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
    
    if len(messages) > 1:
        # Refine query using Llama 3 for speed
        refinement_prompt = f"""Given the following conversation and a new user question, generate a standalone search query that can be used to retrieve relevant video transcript segments.
Conversation History:
{messages[:-1]}
New Question: {last_user_query}
Standalone Query:"""
        try:
            refined_response = llm.invoke(refinement_prompt)
            search_query = refined_response.content
            logger.info(f"Smart RAG: Refined query from '{last_user_query}' to '{search_query}'")
        except:
            search_query = last_user_query
    else:
        search_query = last_user_query

    # Strictly scoped retrieval using the refined query
    context_a_data = query_qdrant(search_query, "A", top_k=5) # Increased top_k for better context
    context_b_data = query_qdrant(search_query, "B", top_k=5)
    
    # Format context with precise segment references
    context_a = [f"[Video A, Segment {item['chunk_id']}]: {item['text']}" for item in context_a_data]
    context_b = [f"[Video B, Segment {item['chunk_id']}]: {item['text']}" for item in context_b_data]
    
    return {
        "video_a_context": context_a, 
        "video_b_context": context_b
    }

async def generate_node(state: GraphState):
    """
    Node 2: Generator
    Synthesizes a high-signal response using timestamped context and performance metadata.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior Social Media Content Strategist and Growth Engineer. 
You are performing a deep-dive comparison between two videos to extract actionable insights for a creator.

### OPERATIONAL DATA:
[VIDEO A - YOUTUBE]
Metadata: {metadata_a}
Transcript Excerpts: {context_a}

[VIDEO B - INSTAGRAM REEL]
Metadata: {metadata_b}
Transcript Excerpts: {context_b}

### STRATEGIC TASKS:
1. **Engagement Deep-Dive**: Compare views, likes, comments, and engagement rates. Explain WHY one outperformed the other based on platform-specific audience behavior.
2. **Hook Analysis**: Specifically analyze the first 5-10 seconds of both videos (using the provided [Xs] timestamps in transcripts). Which hook is more "sticky"?
3. **Content Quality**: Evaluate the pacing, messaging, and CTA (Call to Action) based on the transcripts.
4. **Citations**: EVERY statement regarding content MUST be cited using [Video A, Xs] or [Video B, Xs] to match the transcript timestamps.
5. **Action Plan**: Suggest 3 specific, data-backed improvements for Video B based on the successful elements found in Video A.

### TONE:
Be professional, analytical, and highly critical (like a top-tier consultant). Do not use fluff. If data is missing, state it clearly.
"""),
        ("placeholder", "{messages}")
    ])
    
    chain = prompt | llm
    
    # Extract metadata for A and B for easier prompt injection
    meta = state.get("metadata", {})
    meta_a = meta.get("video_a", {})
    meta_b = meta.get("video_b", {})
    
    response = await chain.ainvoke({
        "metadata_a": meta_a,
        "metadata_b": meta_b,
        "context_a": "\n".join(state.get("video_a_context", [])),
        "context_b": "\n".join(state.get("video_b_context", [])),
        "messages": state["messages"]
    })
    
    return {"messages": [response]}

# Build the LangGraph state machine
workflow = StateGraph(GraphState)

workflow.add_node("retriever", retrieve_node)
workflow.add_node("generator", generate_node)

workflow.add_edge(START, "retriever")
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", END)

# Compile the graph
app = workflow.compile()
