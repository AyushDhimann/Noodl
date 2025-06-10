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
.gr-group {
    border-radius: 15px !important;
    border: 1px solid #ddd;
    padding: 15px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
"""


# --- API Client Functions ---
def make_api_request(method, endpoint, params=None, payload=None, timeout=60):
    try:
        response = requests.request(method, endpoint, params=params, json=payload, timeout=timeout)
        response.raise_for_status()
        if response.status_code == 204:
            return {"status": "success", "message": "Request successful with no content."}
        return response.json()
    except requests.exceptions.HTTPError as e:
        try:
            return e.response.json()
        except json.JSONDecodeError:
            return {"error": "Backend returned a non-JSON error.", "status_code": e.response.status_code,
                    "details": e.response.text[:500]}
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}


# --- Specific Client Functions for UI ---
def create_user(wallet, name, country):
    return make_api_request("POST", f"{BACKEND_URL}/users",
                            payload={"wallet_address": wallet, "name": name, "country": country})


def get_user(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}")


def get_user_created_paths(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}/paths")


def get_user_created_paths_count(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/users/{wallet}/paths/count")


def generate_path_with_progress(topic, wallet):
    start_res = make_api_request("POST", f"{BACKEND_URL}/paths/generate", payload={"topic": topic, "creator_wallet": wallet})
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


def get_generation_status(task_id):
    return make_api_request("GET", f"{BACKEND_URL}/paths/generate/status/{task_id}")


def get_all_paths():
    return make_api_request("GET", f"{BACKEND_URL}/paths")


def get_full_path(path_id):
    return make_api_request("GET", f"{BACKEND_URL}/paths/{path_id}")


def delete_path(path_id, wallet):
    return make_api_request("DELETE", f"{BACKEND_URL}/paths/{path_id}", payload={"user_wallet": wallet})


def get_level_content(path_id, level_num):
    return make_api_request("GET", f"{BACKEND_URL}/paths/{path_id}/levels/{level_num}")


def start_progress(wallet, path_id):
    return make_api_request("POST", f"{BACKEND_URL}/progress/start", payload={"user_wallet": wallet, "path_id": path_id})


def update_location(progress_id, item_index):
    return make_api_request("POST", f"{BACKEND_URL}/progress/location",
                            payload={"progress_id": progress_id, "item_index": item_index})


def update_progress(progress_id, item_id, answer_idx):
    return make_api_request("POST", f"{BACKEND_URL}/progress/update",
                            payload={"progress_id": progress_id, "content_item_id": item_id, "user_answer_index": answer_idx})


def get_scores(wallet):
    return make_api_request("GET", f"{BACKEND_URL}/scores/{wallet}")


def mint_nft(path_id, wallet):
    return make_api_request("POST", f"{BACKEND_URL}/paths/{path_id}/complete", payload={"user_wallet": wallet}, timeout=180)


def get_nft_metadata(path_id):
    return make_api_request("GET", f"{BACKEND_URL}/nft/metadata/{path_id}")


def get_nft_image_html(path_id):
    if not path_id:
        return "Please provide a Path ID."
    return f'<img src="{BACKEND_URL}/nft/image/{path_id}" alt="NFT Image for Path {path_id}" style="width: 300px; height: 300px; border-radius: 10px;"/>'


def search_paths(query):
    return make_api_request("GET", f"{BACKEND_URL}/search", params={"q": query})


# --- Gradio UI Definition ---
def create_and_launch_ui():
    with gr.Blocks(theme=gr.themes.Glass(), css=custom_css, title="Noodl Backend Super-Tester") as demo:
        gr.Markdown("# 🍜 Noodl Backend Super-Tester", elem_id="main-title")

        # --- Define all components first ---

        # Inputs
        with gr.Group():
            gr.Markdown("### ⚙️ Global Inputs")
            with gr.Row():
                wallet_input = gr.Textbox(label="Wallet Address", placeholder="0x...")
                name_input = gr.Textbox(label="User Name", placeholder="Alice")
                country_input = gr.Textbox(label="Country", placeholder="USA")
            with gr.Row():
                topic_input = gr.Textbox(label="Topic for Generation", placeholder="e.g., The History of Rome")
                task_id_input = gr.Textbox(label="Task ID (from generation)", placeholder="UUID...")
            with gr.Row():
                path_id_input = gr.Number(label="Path ID", precision=0)
                level_num_input = gr.Number(label="Level Number", precision=0)
            with gr.Row():
                progress_id_input = gr.Number(label="Progress ID", precision=0)
                content_item_id_input = gr.Number(label="Content Item ID", precision=0)
                answer_index_input = gr.Number(label="Answer Index (0-3)", precision=0)
                item_index_input = gr.Number(label="Item Index (for location)", precision=0)
            with gr.Row():
                search_query_input = gr.Textbox(label="Search Query", placeholder="Enter 2+ characters to search...")

        # Outputs (defined before they are used in click events)
        with gr.Group():
            gr.Markdown("### 📝 API Response / Image Output")
            generation_output = gr.Markdown(label="Generation Log")
            api_output = gr.JSON(label="JSON Response")
            image_output = gr.HTML(label="NFT Image")

        # --- Define the layout and connect events ---
        with gr.Group():
            gr.Markdown("### 🧪 Endpoint Testers")
            with gr.Accordion("🔍 Search Endpoint", open=True):
                with gr.Row():
                    gr.Button("GET /search").click(search_paths, [search_query_input], api_output)

            with gr.Accordion("👤 User Endpoints", open=False):
                with gr.Row():
                    gr.Button("POST /users").click(create_user, [wallet_input, name_input, country_input], api_output)
                    gr.Button("GET /users/<wallet>").click(get_user, [wallet_input], api_output)
                    gr.Button("GET /users/<wallet>/paths").click(get_user_created_paths, [wallet_input], api_output)
                    gr.Button("GET /users/<wallet>/paths/count").click(get_user_created_paths_count, [wallet_input],
                                                                       api_output)

            with gr.Accordion("🛠️ Path Generation Endpoints", open=False):
                with gr.Row():
                    gr.Button("POST /paths/generate", variant="primary").click(generate_path_with_progress,
                                                                               [topic_input, wallet_input],
                                                                               generation_output)
                    gr.Button("GET /paths/generate/status/<task_id>").click(get_generation_status, [task_id_input],
                                                                            api_output)

            with gr.Accordion("📖 Path & Content Endpoints", open=False):
                with gr.Row():
                    gr.Button("GET /paths").click(get_all_paths, [], api_output)
                    gr.Button("GET /paths/<path_id>").click(get_full_path, [path_id_input], api_output)
                    gr.Button("GET /paths/<path_id>/levels/<level_num>").click(get_level_content,
                                                                               [path_id_input, level_num_input],
                                                                               api_output)
                    gr.Button("DELETE /paths/<path_id>", variant="secondary").click(delete_path,
                                                                                    [path_id_input, wallet_input],
                                                                                    api_output)

            with gr.Accordion("🏃‍♂️ Progress & Scoring Endpoints", open=False):
                with gr.Row():
                    gr.Button("POST /progress/start").click(start_progress, [wallet_input, path_id_input], api_output)
                    gr.Button("POST /progress/location").click(update_location, [progress_id_input, item_index_input],
                                                               api_output)
                    gr.Button("POST /progress/update").click(update_progress, [progress_id_input, content_item_id_input,
                                                                               answer_index_input], api_output)
                    gr.Button("GET /scores/<wallet>").click(get_scores, [wallet_input], api_output)

            with gr.Accordion("🏆 NFT Endpoints", open=False):
                with gr.Row():
                    gr.Button("POST /paths/<path_id>/complete").click(mint_nft, [path_id_input, wallet_input],
                                                                      api_output)
                    gr.Button("GET /nft/metadata/<path_id>").click(get_nft_metadata, [path_id_input], api_output)
                    gr.Button("GET /nft/image/<path_id>").click(get_nft_image_html, [path_id_input], image_output)

    demo.launch(server_name="0.0.0.0", server_port=7000, share=True)