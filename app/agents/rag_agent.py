import chromadb
import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# initialize ChromaDB - stores data locally in ./chroma_db folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="financial_reports")

def save_report_to_rag(report_text: str, country: str, report_date: str):
    """Save a generated report into ChromaDB for future retrieval"""
    
    # create a unique ID for this report
    report_id = f"{country}_{report_date}".replace(" ", "_").replace(",", "")
    
    # split report into chunks (simple approach - by paragraphs)
    chunks = [chunk.strip() for chunk in report_text.split("\n\n") if chunk.strip()]
    
    # add each chunk to ChromaDB
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            metadatas=[{
                "country": country,
                "report_date": report_date,
                "chunk_index": i
            }],
            ids=[f"{report_id}_chunk_{i}"]
        )
    
    return {"saved_chunks": len(chunks), "report_id": report_id}

def search_reports(question: str, n_results: int = 5):
    """Search ChromaDB for relevant report chunks"""
    
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    return results

def rag_agent(question: str) -> dict:
    try:
        # step 1 - search for relevant chunks
        results = search_reports(question)
        
        if not results['documents'][0]:
            return {
                "question": question,
                "answer": "No relevant past reports found. Try generating some reports first using the /agent/report endpoint."
            }
        
        # step 2 - combine retrieved chunks as context
        context_chunks = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        context = "\n\n---\n\n".join([
            f"[From {meta['country']} report dated {meta['report_date']}]\n{chunk}"
            for chunk, meta in zip(context_chunks, metadatas)
        ])
        
        # step 3 - ask Claude to answer using retrieved context
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    You are a financial analyst assistant for Atlas Commercial Bank.
                    Answer the question using ONLY the information provided in the context below.
                    If the context doesn't contain enough information, say so.
                    
                    Context from past reports:
                    {context}
                    
                    Question: {question}
                    
                    Provide a clear, concise answer citing which report(s) you used.
                    """
                }
            ]
        )
        
        return {
            "question": question,
            "answer": response.content[0].text.strip(),
            "sources": [
                {"country": meta['country'], "report_date": meta['report_date']}
                for meta in metadatas
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}
