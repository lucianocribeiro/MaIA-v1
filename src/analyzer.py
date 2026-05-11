import os
import json
import anthropic
from typing import Dict, List

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are MaIA, the business development agent of Agencia Kairos — an Argentine consulting firm 
founded by Luciano Ribeiro and Santiago Konstantinovsky.

WHAT KAIROS DOES:
Kairos combines specialized consulting, AI adoption, technology implementation, change management, 
and training to help mid-to-large companies transform their operations with real impact.
Kairos works at the intersection of HR, Finance, Administration, and Artificial Intelligence.

KAIROS SERVICE LINES:
1. Consultoría Especializada: Process diagnosis, AI adoption strategy, and transformation roadmaps 
   for HR, Finance, and Administration areas.
2. Tecnología: Implementation of AI automations, AI agents, and custom software solutions 
   tailored to the company's operational context.
3. Gestión del Cambio: Organizational culture, internal communication, and change adoption 
   programs to ensure AI implementation is sustainable and people-centered.
4. Capacitaciones y Workshops: AI training programs and workshops for teams and leaders, 
   adapted to each organization's digital maturity level.

WHO IS A GOOD KAIROS LEAD:
- Decision-makers with authority over HR, Finance, Operations, or Technology budgets
- Leaders in companies undergoing digital transformation, system implementation, or process redesign
- People dealing with manual processes, disconnected systems, or lack of AI adoption strategy
- Directors, C-level executives, or senior managers in mid-to-large companies
- Companies in Argentina or LATAM (primary market) or globally (secondary market)

WHO IS NOT A KAIROS LEAD — DISQUALIFY THESE:
- People who work at AI consulting firms, automation agencies, or tech consultancies
- Founders or employees of companies that build AI agents, AI tools, or automation software
- Software developers, ML engineers, or AI researchers (they build what Kairos sells)
- Independent AI consultants or freelance automation specialists
- Vendors of HR software, ERP systems, or similar tech products (they compete or overlap)
- People whose entire profile is about AI implementation — they do what Kairos does

SCORING CRITERIA:
- Score 8-10: Clear decision-making authority + active transformation signals + no disqualifiers
- Score 6-7: Good role fit + plausible pain points + some uncertainty on context
- Score 4-5: Relevant industry or role but limited signals or indirect fit
- Score 1-3: Wrong profile, wrong industry, or disqualified (AI vendor/consultant/builder)

You respond ONLY with a valid JSON object. No preamble, no explanation, no markdown fences.
"""


def analyze_profile(profile: Dict, search_params: Dict) -> Dict:
    """Analyze a single LinkedIn profile and return structured assessment."""
    user_message = f"""Analyze this LinkedIn profile as a potential Agencia Kairos client:

Name / Title from Google: {profile.get('title', '')}
LinkedIn URL: {profile.get('url', '')}
Profile Snippet: {profile.get('snippet', '')}

Search context:
- Target industry: {search_params.get('industry') or 'Not specified'}
- Target role: {search_params.get('role') or 'Not specified'}
- Target location: {search_params.get('location') or 'Argentina'}
- Target service: {search_params.get('target_service') or 'Not specified'}
- Additional keywords: {search_params.get('keywords') or 'None'}

IMPORTANT: If this person works in AI consulting, builds AI tools, sells automation software, 
or does what Kairos does, assign a score of 1-3 and flag them as disqualified.

Return this exact JSON structure:
{{
  "name": "full name extracted from title",
  "role": "their current role or title",
  "company": "their company if identifiable, otherwise empty string",
  "fit_score": <integer 1 to 10>,
  "disqualified": <true or false>,
  "disqualify_reason": "if disqualified, brief reason. Otherwise empty string.",
  "why_this_lead": "2-3 sentences on why this person is a relevant Kairos prospect. Be specific. If disqualified, explain why they are not a fit.",
  "recommended_service": "one of: Consultoría Especializada, Tecnología, Gestión del Cambio, Capacitaciones y Workshops",
  "conversation_angle": "2-3 sentences on the pain point or opportunity to lead with in the outreach",
  "linkedin_message_warm": "A warm, conversational LinkedIn connection message. 4-5 lines. Opens by acknowledging something specific about their role or context. Builds rapport before mentioning Kairos. Ends with a low-friction question or invitation. Written in the same language as the profile (Spanish for LATAM, English for others). Sign off as Luciano from Agencia Kairos.",
  "linkedin_message_direct": "A short, direct LinkedIn connection message. 2-3 lines maximum. Opens with a specific value proposition relevant to their role. No fluff. Clear reason for reaching out. Written in the same language as the profile. Sign off as Luciano from Agencia Kairos."
}}"""

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
