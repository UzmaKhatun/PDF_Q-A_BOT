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

🔗 *Watch the [project demo](https://pdf-que-ans-bot-webapp.streamlit.app/)*

---

## 🔑 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/UzmaKhatun/PDF_Q-A_BOT.git
   cd pdf_que_ans_bot
   
2. **Create a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
   ```
   pip install -r requirements.txt

4. **Run the Streamlit app**
   ```
   streamlit run app.py

#### Configuration
- You can set the api_key manually or use .env for security:
  ````
  GROQ_API_KEY=your_groq_key_here
- Optional parameters like chunk size, overlap, embedding model, etc., can be configured in config.py or directly in app.py.

---- 

## 📂 Folder Structure
📁 PDF_Q-A_BOT/
- ├── app.py               # Main Streamlit app
- ├── qa_engine.py         # Core Q&A logic
- ├── requirements.txt     # Dependencies
- └── README.md            # Project documentation

----

## 🤝 Contributing
Contributions, feedback, and suggestions are welcome! Feel free to fork the repo, create issues, or submit PRs.

----

## 🙋‍♀️ Author
Uzma Khatun
AI/ML Enthusiast | BCA Student | Building intelligent tools with passion

📫 Let’s connect on [LinkedIn](https://www.linkedin.com/in/uzma-khatun-88b990334/)

---

## 🌟 If you found this useful, give it a star ⭐ and share it with others!
