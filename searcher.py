import os
import requests
from typing import List, Dict

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"


def build_linkedin_queries(params: dict) -> List[str]:
    """Build targeted LinkedIn profile queries from search params."""
    role = params.get("role", "").strip()
    industry = params.get("industry", "").strip()
    location = params.get("location", "Argentina").strip()
    company_size = params.get("company_size", "").strip()
    keywords = params.get("keywords", "").strip()

    queries = []

    # --- Primary query: strict role + location ---
    parts = ["site:linkedin.com/in"]
    if role:
        parts.append(f'"{role}"')
    if location:
        parts.append(location)
    if industry:
        parts.append(industry)
    if keywords:
        parts.append(keywords)
    queries.append(" ".join(parts))

    # --- Secondary query: variation without quotes for broader reach ---
    if role or industry:
        parts2 = ["site:linkedin.com/in", role, industry, location]
        if company_size:
            parts2.append(company_size)
        queries.append(" ".join(filter(None, parts2)))

    # --- Tertiary query: keywords-first for long-tail hits ---
    if keywords and (role or industry):
        parts3 = ["site:linkedin.com/in", keywords, role, location]
        queries.append(" ".join(filter(None, parts3)))

    return queries


def search_linkedin_profiles(params: dict, max_results: int = 15) -> List[Dict]:
    """
    Search LinkedIn profiles via Serper (Google site: operator).
    Returns up to max_results deduplicated profiles.
    """
    queries = build_linkedin_queries(params)
    all_results = []
    seen_urls = set()

    for query in queries:
        if len(all_results) >= max_results:
            break

        payload = {
            "q": query,
            "num": 10,
            "gl": "ar",   # geo: Argentina
            "hl": "es"    # language: Spanish
        }

        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(SERPER_URL, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[Searcher] Query failed: {query} — {e}")
            continue

        organic = data.get("organic", [])
        for result in organic:
            url = result.get("link", "")
            # Only accept actual profile pages (not company pages or other sections)
            if "linkedin.com/in/" not in url:
                continue
            if url in seen_urls:
                continue

            seen_urls.add(url)
            all_results.append({
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("snippet", ""),
            })

            if len(all_results) >= max_results:
                break

    return all_results[:max_results]
