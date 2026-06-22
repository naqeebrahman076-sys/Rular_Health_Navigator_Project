import json, os, re
from project.core.context_engineering import ContextEngineer, DIAGNOSTIC_PHRASES
from project.core.a2a_protocol import A2AProtocol

try:
    import google.generativeai as genai
    _GENAI = True
except ImportError:
    _GENAI = False

SAFE_FALLBACK = (
    "I am unable to provide specific guidance for this query. "
    "Please consult a qualified doctor or visit your nearest health centre. "
    "If this is an emergency, call 112 immediately."
)
PROFESSIONAL_REFERRAL = "\n\nPlease consult a qualified medical professional for proper diagnosis and treatment."
EMERGENCY_REFERRAL    = "\n\nIf this is an emergency, call 112 immediately."

class Evaluator:
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

    def _rule_based_eval(self, response, priority):
        rl = response.lower()
        for phrase in DIAGNOSTIC_PHRASES:
            if phrase in rl:
                fixed = re.sub(re.escape(phrase), "may be related to ",
                               response, flags=re.IGNORECASE)
                return {"decision": "REVISE",
                        "reason": f"Diagnostic phrase detected: {phrase!r}",
                        "revised_response": fixed + PROFESSIONAL_REFERRAL}
        has_ref = any(kw in rl for kw in ["consult","doctor","physician","professional","clinic"])
        if not has_ref:
            return {"decision": "REVISE", "reason": "Missing professional referral.",
                    "revised_response": response + PROFESSIONAL_REFERRAL}
        if priority == "EMERGENCY" and "112" not in response and "emergency" not in rl:
            return {"decision": "REVISE",
                    "reason": "EMERGENCY missing emergency services reference.",
                    "revised_response": response + EMERGENCY_REFERRAL}
        return {"decision": "PASS", "reason": "Response is safe.",
                "revised_response": response}

    def _llm_eval(self, response, priority):
        if not self._model:
            return {}
        try:
            resp  = self._model.generate_content(self.ctx.build_evaluator_prompt(response, priority))
            match = re.search(r"\{.*\}", resp.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}

    def evaluate(self, task_result_msg, retry_count=0):
        self.logger.start_timer("evaluator")
        payload  = task_result_msg.payload
        response = payload.get("raw_response", "")
        priority = task_result_msg.priority
        result   = self._llm_eval(response, priority) or self._rule_based_eval(response, priority)
        decision         = result.get("decision", "PASS")
        reason           = result.get("reason", "")
        revised_response = result.get("revised_response", response)
        if decision == "BLOCK":
            revised_response = SAFE_FALLBACK
        self.logger.log_eval_decision(decision, reason, retry_count)
        self.logger.end_timer("evaluator")
        return A2AProtocol.create_final_response(
            session_id    = task_result_msg.session_id,
            response      = revised_response,
            priority      = priority,
            eval_decision = decision,
        )
