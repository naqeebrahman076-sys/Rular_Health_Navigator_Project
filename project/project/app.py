import sys, os, json
sys.path.insert(0, "/content")
import gradio as gr
from project.main_agent import MainAgent

PRIORITY_COLORS = {"LOW":"Green","MEDIUM":"Yellow","HIGH":"Orange","EMERGENCY":"Red"}

def chat(user_message, history, session_id):
    if not user_message.strip():
        return history, history, session_id, "", ""
    agent = MainAgent(session_id if session_id else None)
    for h in history:
        agent.session.add_turn("user",      h[0])
        agent.session.add_turn("assistant", h[1])
    result   = agent.handle_message(user_message)
    response = result["response"]
    priority = result["priority"]
    trace    = result["trace"]
    sid      = result["session_id"]
    history.append((user_message, response))
    label = f"{PRIORITY_COLORS.get(priority,'')} ({priority})"
    return history, history, sid, label, json.dumps(trace, indent=2)

with gr.Blocks(title="Rural Health Navigator") as demo:
    gr.Markdown("# Rural Health Navigator Agent\n> Not a diagnostic tool. Always consult a doctor.")
    with gr.Row():
        with gr.Column(scale=3):
            chatbot   = gr.Chatbot(label="Health Assistant", height=450)
            msg_input = gr.Textbox(label="Your health query", lines=2,
                                   placeholder="Describe your symptoms...")
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")
        with gr.Column(scale=2):
            priority_box = gr.Textbox(label="Priority Level", interactive=False)
            trace_box    = gr.Textbox(label="Agent Trace", interactive=False, lines=20)
    state_history    = gr.State([])
    state_session_id = gr.State("")
    send_btn.click(fn=chat,
                   inputs=[msg_input, state_history, state_session_id],
                   outputs=[chatbot, state_history, state_session_id, priority_box, trace_box]
                   ).then(lambda: "", None, msg_input)
    msg_input.submit(fn=chat,
                     inputs=[msg_input, state_history, state_session_id],
                     outputs=[chatbot, state_history, state_session_id, priority_box, trace_box]
                     ).then(lambda: "", None, msg_input)
    clear_btn.click(lambda: ([], [], "", "", ""),
                    outputs=[chatbot, state_history, state_session_id, priority_box, trace_box])
    gr.Markdown("**Try:** `I have fever` | `Clinic in Patna` | `Chest pain` | Hindi text")

if __name__ == "__main__":
    demo.launch(share=True)
