import asyncio
import sys
import time
import streamlit as st
import tempfile
import os
from datetime import datetime

from qa_engine import load_pdf_text, chunk_text, embed_chunks, retrieve_relevant_chunks, answer_question

# Fix for Windows + Python 3.8+
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Track token usage
tokens_used = 0
last_reset_time = time.time()

def estimate_tokens(text):
    return len(text.split())  # basic token estimation (1 word = 1 token)

def rate_limit_check(new_tokens, max_tokens_per_minute=6000):
    global tokens_used, last_reset_time
    current_time = time.time()

    # Reset every 60 seconds
    if current_time - last_reset_time >= 60:
        tokens_used = 0
        last_reset_time = current_time

    # If over the limit, wait
    if tokens_used + new_tokens > max_tokens_per_minute:
        wait_time = 60 - (current_time - last_reset_time)
        st.warning(f"🚦 Token rate limit reached. Waiting for {int(wait_time)} seconds...")
        time.sleep(wait_time)
        tokens_used = 0
        last_reset_time = time.time()

    tokens_used += new_tokens

# Custom CSS for enhanced styling with dark theme support
def load_custom_css():
    st.markdown("""
    <style>
    /* Dark theme detection */
    @media (prefers-color-scheme: dark) {
        .main-header {
            background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        }
        
        .upload-section {
            background: #2d3748;
            border-color: #4a5568;
            color: #e2e8f0;
        }
        
        .upload-section:hover {
            border-color: #667eea;
            background: #1a202c;
        }
        
        .sidebar-info {
            background: #2d3748;
            border-left-color: #fbbf24;
            color: #e2e8f0;
        }
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
        color: #495057;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }
    
    /* Dark theme specific styles */
    [data-theme="dark"] .upload-section,
    .stApp[data-theme="dark"] .upload-section {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    [data-theme="dark"] .upload-section:hover,
    .stApp[data-theme="dark"] .upload-section:hover {
        background: #1a202c;
        border-color: #667eea;
    }
    
    [data-theme="dark"] .sidebar-info,
    .stApp[data-theme="dark"] .sidebar-info {
        background: #2d3748;
        color: #e2e8f0;
        border-left-color: #fbbf24;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        min-width: 150px;
        margin: 0.5rem;
        border-left: 4px solid #667eea;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .question-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        color: #000000;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .answer-box {
        background: #f1f8e9;
        padding: 1.5rem;
        border-radius: 8px;
        color: #000000;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    
    .sidebar-info {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        color: #856404;
    }
    
    .suggestion-box {
        background: #e8f4fd;
        color: #000000;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .suggestion-box h4 {
        margin-top: 0;
        color: #1976d2;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .suggestion-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e3f2fd;
    }
    
    .suggestion-item:hover {
        background: #f3f9ff;
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
    }
    
    /* Dark theme for suggestions */
    [data-theme="dark"] .suggestion-box,
    .stApp[data-theme="dark"] .suggestion-box {
        background: #2d3748;
        color: #e2e8f0;
    }
    
    [data-theme="dark"] .suggestion-item,
    .stApp[data-theme="dark"] .suggestion-item {
        background: #4a5568;
        color: #e2e8f0;
        border-color: #2d3748;
    }
    
    [data-theme="dark"] .suggestion-item:hover,
    .stApp[data-theme="dark"] .suggestion-item:hover {
        background: #1a202c;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to reset PDF state
def reset_pdf_state():
    st.session_state.pdf_processed = False
    st.session_state.chat_history = []
    st.session_state.pdf_stats = {}
    if 'pdf_data' in st.session_state:
        del st.session_state.pdf_data
    if 'current_pdf_name' in st.session_state:
        del st.session_state.current_pdf_name

# Initialize session state
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_stats' not in st.session_state:
    st.session_state.pdf_stats = {}
if 'show_suggestions' not in st.session_state:
    st.session_state.show_suggestions = False
if 'current_pdf_name' not in st.session_state:
    st.session_state.current_pdf_name = None

# Streamlit UI Configuration
st.set_page_config(
    page_title="PDF Q&A Bot", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 PDF Q&A Bot</h1>
    <p>Upload a PDF and ask intelligent questions powered by AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information and settings
with st.sidebar:
    st.markdown("### 📊 Session Statistics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Questions Asked", len(st.session_state.chat_history))
    with col2:
        st.metric("Tokens Used", tokens_used)
    
    st.markdown("### ⚙️ Settings")
    max_tokens = st.slider("Max Tokens per Minute", 1000, 10000, 6000, 500)
    
    st.markdown("""
    <div class="sidebar-info">
        <h4>💡 Tips for Better Results</h4>
        <ul>
            <li>Ask specific questions</li>
            <li>Reference particular sections</li>
            <li>Use clear, concise language</li>
            <li>Break complex queries into parts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File upload section
    st.markdown("### 📁 Upload Your PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf",
        help="Upload a PDF document to analyze and ask questions about"
    )
    
    # Check if a new PDF is uploaded or if no PDF is uploaded
    if uploaded_file is None:
        if st.session_state.pdf_processed:
            reset_pdf_state()
            st.rerun()
    elif uploaded_file and (not st.session_state.pdf_processed or st.session_state.current_pdf_name != uploaded_file.name):
        # Reset state for new PDF
        if st.session_state.current_pdf_name != uploaded_file.name:
            reset_pdf_state()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name
        
        with st.spinner("📚 Processing PDF... This may take a moment"):
            progress_bar = st.progress(0)
            
            # Simulate progress updates
            progress_bar.progress(25)
            raw_text = load_pdf_text(pdf_path)
            
            progress_bar.progress(50)
            chunks = chunk_text(raw_text)
            
            progress_bar.progress(75)
            index, vectors, chunk_texts = embed_chunks(chunks)
            
            progress_bar.progress(100)
            
            # Store processing results
            st.session_state.pdf_processed = True
            st.session_state.current_pdf_name = uploaded_file.name
            st.session_state.pdf_data = {
                'index': index,
                'vectors': vectors,
                'chunk_texts': chunk_texts
            }
            st.session_state.pdf_stats = {
                'filename': uploaded_file.name,
                'total_chunks': len(chunks),
                'total_characters': len(raw_text),
                'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        os.remove(pdf_path)
        st.success("✅ PDF processed successfully!")
        st.rerun()

with col2:
    if st.session_state.pdf_processed:
        st.markdown("### 📈 Document Statistics")
        stats = st.session_state.pdf_stats
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">{stats['total_chunks']}</div>
                <div class="stat-label">Text Chunks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_characters']:,}</div>
                <div class="stat-label">Characters</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"📄 **File:** {stats['filename']}")
        st.info(f"⏰ **Processed:** {stats['processed_at']}")

# Q&A Section
if st.session_state.pdf_processed:
    st.markdown("### 💬 Ask Questions About Your PDF")
    
    # Question input
    with st.form("question_form", clear_on_submit=True):
        query = st.text_area(
            "Your Question:",
            placeholder="What is the main topic of this document?",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_button = st.form_submit_button("🚀 Ask Question")
        with col2:
            suggest_button = st.form_submit_button("✨ Suggest Questions")
    
    # Handle suggest questions button
    if suggest_button:
        st.session_state.show_suggestions = True
        st.rerun()
    
    # Display suggestions if requested
    if st.session_state.show_suggestions:
        suggested_questions = [
            "What is the main purpose of this document?",
            "Can you summarize the key points discussed?",
            "What are the main conclusions or findings?",
            "Who is the target audience for this document?",
            "What methodology or approach is used?",
            "What are the key recommendations mentioned?"
        ]
        
        st.markdown(f"""
        <div class="suggestion-box">
            <h4>💡 Suggested Questions</h4>
            <p>Click on any question below to use it, or get inspired to ask your own:</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, question in enumerate(suggested_questions):
            if st.button(f"❓ {question}", key=f"suggest_{i}"):
                # Use the selected question
                with st.spinner("🤔 Generating answer..."):
                    est_query_tokens = estimate_tokens(question)
                    rate_limit_check(est_query_tokens, max_tokens)
                    
                    # Retrieve and answer
                    context_chunks = retrieve_relevant_chunks(
                        question, 
                        st.session_state.pdf_data['index'],
                        st.session_state.pdf_data['vectors'],
                        st.session_state.pdf_data['chunk_texts']
                    )
                    answer = answer_question(question, context_chunks)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'question': question,
                        'answer': answer,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    st.session_state.show_suggestions = False
                    st.rerun()
        
        if st.button("❌ Hide Suggestions"):
            st.session_state.show_suggestions = False
            st.rerun()
    
    if submit_button and query:
        with st.spinner("🤔 Generating answer..."):
            est_query_tokens = estimate_tokens(query)
            rate_limit_check(est_query_tokens, max_tokens)
            
            # Retrieve and answer
            context_chunks = retrieve_relevant_chunks(
                query, 
                st.session_state.pdf_data['index'],
                st.session_state.pdf_data['vectors'],
                st.session_state.pdf_data['chunk_texts']
            )
            answer = answer_question(query, context_chunks)
            
            # Add to chat history
            st.session_state.chat_history.append({
                'question': query,
                'answer': answer,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💭 Question {len(st.session_state.chat_history) - i} - {chat['timestamp']}", expanded=(i == 0)):
                st.markdown(f"""
                <div class="question-box">
                    <strong>❓ Question:</strong><br>
                    {chat['question']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="answer-box">
                    <strong>🤖 Answer:</strong><br>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True)

else:
    # Welcome message when no PDF is uploaded
    st.markdown("""
    <div class="upload-section">
        <h3>👋 Welcome to PDF Q&A Bot!</h3>
        <p>Upload a PDF document above to get started. Once processed, you can ask intelligent questions about its content.</p>
        <br>
        <p><strong>Features:</strong></p>
        <p>🔍 Semantic search • 🤖 AI-powered answers • 💬 Chat history • 📊 Token tracking</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Powered by Groq LLM • Built with Streamlit • Made with ❤️</p>
</div>
""", unsafe_allow_html=True)