from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate   # updated version for prompt template
# from langchain.schema import Document
from langchain_groq import ChatGroq
import numpy as np
import pdfplumber
import faiss
import os

# Set Groq API Key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Load sentence transformer model
embedder = SentenceTransformer('all-MiniLM-L6-v2')
llm = ChatGroq(api_key=GROQ_API_KEY ,model_name="llama-3.3-70b-versatile", temperature=0)

# PDF Text Extraction 
def load_pdf_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

# Chunking 
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Embedding + FAISS Indexing
def embed_chunks(chunks):
    vectors = embedder.encode(chunks)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors))
    return index, vectors, chunks

# Retrieve Relevant Chunks
def retrieve_relevant_chunks(query, index, vectors, chunks, top_k=3):
    query_vec = embedder.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)
    return [chunks[i] for i in indices[0]]

# Answering the Question Using LLM 
def answer_question(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"Use the following text to answer the question:\n\n{context}\n\nQuestion: {query}\nAnswer:"
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        return f"❌ Error from LLM: {str(e)}"
