import os
import requests
from typing import List, Dict

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"

# ── Country → LinkedIn subdomain + Serper geo code ───────────────────────────
COUNTRY_MAP = {
    # LATAM
    "Argentina":            {"subdomain": "ar",  "gl": "ar"},
    "Brasil":               {"subdomain": "br",  "gl": "br"},
    "Chile":                {"subdomain": "cl",  "gl": "cl"},
    "Colombia":             {"subdomain": "co",  "gl": "co"},
    "México":               {"subdomain": "mx",  "gl": "mx"},
    "Perú":                 {"subdomain": "pe",  "gl": "pe"},
    "Uruguay":              {"subdomain": "uy",  "gl": "uy"},
    "Paraguay":             {"subdomain": "www", "gl": "py"},
    "Bolivia":              {"subdomain": "www", "gl": "bo"},
    "Ecuador":              {"subdomain": "ec",  "gl": "ec"},
    "Venezuela":            {"subdomain": "www", "gl": "ve"},
    "Guatemala":            {"subdomain": "www", "gl": "gt"},
    "Costa Rica":           {"subdomain": "www", "gl": "cr"},
    "Panamá":               {"subdomain": "www", "gl": "pa"},
    "República Dominicana": {"subdomain": "www", "gl": "do"},
    "Cuba":                 {"subdomain": "www", "gl": "cu"},
    "Puerto Rico":          {"subdomain": "www", "gl": "pr"},
    # North America
    "United States":        {"subdomain": "www", "gl": "us"},
    "Canada":               {"subdomain": "ca",  "gl": "ca"},
    # Europe
    "España":               {"subdomain": "es",  "gl": "es"},
    "United Kingdom":       {"subdomain": "uk",  "gl": "gb"},
    "Germany":              {"subdomain": "de",  "gl": "de"},
    "France":               {"subdomain": "fr",  "gl": "fr"},
    "Italy":                {"subdomain": "it",  "gl": "it"},
    "Netherlands":          {"subdomain": "nl",  "gl": "nl"},
    "Belgium":              {"subdomain": "be",  "gl": "be"},
    "Switzerland":          {"subdomain": "ch",  "gl": "ch"},
    "Sweden":               {"subdomain": "se",  "gl": "se"},
    "Norway":               {"subdomain": "no",  "gl": "no"},
    "Denmark":              {"subdomain": "dk",  "gl": "dk"},
    "Finland":              {"subdomain": "fi",  "gl": "fi"},
    "Poland":               {"subdomain": "pl",  "gl": "pl"},
    "Portugal":             {"subdomain": "pt",  "gl": "pt"},
    "Austria":              {"subdomain": "at",  "gl": "at"},
    "Ireland":              {"subdomain": "ie",  "gl": "ie"},
    "Czech Republic":       {"subdomain": "cz",  "gl": "cz"},
    "Romania":              {"subdomain": "ro",  "gl": "ro"},
    "Hungary":              {"subdomain": "hu",  "gl": "hu"},
    "Greece":               {"subdomain": "gr",  "gl": "gr"},
    "Ukraine":              {"subdomain": "ua",  "gl": "ua"},
    "Russia":               {"subdomain": "ru",  "gl": "ru"},
    "Turkey":               {"subdomain": "tr",  "gl": "tr"},
    # Asia Pacific
    "Australia":            {"subdomain": "au",  "gl": "au"},
    "New Zealand":          {"subdomain": "nz",  "gl": "nz"},
    "India":                {"subdomain": "in",  "gl": "in"},
    "China":                {"subdomain": "cn",  "gl": "cn"},
    "Japan":                {"subdomain": "jp",  "gl": "jp"},
    "South Korea":          {"subdomain": "kr",  "gl": "kr"},
    "Singapore":            {"subdomain": "sg",  "gl": "sg"},
    "Malaysia":             {"subdomain": "my",  "gl": "my"},
    "Indonesia":            {"subdomain": "id",  "gl": "id"},
    "Philippines":          {"subdomain": "ph",  "gl": "ph"},
    "Thailand":             {"subdomain": "th",  "gl": "th"},
    "Vietnam":              {"subdomain": "vn",  "gl": "vn"},
    "Hong Kong":            {"subdomain": "hk",  "gl": "hk"},
    "Taiwan":               {"subdomain": "tw",  "gl": "tw"},
    "Pakistan":             {"subdomain": "pk",  "gl": "pk"},
    "Bangladesh":           {"subdomain": "bd",  "gl": "bd"},
    # Middle East & Africa
    "United Arab Emirates": {"subdomain": "ae",  "gl": "ae"},
    "Saudi Arabia":         {"subdomain": "sa",  "gl": "sa"},
    "Israel":               {"subdomain": "il",  "gl": "il"},
    "Egypt":                {"subdomain": "eg",  "gl": "eg"},
    "South Africa":         {"subdomain": "za",  "gl": "za"},
    "Nigeria":              {"subdomain": "ng",  "gl": "ng"},
    "Kenya":                {"subdomain": "ke",  "gl": "ke"},
    "Morocco":              {"subdomain": "ma",  "gl": "ma"},
    "Qatar":                {"subdomain": "qa",  "gl": "qa"},
    "Kuwait":               {"subdomain": "kw",  "gl": "kw"},
    "Jordan":               {"subdomain": "jo",  "gl": "jo"},
}

# ── Industry → native search terms ───────────────────────────────────────────
INDUSTRY_TERMS = {
    "Manufacturing":        "manufactura industria planta producción",
    "Retail":               "retail comercio minorista tiendas",
    "Fintech":              "fintech tecnología financiera pagos",
    "Financial Services":   "servicios financieros banca finanzas",
    "Healthcare":           "salud healthcare farmacéutica clínica",
    "Technology":           "tecnología software IT sistemas",
    "Agro":                 "agro agropecuario campo agricultura",
    "Real Estate":          "real estate inmobiliaria propiedades",
    "Education":            "educación universidad capacitación",
    "Professional Services":"consultoría servicios profesionales",
    "Logistics":            "logística supply chain cadena suministro",
    "Consumer Goods":       "consumo masivo FMCG alimentos bebidas",
}


def get_country_config(location: str) -> dict:
    return COUNTRY_MAP.get(location, {"subdomain": "www", "gl": "us"})


def build_site_operator(subdomain: str) -> str:
    if subdomain == "www":
        return "site:linkedin.com/in"
    return f"site:{subdomain}.linkedin.com/in"


def is_valid_country_url(url: str, subdomain: str) -> bool:
    if subdomain == "www":
        return "linkedin.com/in/" in url
    return f"{subdomain}.linkedin.com/in/" in url


def build_linkedin_queries(params: dict, subdomain: str) -> List[str]:
    role = params.get("role", "").strip()
    industry = params.get("industry", "").strip()
    location = params.get("location", "Argentina").strip()
    company_size = params.get("company_size", "").strip()
    keywords = params.get("keywords", "").strip()

    site = build_site_operator(subdomain)
    industry_terms = INDUSTRY_TERMS.get(industry, industry)

    queries = []

    # Primary: strict role + location + industry terms
    parts = [site]
    if role:
        parts.append(f'"{role}"')
    parts.append(location)
    if industry_terms:
        parts.append(industry_terms)
    if keywords:
        parts.append(keywords)
    queries.append(" ".join(filter(None, parts)))

    # Secondary: broader variation + company size
    if role or industry_terms:
        parts2 = [site, role, industry_terms, location]
        if company_size:
            parts2.append(company_size)
        queries.append(" ".join(filter(None, parts2)))

    # Tertiary: keywords-first for long-tail hits
    if keywords and (role or industry_terms):
        parts3 = [site, keywords, role, location]
        queries.append(" ".join(filter(None, parts3)))

    return queries


def search_linkedin_profiles(params: dict, max_results: int = 15) -> List[Dict]:
    location = params.get("location", "Argentina").strip()
    country_config = get_country_config(location)
    subdomain = country_config["subdomain"]
    gl = country_config["gl"]

    queries = build_linkedin_queries(params, subdomain)
    all_results = []
    seen_urls = set()

    for query in queries:
        if len(all_results) >= max_results:
            break

        payload = {"q": query, "num": 10, "gl": gl, "hl": "es"}
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

        try:
            response = requests.post(SERPER_URL, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[Searcher] Query failed: {query} — {e}")
            continue

        for result in data.get("organic", []):
            url = result.get("link", "")
            if "linkedin.com/in/" not in url:
                continue
            if not is_valid_country_url(url, subdomain):
                print(f"[Searcher] Skipping off-country profile: {url}")
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
