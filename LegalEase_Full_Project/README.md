# LegalEase AI — Complete Full-Stack Project

LegalEase is a modern AI-powered legal document generator built for a project/demo submission.

## Main features

- Modern AI-first dark/glassmorphism interface
- AI conversation panel
- Rental Agreement
- Non-Disclosure Agreement
- Employment Contract
- Freelance Service Agreement
- Gemini 2.5 Flash integration
- Local fallback drafting when Gemini is not configured
- Live document preview
- Clause suggestion chips
- Copy-to-clipboard
- PDF export
- Responsive design
- Dark/light theme
- FastAPI REST backend
- Health endpoint

## Architecture

Browser
  ↓
HTML / CSS / JavaScript
  ↓
FastAPI
  ↓
Gemini 2.5 Flash
  ↓
Generated legal draft
  ↓
Live preview / PDF export

## Requirements

- Python 3.10+
- Gemini API key (optional for demo mode)

## Windows setup

Open Command Prompt or PowerShell inside this folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and put your Gemini key in it:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Start:

```bash
uvicorn main:app --reload
```

Open:

http://127.0.0.1:8000

## Without a Gemini key

The application still runs. It uses a deterministic local drafting template so you can demonstrate the complete workflow.

## Project structure

```text
LegalEase_Full_Project/
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

## API

### Generate
POST `/api/generate`

### AI chat
POST `/api/chat`

### PDF
POST `/api/pdf`

### Health
GET `/health`

## Important legal note

LegalEase generates drafts for educational and drafting assistance. It is not a replacement for a qualified lawyer. Documents should be reviewed for the relevant jurisdiction and facts before signing or relying upon them.

## Suggested project title

**LegalEase: AI-Powered Legal Document Generator**

## Suggested presentation flow

1. Problem statement
2. Existing system limitations
3. Proposed LegalEase solution
4. AI workflow
5. System architecture
6. UI demonstration
7. Document generation demo
8. PDF export demo
9. Future scope
