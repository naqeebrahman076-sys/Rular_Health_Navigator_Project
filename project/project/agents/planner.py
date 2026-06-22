import json, os, re
from project.core.context_engineering import ContextEngineer, EMERGENCY_KEYWORDS
from project.core.a2a_protocol import A2AProtocol

try:
    import google.generativeai as genai
    _GENAI = True
except ImportError:
    _GENAI = False

class Planner:
    def __init__(self, session, logger):
        self.session = session
        self.logger  = logger
        self.ctx     = ContextEngineer()
        self._model  = None
        if _GENAI:
            key = os.getenv("GOOGLE_API_KEY", "")
            if key:
                genai.configure(api_key=key)
                self._model = genai.GenerativeModel("gemini-1.5-flash")

    def _llm_parse(self, prompt):
        if not self._model:
            return {}
        try:
            resp  = self._model.generate_content(prompt)
            match = re.search(r"\{.*\}", resp.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}

    def _rule_based_parse(self, query):
        ql = query.lower()
        if any(kw in ql for kw in EMERGENCY_KEYWORDS):
            return {"symptom_keywords": ["emergency"], "priority": "EMERGENCY",
                    "tasks": ["emergency_alert"], "language": self.session.language,
                    "location": self.session.location}
        symptom_words = ["fever","headache","cough","cold","pain","vomiting",
                         "diarrhea","rash","fatigue","nausea","dizziness",
                         "bleeding","swelling","breathless"]
        found    = [w for w in symptom_words if w in ql]
        priority = "MEDIUM" if found else "LOW"
        tasks    = ["symptom_lookup", "health_faq"]
        if self.session.location != "unknown":
            tasks.append("clinic_search")
        return {"symptom_keywords": found or ["general"], "priority": priority,
                "tasks": tasks, "language": self.session.language,
                "location": self.session.location}

    def plan(self, user_query):
        self.logger.start_timer("planner")
        lang                  = self.ctx.detect_language(user_query)
        self.session.language = lang
        prompt = self.ctx.build_planner_prompt(user_query, self.session.to_context_dict())
        parsed = self._llm_parse(prompt) or self._rule_based_parse(user_query)
        self.session.priority_level = parsed.get("priority", "LOW")
        self.session.update_symptoms(parsed.get("symptom_keywords", []))
        self.logger.log_planner_output(parsed)
        self.logger.end_timer("planner")
        return A2AProtocol.create_task_plan(
            session_id       = self.session.session_id,
            priority         = parsed.get("priority", "LOW"),
            symptom_keywords = parsed.get("symptom_keywords", []),
            location         = parsed.get("location", self.session.location),
            language         = lang,
            tasks            = parsed.get("tasks", ["health_faq"]),
            user_query       = user_query,
        )
