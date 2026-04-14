# MaIA — Kairos LinkedIn Prospecting Agent

MaIA is an AI-powered prospecting agent built for Agencia Kairos. It searches LinkedIn for potential clients using Google's `site:linkedin.com/in` operator via Serper, analyzes each profile with Claude Sonnet, and exports a ranked markdown report.

---

## Stack

- **Language:** Python
- **Framework:** FastAPI
- **Search:** Serper.dev (Google-based LinkedIn search)
- **AI Analysis:** Claude Sonnet 4.6 (Anthropic)
- **Deployment:** Vercel
- **Frontend:** Vanilla HTML/CSS/JS

---

## Project Structure

```
maia/
├── api/
│   └── index.py          # FastAPI app — Vercel entry point
├── src/
│   ├── __init__.py
│   ├── searcher.py       # Serper LinkedIn search
│   ├── analyzer.py       # Claude profile analysis
│   └── reporter.py       # Markdown report generator
├── public/
│   └── index.html        # Frontend UI
├── requirements.txt
├── vercel.json
├── .env.example
└── README.md
```

---

## Local Setup

### 1. Clone and install

```bash
cd maia
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
cp .env.example .env
# Edit .env with your keys
```

### 3. Run locally

```bash
uvicorn api.index:app --reload --port 8000
```

Open http://localhost:8000

---

## Deploy to Vercel

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial MaIA commit"
git remote add origin https://github.com/YOUR_USER/maia.git
git push -u origin main
```

### 2. Connect to Vercel

- Go to vercel.com → New Project → Import your GitHub repo
- Vercel will detect the Python configuration automatically

### 3. Add Environment Variables in Vercel

In your Vercel project settings → Environment Variables, add:

```
ANTHROPIC_API_KEY=your_key
SERPER_API_KEY=your_key
```

### 4. Deploy

Vercel will auto-deploy on every push to `main`.

---

## How It Works

1. You fill in search parameters: Industry, Role, Location, Company Size, Keywords
2. MaIA builds targeted `site:linkedin.com/in` queries and runs them via Serper
3. Each profile snippet is sent to Claude Sonnet 4.6 for analysis
4. Claude returns: fit score (1–10), why this lead matters, and a conversation angle
5. Results are displayed ranked by fit score
6. You can export the full report as a `.md` file

---

## Notes

- LinkedIn profiles are found via Google's index (Serper), not LinkedIn's API
- Profiles with strict privacy settings may not appear in results
- Up to 15 leads per run (configurable in `max_results`)
- All analysis is done by Claude in real-time — each run consumes API credits
