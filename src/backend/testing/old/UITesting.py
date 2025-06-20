import gradio as gr
import requests
import json

# --- Configuration ---
BACKEND_URL = "http://localhost:5000"


# --- API Client Functions (with Robust Error Handling) ---
def make_api_request(method, endpoint, payload=None, timeout=60):
    """A centralized function to handle all API requests and error parsing."""
    try:
        if method.upper() == 'GET':
            response = requests.get(endpoint, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(endpoint, json=payload, timeout=timeout)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"error": "Received non-JSON success response from backend.",
                        "status_code": response.status_code, "content": response.text[:500]}

        try:
            return response.json()
        except json.JSONDecodeError:
            return {
                "error": "Backend returned a non-JSON error.",
                "status_code": response.status_code,
                "details": response.text[:500]
            }

    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}


def create_user(wallet, name, country):
    return make_api_request("POST", f"{BACKEND_URL}/users",
                            {"wallet_address": wallet, "name": name, "country": country})


def get_user(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}")


def generate_path(topic, wallet):
    return make_api_request("POST", f"{BACKEND_URL}/paths/generate", {"topic": topic, "creator_wallet": wallet},
                            timeout=300)


def get_all_paths():
    return make_api_request("GET", f"{BACKEND_URL}/paths")


def get_level_content(path_id, level_num):
    if not path_id or level_num is None: return {"error": "Path ID and Level Number are required."}
    return make_api_request("GET", f"{BACKEND_URL}/paths/{path_id}/levels/{level_num}")


def start_progress(wallet, path_id):
    if not wallet or not path_id: return {"error": "Wallet and Path ID are required."}
    return make_api_request("POST", f"{BACKEND_URL}/progress/start", {"user_wallet": wallet, "path_id": path_id})


def update_progress(progress_id, item_id, answer_idx):
    return make_api_request("POST", f"{BACKEND_URL}/progress/update",
                            {"progress_id": progress_id, "content_item_id": item_id, "user_answer_index": answer_idx})


def get_scores(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/scores/{wallet}")


def mint_nft(path_id, wallet):
    return make_api_request("POST", f"{BACKEND_URL}/paths/{path_id}/complete", {"user_wallet": wallet}, timeout=180)


# --- Interactive Learner Logic (with better error checking) ---
def start_interactive_session(wallet, path_id):
    """Starts a session and fetches the first level's content, with data validation."""
    progress_data = start_progress(wallet, path_id)
    if "error" in progress_data:
        return progress_data, None, f"## Error Starting Session\n\nCould not start progress. Details:\n\n```json\n{json.dumps(progress_data, indent=2)}\n```", gr.update(
            visible=False), gr.update(visible=False)

    level_content_response = get_level_content(path_id, 1)
    if "error" in level_content_response:
        return progress_data, None, f"## Error Fetching Content\n\nCould not fetch content for Level 1. Details:\n\n```json\n{json.dumps(level_content_response, indent=2)}\n```", gr.update(
            visible=False), gr.update(visible=False)

    items = level_content_response.get('items')
    if not items or not isinstance(items, list) or len(items) == 0:
        error_msg = "## Data Structure Error\n\nThe AI-generated content for this level is invalid. The 'items' array is missing, not a list, or empty."
        return progress_data, None, error_msg, gr.update(visible=False), gr.update(visible=False)

    first_item = items[0]
    # FIX: Check for 'item_type' instead of 'type'
    if 'item_type' not in first_item or 'content' not in first_item:
        error_msg = f"## Data Structure Error\n\nThe first item in the lesson is malformed. It's missing an 'item_type' or 'content' key.\n\nReceived item:\n```json\n{json.dumps(first_item, indent=2)}\n```"
        return progress_data, None, error_msg, gr.update(visible=False), gr.update(visible=False)

    session_state = {"progress_data": progress_data, "level_content": items, "current_item_index": 0}

    # FIX: Use 'item_type' to check the item's kind
    if first_item['item_type'] == 'slide':
        return progress_data, session_state, first_item['content'], gr.update(visible=True), gr.update(visible=False)
    elif first_item['item_type'] == 'quiz':
        quiz_content = first_item['content']
        return progress_data, session_state, f"### {quiz_content['question']}", gr.update(visible=False), gr.update(
            visible=True, choices=quiz_content['options'], value=None)
    else:
        error_msg = f"## Data Structure Error\n\nUnknown item type: '{first_item['item_type']}'"  # <--- FIX
        return progress_data, None, error_msg, gr.update(visible=False), gr.update(visible=False)


def process_next_step(session_state, selected_answer=None):
    if not session_state:
        return session_state, "Start a session first.", gr.update(visible=False), gr.update(visible=False), ""

    current_item_index = session_state['current_item_index']
    current_item = session_state['level_content'][current_item_index]

    # FIX: Use 'item_type'
    if current_item['item_type'] == 'quiz' and selected_answer is not None:
        quiz_options = current_item['content']['options']
        answer_index = quiz_options.index(selected_answer)
        update_progress(session_state['progress_data']['id'], current_item['id'], answer_index)
        explanation = current_item['content']['explanation']
        session_state['current_item_index'] += 1
        return session_state, explanation, gr.update(visible=True), gr.update(visible=False), ""

    # FIX: Use 'item_type'
    if current_item['item_type'] == 'slide':
        session_state['current_item_index'] += 1

    if session_state['current_item_index'] >= len(session_state['level_content']):
        return session_state, "🎉 Level Complete! 🎉", gr.update(visible=False), gr.update(visible=False), ""

    next_item = session_state['level_content'][session_state['current_item_index']]
    # FIX: Use 'item_type'
    if next_item['item_type'] == 'slide':
        return session_state, next_item['content'], gr.update(visible=True), gr.update(visible=False), ""
    else:
        quiz_content = next_item['content']
        return session_state, f"### {quiz_content['question']}", gr.update(visible=False), gr.update(visible=True,
                                                                                                     choices=
                                                                                                     quiz_content[
                                                                                                         'options'],
                                                                                                     value=None), ""


# --- Gradio UI Definition (Unchanged) ---
with gr.Blocks(theme=gr.themes.Soft(), title="Noodl Backend Tester") as demo:
    gr.Markdown("# 🍜 Noodl Backend Tester (Full Suite)")

    with gr.Tabs():
        with gr.TabItem("🎓 Interactive Learner"):
            gr.Markdown("### Simulate a user going through a learning path.")
            session_state = gr.State(None)
            with gr.Row():
                learner_wallet_input = gr.Textbox(label="Learner's Wallet Address", placeholder="0x...")
                learner_path_id_input = gr.Number(label="Path ID to Learn", precision=0)
            start_session_btn = gr.Button("🚀 Start Learning Session", variant="primary")
            gr.Markdown("---")
            content_display = gr.Markdown(label="Lesson Content")
            with gr.Row():
                next_slide_btn = gr.Button("➡️ Next", visible=True)
                quiz_choices = gr.Radio(label="Quiz Answer", visible=False)
            session_progress_output = gr.JSON(label="Session Progress Record")
            start_session_btn.click(fn=start_interactive_session, inputs=[learner_wallet_input, learner_path_id_input],
                                    outputs=[session_progress_output, session_state, content_display, next_slide_btn,
                                             quiz_choices])
            next_slide_btn.click(fn=process_next_step, inputs=[session_state],
                                 outputs=[session_state, content_display, next_slide_btn, quiz_choices,
                                          gr.Textbox(value="", visible=False)])
            quiz_choices.change(fn=process_next_step, inputs=[session_state, quiz_choices],
                                outputs=[session_state, content_display, next_slide_btn, quiz_choices,
                                         gr.Textbox(value="", visible=False)])

        with gr.TabItem("👤 Users"):
            gr.Markdown("Create and manage users.")
            with gr.Row():
                user_wallet_input = gr.Textbox(label="User Wallet Address")
                user_name_input = gr.Textbox(label="Name")
                user_country_input = gr.Textbox(label="Country")
            create_user_btn = gr.Button("Create/Update User")
            get_user_btn = gr.Button("Get User by Wallet")
            user_output = gr.JSON()
            create_user_btn.click(create_user, [user_wallet_input, user_name_input, user_country_input], user_output)
            get_user_btn.click(get_user, [user_wallet_input], user_output)

        with gr.TabItem("📚 Paths & Content"):
            gr.Markdown("Generate new paths and view content.")
            with gr.Accordion("Generate New Path", open=False):
                gen_topic_input = gr.Textbox(label="Learning Topic")
                gen_wallet_input = gr.Textbox(label="Creator's Wallet Address")
                generate_btn = gr.Button("✨ Generate Path")
                generate_output = gr.JSON()
                generate_btn.click(generate_path, [gen_topic_input, gen_wallet_input], generate_output)
            with gr.Accordion("View Content", open=True):
                refresh_paths_btn = gr.Button("🔄 Refresh Path List")
                path_list_output = gr.JSON(label="Available Paths")
                refresh_paths_btn.click(get_all_paths, [], path_list_output)
                with gr.Row():
                    view_path_id_input = gr.Number(label="Path ID", precision=0)
                    view_level_num_input = gr.Number(label="Level Number", precision=0)
                get_content_btn = gr.Button("📚 Get Level Content")
                level_content_output = gr.JSON(label="Level Content (Interleaved)")
                get_content_btn.click(get_level_content, [view_path_id_input, view_level_num_input],
                                      level_content_output)

        with gr.TabItem("🏃‍♂️ Progress & Scoring"):
            gr.Markdown("Track user progress and view scores.")
            with gr.Row():
                prog_wallet_input = gr.Textbox(label="User Wallet")
                prog_path_id_input = gr.Number(label="Path ID", precision=0)
            start_prog_btn = gr.Button("Start/Get Progress")
            progress_output = gr.JSON(label="Progress Record")
            start_prog_btn.click(start_progress, [prog_wallet_input, prog_path_id_input], progress_output)
            with gr.Accordion("Log a Quiz Attempt", open=False):
                log_prog_id_input = gr.Number(label="Progress ID (from above)", precision=0)
                log_item_id_input = gr.Number(label="Content Item ID (of the quiz)", precision=0)
                log_answer_idx_input = gr.Number(label="User's Answer Index (0-3)", precision=0)
                log_attempt_btn = gr.Button("Log Attempt")
                log_output = gr.JSON()
                log_attempt_btn.click(update_progress, [log_prog_id_input, log_item_id_input, log_answer_idx_input],
                                      log_output)
            with gr.Accordion("Fetch User Scores", open=False):
                score_wallet_input = gr.Textbox(label="User Wallet to Fetch Scores For")
                get_scores_btn = gr.Button("Get Scores")
                scores_output = gr.JSON()
                get_scores_btn.click(get_scores, [score_wallet_input], scores_output)

        with gr.TabItem("🏆 Mint NFT"):
            gr.Markdown("Mint an NFT certificate for completing a path.")
            with gr.Row():
                mint_path_id_input = gr.Number(label="Completed Path ID", precision=0)
                mint_wallet_input = gr.Textbox(label="User's Wallet to Receive NFT")
            mint_btn = gr.Button("🏆 Mint NFT")
            mint_output = gr.JSON(label="Minting Result")
            mint_btn.click(mint_nft, [mint_path_id_input, mint_wallet_input], mint_output)

# --- Launch the Gradio UI ---
print("Gradio UI is ready. Visit http://localhost:7000 to access it.")
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7000, share=False)