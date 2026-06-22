import json, time, os, uuid
from datetime import datetime, timezone

LOG_DIR  = "project/logs"
LOG_FILE = os.path.join(LOG_DIR, "session_log.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)

class Logger:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self._timers = {}

    def _write(self, entry):
        entry["session_id"] = self.session_id
        entry["timestamp"]  = datetime.now(timezone.utc).isoformat()
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_user_input(self, raw_input):
        self._write({"event": "user_input", "raw_input": raw_input})

    def log_planner_output(self, task_plan):
        self._write({"event": "planner_output", "task_plan": task_plan})

    def log_tool_call(self, tool_name, tool_input, tool_output, latency_ms):
        self._write({"event": "tool_call", "tool_name": tool_name,
                     "tool_input": str(tool_input)[:200],
                     "tool_output": str(tool_output)[:300],
                     "latency_ms": round(latency_ms, 2)})

    def log_worker_output(self, raw_response, tools_used):
        self._write({"event": "worker_output",
                     "raw_response": raw_response[:300],
                     "tools_used": tools_used})

    def log_eval_decision(self, decision, reason, retry_count=0):
        self._write({"event": "evaluator_decision", "decision": decision,
                     "reason": reason, "retry_count": retry_count})

    def log_final_response(self, response):
        self._write({"event": "final_response", "response_preview": response[:300]})

    def log_error(self, agent, error):
        self._write({"event": "error", "agent": agent, "error": error})

    def start_timer(self, label):
        self._timers[label] = time.time()

    def end_timer(self, label):
        elapsed = (time.time() - self._timers.get(label, time.time())) * 1000
        self._write({"event": "timing", "label": label, "elapsed_ms": round(elapsed, 2)})
        return elapsed

    def get_session_trace(self):
        if not os.path.exists(LOG_FILE):
            return []
        entries = []
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("session_id") == self.session_id:
                        entries.append(e)
                except Exception:
                    pass
        return entries
