import uuid

class SessionMemory:
    def __init__(self, session_id=None):
        self.session_id           = session_id or str(uuid.uuid4())[:8]
        self.language             = "en"
        self.location             = "unknown"
        self.symptom_history      = []
        self.priority_level       = "LOW"
        self.conversation_turns   = []
        self.last_tool_used       = ""
        self.conversation_summary = ""
        self.retry_count          = 0

    def add_turn(self, role, content):
        self.conversation_turns.append({"role": role, "content": content})

    def update_symptoms(self, keywords):
        for kw in keywords:
            if kw and kw not in self.symptom_history:
                self.symptom_history.append(kw)

    def to_context_dict(self):
        return {
            "session_id":            self.session_id,
            "language":              self.language,
            "location":              self.location,
            "symptom_history":       self.symptom_history,
            "priority_level":        self.priority_level,
            "conversation_summary":  self.conversation_summary,
        }

    def reset(self):
        self.__init__(self.session_id)
