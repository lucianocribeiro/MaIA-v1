import sys
import os

# Ensure project root is in path for src/ imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import traceback

from src.searcher import search_linkedin_profiles
from src.analyzer import analyze_profiles
from src.reporter import generate_md_report

app = FastAPI(title="MaIA — Kairos LinkedIn Prospecting Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchParams(BaseModel):
    industry: Optional[str] = ""
    role: Optional[str] = ""
    location: Optional[str] = "Argentina"
    company_size: Optional[str] = ""
    keywords: Optional[str] = ""
    max_results: Optional[int] = 15


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend."""
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/search")
async def run_search(params: SearchParams):
    """
    Main search endpoint.
    1. Search LinkedIn profiles via Serper
    2. Analyze each with Claude
    3. Return leads + markdown report content
    """
    try:
        search_params = params.model_dump()

        # Step 1: Search
        print(f"[MaIA] Starting search with params: {search_params}")
        profiles = search_linkedin_profiles(search_params, params.max_results)

        if not profiles:
            return {
                "leads": [],
                "report_md": "",
                "total": 0,
                "message": "No LinkedIn profiles found for these parameters. Try broader keywords or a different role."
            }

        print(f"[MaIA] Found {len(profiles)} profiles. Analyzing...")

        # Step 2: Analyze
        analyzed = analyze_profiles(profiles, search_params)

        # Step 3: Generate report
        report_md = generate_md_report(analyzed, search_params)

        print(f"[MaIA] Done. {len(analyzed)} leads analyzed.")

        return {
            "leads": analyzed,
            "report_md": report_md,
            "total": len(analyzed),
            "message": f"Found and analyzed {len(analyzed)} leads."
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"MaIA encountered an error: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "MaIA", "version": "1.0"}
