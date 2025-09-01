# ADA Compliance Checker - Task

Build a full stack application that provides a simple, intuitive interface to quickly check HTML document for
common accessibility issues.

---

## Technologies
  -- Backend: Django and Flask
  -- Frontend: React
---

## Project Structure
```
project-root/
├─ backend/
│  ├─ app.py                 # Flask API (runs on :8000)
│  ├─ utils.py               # HTML parsing + rules
│  └─ requirements.txt
└─ frontend/
   ├─ package.json           # has proxy → http://127.0.0.1:8000
   ├─ src/
   │  ├─ App.jsx             # React UI (MUI)
   │  ├─ Home.jsx             
   │  ├─ Page.jsx             # React UI (MUI)
   │  ├─ index.js
   │  └─ styles.css          # highlight style
   └─ public/
```

## Start (Two Terminals)

### 1) Backend — Flask API
```bash
cd backend
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py    # starts http://127.0.0.1:8000
```

### 2) Frontend — React
```bash
cd frontend
npm install
npm start        # opens http://localhost:3000
```

The frontend is preconfigured to proxy `/api/*` to `http://127.0.0.1:8000`.

---

## 🔌 Proxy Configuration (already set)
Ensure `frontend/package.json` contains:
```json
{
  "proxy": "http://127.0.0.1:8000"
}
```
This avoids CORS hassles during development.

---

## How to Use
1. Start **backend** (`python app.py`) and **frontend** (`npm start`).
2. In the UI:
   - Paste HTML into the textarea **or** click **Upload HTML** to load a file.
   - Click **Check**. Issues are listed on the right.
   - Click any issue to **highlight** the element in the live preview.

---

## API Reference
**POST** `/api/check/`

**Request (JSON):**
```json
{
  "html": "<html><head></head><body><img src='logo.png'></body></html>"
}
```

**Response (JSON):**
```json
{
  "issues": [
    {
      "ruleId": "DOC_TITLE_MISSING",
      "message": "Page is missing a non-empty <title> tag.",
      "element": "title",
      "selector": "head > title",
      "codeSnippet": "<title>"
    }
  ]
}
```

---

## Troubleshooting
- **Frontend can’t reach backend**
  - Ensure Flask is on `http://127.0.0.1:8000`.
  - Confirm `frontend/package.json` has the `proxy` entry.
  - Browser console → Network tab for errors.
- **Port already in use**
  - Change port: `python app.py` → modify `app.run(..., port=8000)` or kill the conflicting process.
- **cURL quoting on Windows**
  - Prefer PowerShell example above or use a REST client (Postman/Insomnia).

---

## Credits
Built for a take‑home assessment. Backend: Flask + BeautifulSoup + webcolors. Frontend: React + Material‑UI.

