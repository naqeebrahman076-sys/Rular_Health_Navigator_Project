import time, os
from project.core.context_engineering import ContextEngineer
from project.core.a2a_protocol import A2AProtocol
from project.tools.tools import (web_search, clinic_finder, translator,
                                  summarizer, health_faq_lookup, emergency_detector)

try:
    import google.generativeai as genai
    _GENAI = True
except ImportError:
    _GENAI = False

EMERGENCY_RESPONSE = (
    "EMERGENCY ALERT\n\n"
    "The symptoms you described may be life-threatening.\n"
    "Please call emergency services (112) immediately.\n"
    "Do not wait - get to the nearest hospital right away.\n\n"
    "If someone is with you, ask them to help now."
)

class Worker:
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

    def _run_tools(self, task_plan):
        tasks      = task_plan.get("tasks", [])
        keywords   = task_plan.get("symptom_keywords", [])
        location   = task_plan.get("location", "unknown")
        results    = {}
        tools_used = []

        if "emergency_alert" in tasks:
            results["emergency"] = EMERGENCY_RESPONSE
            tools_used.append("emergency_detector")

        if "symptom_lookup" in tasks and keywords:
            t0  = time.time()
            res = summarizer(web_search(" ".join(keywords[:2]) + " symptoms treatment"))
            self.logger.log_tool_call("web_search", keywords, res, (time.time()-t0)*1000)
            results["symptom_info"] = res
            tools_used.append("web_search")

        if "health_faq" in tasks:
            t0  = time.time()
            res = health_faq_lookup(keywords)
            self.logger.log_tool_call("health_faq", keywords, res, (time.time()-t0)*1000)
            results["health_faq"] = res
            tools_used.append("health_faq_lookup")

        if "clinic_search" in tasks:
            t0  = time.time()
            res = clinic_finder(location)
            self.logger.log_tool_call("clinic_finder", location, res, (time.time()-t0)*1000)
            results["nearby_clinics"] = res
            tools_used.append("clinic_finder")

        self.session.last_tool_used = ", ".join(tools_used)
        return results, tools_used

    def _generate_response(self, task_plan, tool_results):
        if "emergency" in tool_results:
            return tool_results["emergency"]
        prompt = self.ctx.build_worker_prompt(task_plan, tool_results)
        if self._model:
            try:
                return self._model.generate_content(prompt).text
            except Exception:
                pass
        parts = []
        if tool_results.get("health_faq"):
            parts.append(tool_results["health_faq"])
        if tool_results.get("symptom_info"):
            parts.append("Additional info: " + tool_results["symptom_info"])
        if tool_results.get("nearby_clinics"):
            parts.append(tool_results["nearby_clinics"])
        parts.append("\nPlease consult a qualified doctor for proper diagnosis and treatment.")
        return "\n\n".join(parts)

    def execute(self, task_plan_msg):
        self.logger.start_timer("worker")
        plan          = task_plan_msg.payload
        priority      = task_plan_msg.priority
        tool_results, tools_used = self._run_tools(plan)
        raw_response  = self._generate_response(plan, tool_results)
        lang = plan.get("language", "en")
        if lang != "en" and "emergency" not in tool_results:
            t0           = time.time()
            raw_response = translator(raw_response, target_lang=lang)
            self.logger.log_tool_call("translator", lang, raw_response[:100], (time.time()-t0)*1000)
            tools_used.append("translator")
        self.logger.log_worker_output(raw_response, tools_used)
        self.logger.end_timer("worker")
        return A2AProtocol.create_task_result(
            session_id   = task_plan_msg.session_id,
            priority     = priority,
            raw_response = raw_response,
            tools_used   = tools_used,
            language     = lang,
        )
