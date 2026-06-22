# 🩺 Rural Health Navigator Agent

> **Kaggle Capstone Project — Agents for Good Track**  
> A multi-agent AI system providing safe health guidance to rural and underserved communities.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)
![Gemini](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Track](https://img.shields.io/badge/Kaggle-Agents%20for%20Good-red)

---

## 🌍 Problem Statement

Millions of people in rural India and similar regions face critical barriers
to basic healthcare:

- No nearby doctors or clinics
- Health resources available only in English
- Low health literacy — not knowing when symptoms are serious

This project bridges that gap using a conversational AI agent that is
**safe, non-diagnostic, and accessible.**

---

## 💡 Solution Overview

A user describes their symptoms in plain language (or Hindi).
The multi-agent system responds with safe health guidance,
nearby clinic information, and professional referrals —
all safety-checked before reaching the user.

---

## 🤖 Multi-Agent Architecture
### Agents

| Agent | Responsibility |
|---|---|
| **Planner** | Parses query, assigns priority (LOW / MEDIUM / HIGH / EMERGENCY), creates task plan |
| **Worker** | Runs tools — health FAQ, web search, clinic finder, translator |
| **Evaluator** | Blocks diagnostic language, ensures doctor referral, flags emergencies |

---

## ✨ Key Features

- 🚨 **Emergency Detection** — detects chest pain, difficulty breathing etc. and prompts 112
- 🌐 **Hindi Language Support** — auto-detects Hindi and responds in Hindi
- 🏥 **Clinic Finder** — finds nearby hospitals using OpenStreetMap
- 🛡️ **Safety Guardrails** — Evaluator blocks all diagnostic statements
- 📋 **Agent Trace Panel** — live log of every agent decision in the UI
- ⚡ **Works without API Key** — rule-based fallbacks require no Gemini key

---

## 🗂️ Project Structure
---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rural-health-navigator.git
cd rural-health-navigator
```

### 2. Install Dependencies
```bash
pip install -r project/requirements.txt
```

### 3. Set API Key (Optional)
```bash
export GOOGLE_API_KEY="your_gemini_api_key_here"
# Leave blank to use rule-based fallback mode
```

### 4. Run the App
```bash
python project/app.py
```

### 5. Or Run on Google Colab
Open `Rural_Health_Navigator_Agent_v2.ipynb` in Google Colab
and click **Runtime → Run All**.

---

## 🧪 Test Scenarios

| Input | Priority | Response |
|---|---|---|
| "Hello, how do I stay healthy?" | LOW | General wellness advice |
| "I have fever and headache, I am in Patna" | MEDIUM | FAQ + nearby clinics |
| "Vomiting and diarrhea since last night" | HIGH | ORS advice + doctor referral |
| "Chest pain and difficulty breathing!" | EMERGENCY | Call 112 immediately |
| "मुझे बुखार है" (Hindi) | MEDIUM | Response in Hindi |

---

## 🛠️ Tools Used

| Tool | Purpose | Source |
|---|---|---|
| `web_search` | Symptom information lookup | DuckDuckGo API |
| `clinic_finder` | Nearby hospitals/clinics | OpenStreetMap Nominatim |
| `translator` | Hindi/regional language support | MyMemory API |
| `health_faq_lookup` | Curated health FAQ responses | Built-in knowledge base |
| `emergency_detector` | Life-threatening keyword detection | Rule-based |
| `summarizer` | Condense long medical articles | Extractive summarization |

---

## 🧩 A2A Protocol

Agents communicate using a structured message schema:

```python
A2AMessage(
    sender       = "planner",
    receiver     = "worker",
    message_type = "task_plan",
    priority     = "MEDIUM",
    payload      = { "tasks": [...], "symptom_keywords": [...] }
)
```

Flow: `Planner → Worker → Evaluator → User`  
On REVISE: `Evaluator → Worker (retry, max 2 times)`

---

## 🚀 Deployment

### Hugging Face Spaces
1. Create a new Gradio Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Upload the `project/` folder
3. Set `app.py` as the entry point
4. Add `GOOGLE_API_KEY` as a Space secret (optional)

### Google Colab
Upload `Rural_Health_Navigator_Agent_v2.ipynb` and run all cells.

---

## ⚠️ Disclaimer

This system is **not a medical diagnostic tool**.
It provides general health information only.
All responses include a recommendation to consult a qualified doctor.
Emergency cases are immediately directed to call **112**.

---

## 🏆 Kaggle Capstone — Agents for Good

| Criteria | Implementation |
|---|---|
| Social Impact | Serves rural populations with no healthcare access |
| Multi-Agent System | True Planner → Worker → Evaluator pipeline |
| Safety | Evaluator blocks all diagnostic language |
| Accessibility | Hindi support, simple language, no API key required |
| Deployable | Gradio app on Hugging Face Spaces |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Acknowledgements

- [Google Gemini API](https://ai.google.dev/) for LLM capabilities
- [Gradio](https://gradio.app/) for the chat interface
- [OpenStreetMap Nominatim](https://nominatim.org/) for clinic search
- [DuckDuckGo API](https://duckduckgo.com/) for web search
- [MyMemory](https://mymemory.translated.net/) for translation
- WHO public health guidelines for FAQ content
- 
