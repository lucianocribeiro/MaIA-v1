import os
import json
import anthropic
from typing import Dict, List

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are MaIA, a strategic business development agent for Agencia Kairos — an Argentine consulting firm specializing in HR Technology, AI implementation, process design, and business transformation.

Your role is to evaluate LinkedIn profiles and determine whether each person is a strong potential client for Kairos. You assess:
- Decision-making authority: CHROs, HR Directors, COOs, CEOs, People & Culture leads, Ops Directors
- Industry fit: companies going through growth, digital transformation, or talent strategy shifts
- Signals of AI, HR tech, or process transformation needs
- Location and market fit: Argentina and LATAM

You respond ONLY with a valid JSON object. No preamble, no explanation, no markdown fences. Pure JSON."""


def analyze_profile(profile: Dict, search_params: Dict) -> Dict:
    """Analyze a single LinkedIn profile and return structured assessment."""
    language = "Spanish" if search_params.get("language") == "es" else "English"

    user_message = f"""Analyze this LinkedIn profile as a potential Kairos client:

Name / Title from Google: {profile.get('title', '')}
LinkedIn URL: {profile.get('url', '')}
Profile Snippet: {profile.get('snippet', '')}

Search context used to find this person:
- Target industry: {search_params.get('industry') or 'Not specified'}
- Target role: {search_params.get('role') or 'Not specified'}
- Target location: {search_params.get('location') or 'Argentina'}
- Additional keywords: {search_params.get('keywords') or 'None'}
- Output language for all text fields: {language}

Return this exact JSON structure (no extra fields, no markdown):
{{
  "name": "full name extracted from title, or best guess",
  "role": "their current role or title",
  "company": "their company name if identifiable, otherwise empty string",
  "fit_score": <integer from 1 to 10>,
  "why_this_lead": "2 to 3 sentences explaining why this person is a relevant Kairos prospect. Be specific and grounded in what you see.",
  "conversation_angle": "2 to 3 sentences on how to open the LinkedIn message — what pain point, transformation challenge, or opportunity to lead with.",
  "recommended_service": "one of: AI Implementation, HR Technology, Process Design, Automation, Business Transformation"
}}

Language rule:
- Write "name", "role", "company", "why_this_lead", and "conversation_angle" in {language}.
- Keep "recommended_service" in English using exactly one of the allowed values above."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    # Strip accidental markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    analysis = json.loads(raw)
    analysis["linkedin_url"] = profile.get("url", "")
    analysis["raw_snippet"] = profile.get("snippet", "")

    return analysis


def analyze_profiles(profiles: List[Dict], search_params: Dict) -> List[Dict]:
    """
    Analyze all profiles in sequence.
    Returns results sorted by fit_score descending.
    Failed profiles are skipped silently.
    """
    results = []

    for profile in profiles:
        try:
            analysis = analyze_profile(profile, search_params)
            results.append(analysis)
        except json.JSONDecodeError as e:
            print(f"[Analyzer] JSON parse error for {profile.get('url', '')}: {e}")
        except Exception as e:
            print(f"[Analyzer] Failed for {profile.get('url', '')}: {e}")

    results.sort(key=lambda x: x.get("fit_score", 0), reverse=True)
    return results
