EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "unconscious", "not breathing",
    "heart attack", "stroke", "severe bleeding", "poisoning", "overdose",
    "seizure", "choking", "cannot wake",
]

DIAGNOSTIC_PHRASES = [
    "you have ", "you are diagnosed", "this is definitely",
    "diagnosis is", "you suffer from", "it is confirmed",
]

class ContextEngineer:
    MAX_TURNS = 6

    def build_planner_prompt(self, user_query, session_context):
        lang    = session_context.get("language", "en")
        loc     = session_context.get("location", "unknown")
        summary = session_context.get("conversation_summary", "")
        return (
            "You are the Planner agent of a Rural Health Navigator.\n"
            "Parse the user health query and return ONLY valid JSON.\n\n"
            f"Session: language={lang}, location={loc}\n"
            f"Summary: {summary}\n\n"
            f"Emergency keywords (use priority=EMERGENCY if found): {EMERGENCY_KEYWORDS}\n\n"
            "Examples:\n"
            'User: I have fever\nPlan: {"symptom_keywords":["fever"],"priority":"MEDIUM","tasks":["symptom_lookup","health_faq"],"language":"en","location":"unknown"}\n\n'
            "Return JSON only:\n"
            '{"symptom_keywords":[...],"priority":"LOW|MEDIUM|HIGH|EMERGENCY",'
            '"tasks":["symptom_lookup","clinic_search","health_faq","emergency_alert"],'
            f'"language":"{lang}","location":"{loc}"}}\n\n'
            f"User query: {user_query}"
        )

    def build_worker_prompt(self, task_plan, tool_results):
        results_text = "\n".join(f"[{k}]: {v}" for k, v in tool_results.items())
        lang = task_plan.get("language", "en")
        return (
            "You are the Worker agent of a Rural Health Navigator.\n"
            "Write a helpful, compassionate health guidance response.\n\n"
            "STRICT RULES:\n"
            "1. Never diagnose. Use phrases like may be related to.\n"
            "2. Always recommend consulting a qualified doctor.\n"
            "3. If priority=EMERGENCY include: Call emergency services 112 immediately.\n"
            f"4. Respond in language: {lang}. Keep under 200 words.\n\n"
            f"Task plan: {task_plan}\n\n"
            f"Tool results:\n{results_text}\n\n"
            "Response:"
        )

    def build_evaluator_prompt(self, raw_response, priority):
        return (
            "You are the Evaluator agent. Check the response for safety.\n"
            "Respond ONLY with valid JSON.\n\n"
            f"Diagnostic phrases to reject: {DIAGNOSTIC_PHRASES}\n"
            f"Priority: {priority}\n\n"
            "PASS = safe and non-diagnostic\n"
            "REVISE = has diagnostic language (fix it)\n"
            "BLOCK = harmful or completely wrong\n\n"
            f"Response to evaluate:\n{raw_response}\n\n"
            'Return: {"decision":"PASS|REVISE|BLOCK","reason":"...","revised_response":"..."}'
        )

    def compress_history(self, turns):
        if len(turns) <= self.MAX_TURNS:
            return turns, ""
        summary = "Earlier: " + " | ".join(
            f"{t['role']}: {str(t['content'])[:80]}" for t in turns[:-3]
        )
        return turns[-3:], summary

    @staticmethod
    def detect_language(text):
        hindi = set("\u0905\u0906\u0907\u0908\u0909\u090a\u090f\u0910\u0913\u0914\u0915\u0916\u0917\u0918\u091a\u091b\u091c\u091d\u091f\u0920\u0921\u0922\u0923\u0924\u0925\u0926\u0927\u0928\u092a\u092b\u092c\u092d\u092e\u092f\u0930\u0932\u0935\u0936\u0937\u0938\u0939")
        return "hi" if any(c in hindi for c in text) else "en"

    @staticmethod
    def is_emergency(text):
        tl = text.lower()
        return any(kw in tl for kw in EMERGENCY_KEYWORDS)
