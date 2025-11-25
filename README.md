# Draftly - AI-Assisted Document Authoring Platform

Draftly is a powerful platform that leverages Large Language Models (LLMs) to help users generate, refine, and export business-ready documents (Word .docx) and presentations (PowerPoint .pptx).

## Features
*   **Project Management**: Create and organize document generation projects.
*   **AI Content Generation**: Automatically generate outlines and detailed content sections using LLMs (Ollama, Gemini, etc.).
*   **Content Refinement**: Refine specific sections with AI instructions (e.g., "Make this more professional").
*   **Multi-Format Export**: Export projects to formatted Word documents and PowerPoint presentations.
*   **Interactive UI**: Modern, responsive interface built with React.

## Prerequisites
*   **Python 3.10+**
*   **Node.js 18+**
*   **PostgreSQL** (Local or Cloud)
*   **Ollama** (for local LLM support) or an API Key for Gemini/OpenAI.

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Draftly
```

### 2. Backend Setup
Navigate to the backend directory:
```bash
cd Backend
```

Create a virtual environment and activate it:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the `Backend` directory with the following variables:
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_DB=document_ai
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost/document_ai

# Security
SECRET_KEY=your_super_secret_key_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
# Options: 'ollama', 'gemini', 'openai'
LLM_PROVIDER=ollama

# If using Ollama (Local)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2

# If using Gemini
# GEMINI_API_KEY=your_gemini_api_key
```

Run database migrations (if applicable) or let the app create tables on startup.

Start the Backend Server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 3. Frontend Setup
Navigate to the frontend directory:
```bash
cd ../frontend
```

Install dependencies:
```bash
npm install
```

Create a `.env` file in the `frontend` directory (optional, defaults to localhost):
```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the Frontend Development Server:
```bash
npm run dev
```
The application will be available at `http://localhost:5173`.

## Usage Guide

1.  **Register/Login**: Create an account to access the dashboard.
2.  **Create Project**: Click "Create Project", enter a title, select a type (Word/PowerPoint), and provide a topic prompt.
3.  **Generate Content**: Use the "Generate outline & sections" panel to have the AI create the initial structure and content.
4.  **Edit & Refine**: Click on sections to edit text manually or use the "Refine" feature to update content with AI instructions.
5.  **Export**: Click "Export DOCX" or "Export PPTX" to download your finished document.

## Tech Stack
*   **Frontend**: React, TypeScript, Vite, Axios
*   **Backend**: FastAPI, SQLAlchemy, Pydantic
*   **Database**: PostgreSQL
*   **AI/LLM**: Ollama (Local), Google Gemini (Cloud)
