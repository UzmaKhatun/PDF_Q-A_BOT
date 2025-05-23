# 📄 PDF Q&A Bot 🤖

An intelligent AI-powered chatbot that allows users to **upload any PDF** and **ask questions** based on its content. Built with **Groq LLM**, **LangChain**, **FAISS**, and **Streamlit**, this project extracts knowledge from documents and delivers clear, context-aware answers.

---

## 🚀 Features

- 📁 Upload and process PDF documents
- 🧠 Ask natural language questions based on the PDF content
- 🔍 Semantic search using **FAISS** and **SentenceTransformers**
- 📊 Token usage and document statistics
- 📝 Tips for asking better questions
- 💬 Chat history with real-time LLM responses

---

## 🛠️ Tech Stack

| Tool           | Description                            |
|----------------|----------------------------------------|
| **Python**     | Core backend logic                     |
| **Streamlit**  | Web-based UI                           |
| **LangChain**  | Document loading and LLM orchestration |
| **FAISS**      | Efficient vector similarity search     |
| **Groq LLM**   | Fast and intelligent language model    |
| **SentenceTransformers** | Text embedding for semantic search |

---

## 📷 Demo

![Screenshot](screenshots/overview.png)

🔗 *Watch the [project demo](#)*

---

## 🔑 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/pdf_que_ans_bot.git
   cd pdf_que_ans_bot
   
2. **Create a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
