import requests, re, time

def _safe_get(url, params=None, timeout=8):
    try:
        r = requests.get(url, params=params, timeout=timeout,
                         headers={"User-Agent": "RuralHealthNavigator/1.0"})
        return r.json() if r.ok else {}
    except Exception:
        return {}

def web_search(query):
    data = _safe_get("https://api.duckduckgo.com/",
                     {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"})
    abstract = data.get("AbstractText", "")
    if abstract:
        return abstract[:600]
    topics   = data.get("RelatedTopics", [])
    snippets = [t.get("Text", "") for t in topics[:3] if isinstance(t, dict)]
    result   = " ".join(snippets)
    return result[:600] if result else "No information found."

def clinic_finder(location, query="hospital clinic"):
    if not location or location == "unknown":
        return "Location not provided. Please share your city or district."
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": f"{query} near {location}",
                                 "format": "json", "limit": 3, "addressdetails": 1},
                         headers={"User-Agent": "RuralHealthNavigator/1.0"}, timeout=8)
        results = r.json() if r.ok else []
    except Exception:
        results = []
    if not results:
        return f"No clinics found near {location}. Try Google Maps."
    lines = []
    for i, p in enumerate(results[:3], 1):
        name    = p.get("display_name", "Unknown").split(",")[0]
        address = ", ".join(p.get("display_name", "").split(",")[:3])
        lines.append(f"{i}. {name} - {address}")
    return "Nearby facilities:\n" + "\n".join(lines)

def translator(text, target_lang="hi", source_lang="en"):
    if target_lang == source_lang or target_lang == "en":
        return text
    data = _safe_get("https://api.mymemory.translated.net/get",
                     {"q": text[:500], "langpair": f"{source_lang}|{target_lang}"})
    return data.get("responseData", {}).get("translatedText", "") or text

def summarizer(text, max_sentences=3):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if len(s) > 20]
    return " ".join(sentences[:max_sentences]) if sentences else text[:300]

def emergency_detector(text):
    KEYS = ["chest pain","difficulty breathing","unconscious","not breathing",
            "heart attack","stroke","severe bleeding","poisoning","overdose",
            "seizure","choking","cannot wake"]
    tl        = text.lower()
    triggered = [k for k in KEYS if k in tl]
    return {"is_emergency": bool(triggered), "triggered_keywords": triggered,
            "message": "EMERGENCY: Call 112 immediately!" if triggered else ""}

HEALTH_FAQ = {
    "fever":      "Fever is often caused by infections. Rest and stay hydrated. Consult a doctor if fever exceeds 39.4C or lasts more than 3 days.",
    "headache":   "Headaches can result from stress or dehydration. Rest in a quiet room and drink water. See a doctor if severe or with vision changes.",
    "cough":      "Coughs are commonly caused by colds or allergies. Drink warm fluids and rest. See a doctor if cough persists over 2 weeks.",
    "diarrhea":   "Drink ORS to prevent dehydration. Avoid fatty foods. See a doctor if it lasts more than 2 days.",
    "vomiting":   "Sip clear fluids slowly. Seek care if you cannot keep fluids down for 24 hours.",
    "chest pain": "Chest pain can be serious. Call emergency services immediately if sudden and severe.",
    "rash":       "Rashes can be caused by allergies or infections. Avoid scratching. See a doctor if spreading or with fever.",
    "dizziness":  "Dizziness may result from dehydration or low blood pressure. Sit or lie down and drink water. See a doctor if persistent.",
    "default":    "For any health concern, please consult a qualified medical professional. Do not self-diagnose.",
}

def health_faq_lookup(symptom_keywords):
    results = []
    for kw in symptom_keywords:
        kl = kw.lower()
        for key, val in HEALTH_FAQ.items():
            if key in kl or kl in key:
                results.append(f"[{key.title()}]: {val}")
                break
    if not results:
        results.append(HEALTH_FAQ["default"])
    return "\n\n".join(results)
