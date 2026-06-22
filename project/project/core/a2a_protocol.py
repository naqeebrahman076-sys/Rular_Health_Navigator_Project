from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Literal
from datetime import datetime, timezone
import json

@dataclass
class A2AMessage:
    sender:       str
    receiver:     str
    message_type: str
    payload:      Dict[str, Any]
    priority:     str = "LOW"
    session_id:   str = ""
    status:       str = "pending"
    timestamp:    str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count:  int = 0

    def to_dict(self): return asdict(self)

class A2AProtocol:
    @staticmethod
    def create_task_plan(session_id, priority, symptom_keywords,
                         location, language, tasks, user_query):
        return A2AMessage(
            sender="planner", receiver="worker",
            message_type="task_plan", priority=priority,
            session_id=session_id, status="pending",
            payload={"user_query": user_query,
                     "symptom_keywords": symptom_keywords,
                     "location": location,
                     "language": language,
                     "tasks": tasks})

    @staticmethod
    def create_task_result(session_id, priority, raw_response, tools_used, language):
        return A2AMessage(
            sender="worker", receiver="evaluator",
            message_type="task_result", priority=priority,
            session_id=session_id, status="in_progress",
            payload={"raw_response": raw_response,
                     "tools_used": tools_used,
                     "language": language})

    @staticmethod
    def create_final_response(session_id, response, priority, eval_decision):
        return A2AMessage(
            sender="evaluator", receiver="user",
            message_type="final_response", priority=priority,
            session_id=session_id, status="completed",
            payload={"response": response, "eval_decision": eval_decision})
