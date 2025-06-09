import gradio as gr
import requests
import json
import time

# --- Configuration ---
BACKEND_URL = "http://localhost:5000"

# --- Custom CSS for a more aesthetic UI ---
custom_css = """
body {
    background-color: #f0f2f5;
    background-image: linear-gradient(to top right, #f0f2f5, #e6e9f0);
}
.gradio-container {
    border-radius: 20px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
#main-title {
    text-align: center;
    font-size: 2.5em;
    color: #2c3e50;
    font-weight: 600;
    margin-bottom: 20px;
}
.gr-button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.gr-button-primary {
    background: linear-gradient(to right, #4a90e2, #50e3c2) !important;
    border: none !important;
}
.gr-button-secondary {
    background: linear-gradient(to right, #f093fb, #f5576c) !important;
    border: none !important;
    color: white !important;
}
.gr-tabs button {
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 20px !important;
}
.gr-accordion {
    border-radius: 10px !important;
    border: 1px solid #ddd;
}
"""


# --- API Client Functions ---
def make_api_request(method, endpoint, payload=None, timeout=60):
    try:
        response = requests.request(method, endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            return e.response.json()
        except json.JSONDecodeError:
            return {"error": "Backend returned a non-JSON error.", "status_code": e.response.status_code,
                    "details": e.response.text[:500]}
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}


def create_user(wallet, name, country):
    return make_api_request("POST", f"{BACKEND_URL}/users",
                            {"wallet_address": wallet, "name": name, "country": country})


def get_user(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}")


def get_user_created_paths(wallet):
    if not wallet: return {"error": "Wallet address is required."}
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}/paths")


def get_user_created_paths_count(wallet):
    if not wallet: return {"error": "Wallet address is required."}
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}/paths/count")


def get_all_paths():
    return make_api_request("GET", f"{BACKEND_URL}/paths")


def get_full_path(path_id):
    if not path_id: return {"error": "Path ID is required."}
    return make_api_request("GET", f"{BACKEND_URL}/paths/{path_id}")


def delete_path(path_id, wallet):
    if not path_id or not wallet: return {"error": "Path ID and Wallet are required."}
    return make_api_request("DELETE", f"{BACKEND_URL}/paths/{path_id}", payload={"user_wallet": wallet})


def start_progress(wallet, path_id):
    if not wallet or not path_id: return {"error": "Wallet and Path ID are required."}
    return make_api_request("POST", f"{BACKEND_URL}/progress/start", {"user_wallet": wallet, "path_id": path_id})


def update_progress(progress_id, item_id, answer_idx):
    return make_api_request("POST", f"{BACKEND_URL}/progress/update",
                            {"progress_id": progress_id, "content_item_id": item_id, "user_answer_index": answer_idx})


def update_location(progress_id, item_index):
    print(f"UI: Updating location for progress_id {progress_id} to item_index {item_index}")
    make_api_request("POST", f"{BACKEND_URL}/progress/location",
                     {"progress_id": progress_id, "item_index": item_index})


def get_scores(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/scores/{wallet}")


def mint_nft(path_id, wallet):
    return make_api_request("POST", f"{BACKEND_URL}/paths/{path_id}/complete", {"user_wallet": wallet}, timeout=180)


def generate_path_with_progress(topic, wallet):
    start_res = make_api_request("POST", f"{BACKEND_URL}/paths/generate", {"topic": topic, "creator_wallet": wallet})
    if "error" in start_res:
        error_msg = f"### ❌ Error Starting Task\n\n**Reason:** {start_res['error']}"
        if 'similar_path' in start_res:
            similar = start_res['similar_path']
            error_msg += f"\n\n**Similar Path Found:**\n- **ID:** {similar['id']}\n- **Title:** {similar['title']}"
        yield error_msg
        return

    task_id = start_res['task_id']
    log = [f"### 🚀 Generation Started\n\nTask ID: `{task_id}`\n\n---"]
    yield "\n".join(log)

    last_log_count = 0
    while True:
        time.sleep(2)
        status_res = make_api_request("GET", f"{BACKEND_URL}/paths/generate/status/{task_id}")
        if "error" in status_res:
            log.append(f"**Error fetching status:** {json.dumps(status_res, indent=2)}")
            yield "\n".join(log)
            break

        progress_data = status_res.get('progress', [])
        if len(progress_data) > last_log_count:
            new_logs = progress_data[last_log_count:]
            for item in new_logs:
                log.append(f"- {item['status']}")
                if 'data' in item and item.get('data') and 'explorer_url' in item.get('data', {}):
                    url = item['data']['explorer_url']
                    if url:
                        log.append(f"\n\n[🔗 View Transaction on Block Explorer]({url})")

            last_log_count = len(progress_data)
            yield "\n".join(log)

        if any("SUCCESS" in item['status'] or "ERROR" in item['status'] for item in progress_data):
            break


# --- Interactive Learner Logic ---
def start_interactive_session(wallet, path_id):
    progress_data = start_progress(wallet, path_id)
    if "error" in progress_data:
        return progress_data, None, f"## Error Starting Session\n\nDetails:\n\n```json\n{json.dumps(progress_data, indent=2)}\n```", gr.update(
            visible=False), gr.update(visible=False)

    update_location(progress_data['id'], 0)

    level_content_response = get_full_path(path_id)
    if "error" in level_content_response:
        return progress_data, None, f"## Error Fetching Content\n\nDetails:\n\n```json\n{json.dumps(level_content_response, indent=2)}\n```", gr.update(
            visible=False), gr.update(visible=False)

    items = level_content_response.get('levels', [])[0].get('content_items', [])
    if not items or not isinstance(items, list) or len(items) == 0:
        return progress_data, None, "## Data Error\n\n'items' array is missing or empty.", gr.update(
            visible=False), gr.update(visible=False)

    first_item = items[0]
    session_state = {"progress_data": progress_data, "level_content": items, "current_item_index": 0}

    if first_item['item_type'] == 'slide':
        return progress_data, session_state, first_item['content'], gr.update(visible=True), gr.update(visible=False)
    else:
        quiz_content = first_item['content']
        return progress_data, session_state, f"### {quiz_content['question']}", gr.update(visible=False), gr.update(
            visible=True, choices=quiz_content['options'], value=None)


def process_next_step(session_state, selected_answer=None):
    if not session_state:
        return session_state, "Start a session first.", gr.update(visible=False), gr.update(visible=False), ""

    current_item_index_before = session_state['current_item_index']
    current_item = session_state['level_content'][current_item_index_before]
    explanation_text = ""

    if current_item['item_type'] == 'quiz' and selected_answer is not None:
        quiz_options = current_item['content']['options']
        answer_index = quiz_options.index(selected_answer)
        update_progress(session_state['progress_data']['id'], current_item['id'], answer_index)
        explanation_text = current_item['content']['explanation']
        session_state['current_item_index'] += 1
    elif current_item['item_type'] == 'slide':
        session_state['current_item_index'] += 1

    if session_state['current_item_index'] > current_item_index_before:
        update_location(session_state['progress_data']['id'], session_state['current_item_index'])

    if session_state['current_item_index'] >= len(session_state['level_content']):
        final_message = "## 🎉 Level Complete! 🎉"
        if explanation_text:
            final_message = f"{explanation_text}\n\n---\n\n{final_message}"
        return session_state, final_message, gr.update(visible=False), gr.update(visible=False), ""

    next_item = session_state['level_content'][session_state['current_item_index']]
    display_content = ""
    if next_item['item_type'] == 'slide':
        display_content = next_item['content']
        if explanation_text:
            display_content = f"{explanation_text}\n\n---\n\n{display_content}"
        return session_state, display_content, gr.update(visible=True), gr.update(visible=False), ""
    else:
        quiz_content = next_item['content']
        display_content = f"### {quiz_content['question']}"
        if explanation_text:
            display_content = f"{explanation_text}\n\n---\n\n{display_content}"
        return session_state, display_content, gr.update(visible=False), gr.update(visible=True,
                                                                                   choices=quiz_content['options'],
                                                                                   value=None), ""


# --- Gradio UI Definition ---
def create_and_launch_ui():
    with gr.Blocks(theme=gr.themes.Glass(), css=custom_css, title="Noodl Backend Tester") as demo:
        gr.Markdown("# 🍜 Noodl Backend Tester", elem_id="main-title")
        with gr.Tabs():
            with gr.TabItem("🛠️ Generate"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 1. Define Your Path")
                        gen_topic_input = gr.Textbox(label="Learning Topic", placeholder="e.g., Quantum Computing")
                        gen_wallet_input = gr.Textbox(label="Creator's Wallet Address", placeholder="0x...")
                        generate_btn = gr.Button("✨ Generate Path & Watch Progress", variant="primary")
                    with gr.Column(scale=2):
                        gr.Markdown("### 2. Watch the Magic Happen")
                        progress_log = gr.Markdown(label="Live Generation Log")
                generate_btn.click(generate_path_with_progress, [gen_topic_input, gen_wallet_input], progress_log)

            with gr.TabItem("🎓 Learn"):
                session_state = gr.State(None)
                gr.Markdown("### Simulate a User's Learning Experience")
                with gr.Row():
                    learner_wallet_input = gr.Textbox(label="Learner's Wallet Address", placeholder="0x...")
                    learner_path_id_input = gr.Number(label="Path ID to Learn", precision=0)
                start_session_btn = gr.Button("🚀 Start Learning Session", variant="primary")
                gr.Markdown("---")
                with gr.Row():
                    with gr.Column(scale=2):
                        content_display = gr.Markdown(label="Lesson Content")
                        with gr.Group():
                            next_slide_btn = gr.Button("➡️ Next", visible=True)
                            quiz_choices = gr.Radio(label="Quiz Answer", visible=False)
                    with gr.Column(scale=1):
                        session_progress_output = gr.JSON(label="Session Progress Record")

                start_session_btn.click(fn=start_interactive_session,
                                        inputs=[learner_wallet_input, learner_path_id_input],
                                        outputs=[session_progress_output, session_state, content_display,
                                                 next_slide_btn, quiz_choices])
                next_slide_btn.click(fn=process_next_step, inputs=[session_state],
                                     outputs=[session_state, content_display, next_slide_btn, quiz_choices,
                                              gr.Textbox(value="", visible=False)])
                quiz_choices.change(fn=process_next_step, inputs=[session_state, quiz_choices],
                                    outputs=[session_state, content_display, next_slide_btn, quiz_choices,
                                             gr.Textbox(value="", visible=False)])

            with gr.TabItem("🗂️ Data & Users"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### User Management")
                        user_wallet_input = gr.Textbox(label="User Wallet Address", placeholder="0x...")
                        user_name_input = gr.Textbox(label="Name", placeholder="Alice")
                        user_country_input = gr.Textbox(label="Country", placeholder="USA")
                        with gr.Row():
                            create_user_btn = gr.Button("👤 Create / Update")
                            get_user_btn = gr.Button("🔍 Get User")
                        user_output = gr.JSON(label="User Info / Path Count")
                        create_user_btn.click(create_user, [user_wallet_input, user_name_input, user_country_input],
                                              user_output)
                        get_user_btn.click(get_user, [user_wallet_input], user_output)

                    with gr.Column():
                        gr.Markdown("### Path Information")
                        path_wallet_input = gr.Textbox(label="Creator Wallet Address", placeholder="0x...")
                        with gr.Row():
                            get_created_paths_btn = gr.Button("📚 Get Created Paths")
                            get_created_paths_count_btn = gr.Button("🔢 Get Path Count")
                        created_paths_output = gr.JSON(label="User-Created Paths")
                        get_created_paths_btn.click(get_user_created_paths, [path_wallet_input], created_paths_output)
                        get_created_paths_count_btn.click(get_user_created_paths_count, [path_wallet_input],
                                                          user_output)

                with gr.Accordion("View Full Path Details", open=False):
                    gr.Markdown("### 📖 Get a path and all its content")
                    full_path_id_input = gr.Number(label="Path ID", precision=0)
                    get_full_path_btn = gr.Button("🔍 Fetch Full Path")
                    full_path_output = gr.JSON(label="Full Path Details")
                    get_full_path_btn.click(get_full_path, [full_path_id_input], full_path_output)

                with gr.Accordion("Path Deletion (Danger Zone)", open=False):
                    gr.Markdown("### 🗑️ Delete a Learning Path")
                    delete_path_id_input = gr.Number(label="Path ID to Delete", precision=0)
                    delete_wallet_input = gr.Textbox(label="Creator's Wallet (for verification)", placeholder="0x...")
                    delete_btn = gr.Button("🔥 Delete Path", variant="secondary")
                    delete_output = gr.JSON(label="Deletion Result")
                    delete_btn.click(delete_path, [delete_path_id_input, delete_wallet_input], delete_output)

            with gr.TabItem("🏆 Mint NFT"):
                gr.Markdown("### Mint an NFT Certificate")
                with gr.Row():
                    with gr.Column():
                        mint_path_id_input = gr.Number(label="Completed Path ID", precision=0)
                        mint_wallet_input = gr.Textbox(label="User's Wallet to Receive NFT", placeholder="0x...")
                        mint_btn = gr.Button("🏆 Mint NFT", variant="primary")
                    with gr.Column():
                        mint_output = gr.JSON(label="Minting Result")
                mint_btn.click(mint_nft, [mint_path_id_input, mint_wallet_input], mint_output)

    demo.launch(server_name="0.0.0.0", server_port=7000, share=True)