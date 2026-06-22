from project.memory.session_memory import SessionMemory
from project.core.observability import Logger
from project.agents.planner import Planner
from project.agents.worker import Worker
from project.agents.evaluator import Evaluator

class MainAgent:
    MAX_RETRIES = 2

    def __init__(self, session_id=None):
        self.session   = SessionMemory(session_id)
        self.logger    = Logger(self.session.session_id)
        self.planner   = Planner(self.session, self.logger)
        self.worker    = Worker(self.session, self.logger)
        self.evaluator = Evaluator(self.session, self.logger)

    def handle_message(self, user_input):
        self.logger.log_user_input(user_input)
        self.session.add_turn("user", user_input)
        task_plan_msg   = self.planner.plan(user_input)
        task_result_msg = self.worker.execute(task_plan_msg)
        retry, final_msg = 0, None
        while retry <= self.MAX_RETRIES:
            eval_msg = self.evaluator.evaluate(task_result_msg, retry)
            decision = eval_msg.payload.get("eval_decision", "PASS")
            if decision in ("PASS", "BLOCK"):
                final_msg = eval_msg
                break
            task_result_msg.payload["raw_response"] = eval_msg.payload.get("response", "")
            retry += 1
        if final_msg is None:
            final_msg = eval_msg
        response = final_msg.payload.get("response", "")
        self.logger.log_final_response(response)
        self.session.add_turn("assistant", response)
        return {
            "response":      response,
            "priority":      task_plan_msg.priority,
            "session_id":    self.session.session_id,
            "eval_decision": final_msg.payload.get("eval_decision", "PASS"),
            "trace":         self.logger.get_session_trace(),
        }

def run_agent(user_input: str) -> str:
    agent = MainAgent()
    result = agent.handle_message(user_input)
    return result["response"]
