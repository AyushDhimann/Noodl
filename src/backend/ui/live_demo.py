import gradio as gr
import requests
import json
import time

# --- Configuration ---
BACKEND_URL = "http://localhost:5000"


# --- API Client ---
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


# --- UI Helper & Callback Functions ---

def login_user(wallet, name, country):
    if not wallet:
        gr.Warning("Wallet address is required to log in.")
        return None, None, None, gr.Tabs(selected=0)

    user_data = make_api_request("POST", f"{BACKEND_URL}/users",
                                 payload={"wallet_address": wallet, "name": name, "country": country})
    if "error" in user_data:
        gr.Error(f"Login Failed: {user_data.get('error')}")
        return None, None, None, gr.Tabs(selected=0)

    gr.Info(f"Welcome, {name or wallet}!")
    return wallet, name, country, gr.Tabs(selected=1)


def refresh_dashboard(wallet):
    if not wallet:
        return [], []

    my_paths_data = make_api_request("GET", f"{BACKEND_URL}/users/{wallet}/paths")
    all_paths_data = make_api_request("GET", f"{BACKEND_URL}/paths")

    my_paths_formatted = [[p.get('id'), p.get('title'), p.get('total_levels')] for p in my_paths_data] if isinstance(
        my_paths_data, list) else []
    all_paths_formatted = [[p.get('id'), p.get('title'), p.get('total_levels')] for p in all_paths_data] if isinstance(
        all_paths_data, list) else []

    return my_paths_formatted, all_paths_formatted


def search_for_paths(query):
    if not query or len(query) < 2:
        return []
    results = make_api_request("GET", f"{BACKEND_URL}/search", params={"q": query}) or []

    return [[item.get('id'), item.get('title'), item.get('match_type')] for item in results] if isinstance(results,
                                                                                                           list) else []


def generate_path_live(topic, wallet):
    if not topic or not wallet:
        gr.Warning("Topic and wallet address are required.")
        yield "Please provide a topic and ensure you are logged in.", gr.Button(visible=False), gr.Button(visible=False)
        return

    start_res = make_api_request("POST", f"{BACKEND_URL}/paths/generate",
                                 payload={"topic": topic, "creator_wallet": wallet})
    if "error" in start_res:
        error_msg = f"### ❌ Error Starting Task\n\n**Reason:** {start_res['error']}"
        if 'similar_path' in start_res:
            similar = start_res['similar_path']
            error_msg += f"\n\n**Similar Path Found:**\n- **ID:** {similar['id']}\n- **Title:** {similar['title']}"
        yield error_msg, gr.Button(visible=False), gr.Button(visible=False)
        return

    task_id = start_res['task_id']
    log = [f"### 🚀 Generation Started\n\nTask ID: `{task_id}`\n\n---"]
    yield "\n".join(log), gr.Button(visible=False), gr.Button(visible=False)

    final_path_id = None
    tx_url = None
    last_log_count = 0

    while True:
        time.sleep(2)
        status_res = make_api_request("GET", f"{BACKEND_URL}/paths/generate/status/{task_id}")
        if "error" in status_res:
            log.append(f"**Error fetching status:** {json.dumps(status_res, indent=2)}")
            yield "\n".join(log), gr.Button(visible=False), gr.Button(visible=False)
            break

        progress_data = status_res.get('progress', [])

        if len(progress_data) > last_log_count:
            new_logs = progress_data[last_log_count:]
            for item in new_logs:
                log.append(f"- {item['status']}")

                if 'data' in item and item.get('data'):
                    if 'path_id' in item['data']:
                        final_path_id = item['data']['path_id']
                    if 'explorer_url' in item['data']:
                        tx_url = item['data']['explorer_url']
                        if tx_url:
                            log.append(f"\n\n[🔗 View Transaction on Block Explorer]({tx_url})")

            last_log_count = len(progress_data)
            yield "\n".join(log), gr.Button(visible=final_path_id is not None,
                                            value=f"Continue to Path {final_path_id}"), gr.Button(
                visible=tx_url is not None, link=tx_url)

        if any("SUCCESS" in item['status'] or "ERROR" in item['status'] for item in progress_data):
            break


def start_learning_path(path_id, user_wallet):
    if not path_id:
        gr.Warning("Please enter a Path ID to start learning.")
        return None, None, 0, 0, gr.Tabs(selected=1), None, gr.Button(visible=True), gr.Button(visible=True), gr.Button(visible=False), gr.Markdown(visible=False)


    try:
        path_id_int = int(path_id)
    except (ValueError, TypeError):
        gr.Warning(f"Invalid Path ID: '{path_id}'. Please enter a number.")
        return None, None, 0, 0, gr.Tabs(selected=1), None, gr.Button(visible=True), gr.Button(visible=True), gr.Button(visible=False), gr.Markdown(visible=False)


    path_data = make_api_request("GET", f"{BACKEND_URL}/paths/{path_id_int}")
    if "error" in path_data:
        gr.Error(f"Could not load path: {path_data['error']}")
        return None, None, 0, 0, gr.Tabs(selected=1), None, gr.Button(visible=True), gr.Button(visible=True), gr.Button(visible=False), gr.Markdown(visible=False)


    progress_res = make_api_request("POST", f"{BACKEND_URL}/progress/start",
                                    payload={"user_wallet": user_wallet, "path_id": path_id_int})

    progress_id = progress_res.get('id') if isinstance(progress_res, dict) else None
    if not progress_id:
        gr.Error("Could not get a valid progress ID from the backend.")
        return None, None, 0, 0, gr.Tabs(selected=1), None, gr.Button(visible=True), gr.Button(visible=True), gr.Button(visible=False), gr.Markdown(visible=False)


    level_titles = [level.get('level_title', f"Level {i + 1}") for i, level in enumerate(path_data.get('levels', []))]

    return (path_data, progress_id, 0, 0, gr.Tabs(selected=2),
            gr.Radio(choices=level_titles, value=level_titles[0]),
            gr.Button(visible=True), gr.Button(visible=True),
            gr.Button(visible=False), gr.Markdown(visible=False))


def render_learn_view(path_data, level_idx, item_idx):
    if not path_data:
        return "No path loaded.", "", gr.Radio(choices=[], value=None, visible=False), gr.Button(visible=False), ""

    level = path_data['levels'][level_idx]
    item = level['content_items'][item_idx]

    header = f"## {path_data['title']} - Level {level_idx + 1}/{path_data['total_levels']}"
    content_md = f"### {level['level_title']} ({item_idx + 1}/{len(level['content_items'])})\n\n---\n\n"

    quiz_options = gr.Radio(choices=[], value=None, visible=False)
    submit_button = gr.Button(visible=False)
    feedback_md = ""

    if item['item_type'] == 'slide':
        content_md += item['content']
    elif item['item_type'] == 'quiz':
        quiz_data = item['content']
        content_md += f"**Question:** {quiz_data['question']}"
        quiz_options = gr.Radio(choices=quiz_data['options'], value=None, visible=True, interactive=True)
        submit_button = gr.Button(visible=True)

    return header, content_md, quiz_options, submit_button, feedback_md


def handle_navigation(path_data, progress_id, level_idx, item_idx, direction):
    if not path_data:
        return path_data, progress_id, level_idx, item_idx, None, gr.Button(visible=True), gr.Button(visible=True), gr.Button(visible=False), gr.Markdown(visible=False)


    num_levels = len(path_data['levels'])
    num_items_in_level = len(path_data['levels'][level_idx]['content_items'])

    if direction == "next":
        if item_idx < num_items_in_level - 1:
            item_idx += 1
        elif level_idx < num_levels - 1:
            level_idx += 1
            item_idx = 0
            gr.Info(f"Great work! Moving to Level {level_idx + 1}.")
        else:
            gr.Info("🎉 Congratulations! You have completed the path!")
            return (path_data, progress_id, level_idx, item_idx, gr.Radio(),
                    gr.Button(visible=False), gr.Button(visible=False),
                    gr.Button(visible=True),
                    gr.Markdown(visible=True, value="### You've earned an NFT!\n\nClick the button below to mint your certificate to your wallet."))
    elif direction == "prev":
        if item_idx > 0:
            item_idx -= 1
        elif level_idx > 0:
            level_idx -= 1
            item_idx = len(path_data['levels'][level_idx]['content_items']) - 1

    make_api_request("POST", f"{BACKEND_URL}/progress/location",
                     payload={"progress_id": progress_id, "item_index": item_idx})

    new_level_title = path_data['levels'][level_idx]['level_title']
    return (path_data, progress_id, level_idx, item_idx, gr.Radio(value=new_level_title),
            gr.Button(visible=True), gr.Button(visible=True),
            gr.Button(visible=False), gr.Markdown(visible=False))


def select_level(path_data, progress_id, selected_title):
    if not path_data or not selected_title:
        return 0, 0

    level_titles = [level.get('level_title') for level in path_data.get('levels', [])]
    try:
        new_level_index = level_titles.index(selected_title)
        make_api_request("POST", f"{BACKEND_URL}/progress/location",
                         payload={"progress_id": progress_id, "item_index": 0})
        return new_level_index, 0
    except ValueError:
        return 0, 0


def submit_quiz(path_data, progress_id, level_idx, item_idx, selected_answer):
    if selected_answer is None:
        gr.Warning("Please select an answer.")
        return ""

    item = path_data['levels'][level_idx]['content_items'][item_idx]
    quiz_data = item['content']

    correct_idx = quiz_data['correctAnswerIndex']
    options = quiz_data['options']
    selected_idx = options.index(selected_answer)
    is_correct = selected_idx == correct_idx

    make_api_request("POST", f"{BACKEND_URL}/progress/update", payload={
        "progress_id": progress_id,
        "content_item_id": item['id'],
        "user_answer_index": selected_idx
    })

    if is_correct:
        feedback = f"✅ **Correct!** Great job.\n\n---\n\n**Explanation:** {quiz_data['explanation']}"
        gr.Info("Correct! Moving to the next item in 3 seconds...")
        time.sleep(3)
    else:
        feedback = f"❌ **Incorrect.** The correct answer was: **{options[correct_idx]}**\n\n---\n\n**Explanation:** {quiz_data['explanation']}"

    return feedback


def get_lucky_topic():
    response = make_api_request("GET", f"{BACKEND_URL}/paths/random-topic")
    if "error" in response:
        gr.Error(f"Could not get a topic: {response['error']}")
        return ""
    return response.get('topic', '')


def mint_nft_for_path(path_data, user_wallet):
    if not path_data or not user_wallet:
        yield "Path data or user wallet is missing. Cannot mint."
        return

    path_id = path_data.get('id')
    yield "### 🏆 Minting your NFT...\n\nThis may take a minute. Please wait for the transaction to be confirmed on the blockchain."

    response = make_api_request(
        "POST",
        f"{BACKEND_URL}/paths/{path_id}/complete",
        payload={"user_wallet": user_wallet},
        timeout=180
    )

    if "error" in response:
        error_detail = response.get('detail', 'No details provided.')
        yield f"### ❌ Minting Failed\n\n**Reason:** {response.get('error')}\n\n**Details:** {error_detail}"
        return

    token_id = response.get('token_id')
    contract_address = response.get('nft_contract_address')

    success_message = f"""
    ### 🎉 NFT Minted Successfully!

    Congratulations! Your unique Certificate of Completion has been minted to the blockchain.

    **Token ID:** `{token_id}`
    **NFT Contract Address:** `{contract_address}`

    ---

    #### 🦊 How to Add Your NFT to MetaMask

    1.  **Open MetaMask** and ensure you are connected to the **Sepolia Test Network**.
    2.  Go to the **"NFTs"** tab in your wallet.
    3.  Scroll to the bottom and click **"Import NFTs"**.
    4.  In the "Address" field, paste the NFT Contract Address:
        ```
        {contract_address}
        ```
    5.  In the "Token ID" field, enter your unique ID:
        ```
        {token_id}
        ```
    6.  Click **"Add"** and your Noodl certificate will appear in your wallet!
    """
    yield success_message


# --- Gradio UI Definition ---
def create_and_launch_demo_ui(port):
    with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}", title="Noodl Live Demo") as demo:
        user_wallet = gr.State(None)
        user_name = gr.State(None)
        user_country = gr.State(None)

        current_path_data = gr.State(None)
        current_progress_id = gr.State(None)
        current_level_index = gr.State(0)
        current_item_index = gr.State(0)

        with gr.Tabs() as main_tabs:
            with gr.TabItem("Login", id=0):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Image("ui/assets/logo.png", show_label=False, container=False)
                    with gr.Column(scale=2):
                        gr.Markdown("# Welcome to Noodl!\nYour personal AI-powered learning companion.")
                        login_wallet_input = gr.Textbox(label="Your Wallet Address", placeholder="0x123...")
                        login_name_input = gr.Textbox(label="Your Name", placeholder="Alex")
                        login_country_input = gr.Textbox(label="Your Country", placeholder="Canada")
                        login_button = gr.Button("Login / Register", variant="primary")

            with gr.TabItem("Dashboard", id=1):
                gr.Markdown("# 🍜 Noodl Dashboard")
                with gr.Row():
                    with gr.Column(scale=2):
                        with gr.Accordion("✨ Create a New Learning Path", open=True):
                            generate_topic_input = gr.Textbox(label="What do you want to learn about?",
                                                              placeholder="e.g., How to bake sourdough bread")
                            with gr.Row():
                                generate_button = gr.Button("Generate Path", variant="primary")
                                lucky_button = gr.Button("I'm Feeling Lucky 🎲")

                        with gr.Accordion("🔍 Search for a Path", open=True):
                            search_query_input = gr.Textbox(label="Search Query",
                                                            placeholder="Search for 'python', 'history', etc.")
                            search_button = gr.Button("Search")
                            search_results_df = gr.DataFrame(headers=["ID", "Title", "Match Type"], interactive=False,
                                                             col_count=(3, "fixed"))

                    with gr.Column(scale=3):
                        generation_progress_output = gr.Markdown("Your generation progress will appear here...")
                        generate_continue_button = gr.Button("Continue to Path", visible=False)
                        generate_tx_button = gr.Button("View Transaction", visible=False, link="",
                                                       icon="https://etherscan.io/images/favicon.ico")

                with gr.Tabs():
                    with gr.TabItem("My Created Paths"):
                        my_paths_df = gr.DataFrame(headers=["ID", "Title", "Levels"], interactive=False,
                                                   col_count=(3, "fixed"))
                    with gr.TabItem("All Public Paths"):
                        all_paths_df = gr.DataFrame(headers=["ID", "Title", "Levels"], interactive=False,
                                                    col_count=(3, "fixed"))

                refresh_dashboard_button = gr.Button("Refresh Dashboard")
                start_learning_button = gr.Button("Start Learning Selected Path", variant="secondary")
                selected_path_id = gr.Textbox(label="Enter Path ID to start learning", placeholder="e.g., 42")

            with gr.TabItem("Learn", id=2):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Levels")
                        level_selector_radio = gr.Radio(label="Path Outline", interactive=True)
                        back_to_dashboard_button = gr.Button("⬅️ Back to Dashboard")

                    with gr.Column(scale=3):
                        learn_header_md = gr.Markdown("## Path Title")
                        learn_content_md = gr.Markdown("Content will be loaded here.")
                        quiz_options_radio = gr.Radio(label="Your Answer", visible=False)
                        submit_quiz_button = gr.Button("Submit Answer", variant="primary", visible=False)
                        quiz_feedback_md = gr.Markdown()
                        with gr.Row():
                            prev_button = gr.Button("⬅️ Previous")
                            next_button = gr.Button("Next ➡️")
                        mint_nft_button = gr.Button("🏆 Mint Completion NFT", variant="primary", visible=False)
                        minting_output_md = gr.Markdown(visible=False)

        # --- Event Handling ---

        login_button.click(fn=login_user, inputs=[login_wallet_input, login_name_input, login_country_input],
                           outputs=[user_wallet, user_name, user_country, main_tabs]).then(fn=refresh_dashboard,
                                                                                           inputs=[user_wallet],
                                                                                           outputs=[my_paths_df,
                                                                                                    all_paths_df])
        refresh_dashboard_button.click(fn=refresh_dashboard, inputs=[user_wallet], outputs=[my_paths_df, all_paths_df])
        search_button.click(search_for_paths, search_query_input, search_results_df)

        generate_button.click(fn=generate_path_live, inputs=[generate_topic_input, user_wallet],
                              outputs=[generation_progress_output, generate_continue_button, generate_tx_button])
        lucky_button.click(fn=get_lucky_topic, outputs=[generate_topic_input]).then(fn=generate_path_live,
                                                                                    inputs=[generate_topic_input,
                                                                                            user_wallet],
                                                                                    outputs=[generation_progress_output,
                                                                                             generate_continue_button,
                                                                                             generate_tx_button])

        def continue_to_path_from_generation(path_id_str, wallet):
            path_id = int(path_id_str.split()[-1])
            return start_learning_path(path_id, wallet)

        start_learning_outputs = [current_path_data, current_progress_id, current_level_index,
                                  current_item_index, main_tabs, level_selector_radio,
                                  prev_button, next_button, mint_nft_button, minting_output_md]

        generate_continue_button.click(fn=continue_to_path_from_generation,
                                       inputs=[generate_continue_button, user_wallet],
                                       outputs=start_learning_outputs)
        start_learning_button.click(fn=start_learning_path, inputs=[selected_path_id, user_wallet],
                                    outputs=start_learning_outputs)

        render_outputs = [learn_header_md, learn_content_md, quiz_options_radio, submit_quiz_button, quiz_feedback_md]
        main_tabs.select(fn=render_learn_view, inputs=[current_path_data, current_level_index, current_item_index],
                         outputs=render_outputs)

        back_to_dashboard_button.click(lambda: gr.Tabs(selected=1), outputs=[main_tabs])

        nav_outputs = [current_path_data, current_progress_id, current_level_index, current_item_index,
                       level_selector_radio, prev_button, next_button, mint_nft_button, minting_output_md]

        prev_button.click(fn=handle_navigation,
                          inputs=[current_path_data, current_progress_id, current_level_index, current_item_index,
                                  gr.State("prev")],
                          outputs=nav_outputs).then(fn=render_learn_view,
                                                    inputs=[current_path_data, current_level_index,
                                                            current_item_index],
                                                    outputs=render_outputs)
        next_button.click(fn=handle_navigation,
                          inputs=[current_path_data, current_progress_id, current_level_index, current_item_index,
                                  gr.State("next")],
                          outputs=nav_outputs).then(fn=render_learn_view,
                                                    inputs=[current_path_data, current_level_index,
                                                            current_item_index],
                                                    outputs=render_outputs)

        level_selector_radio.select(fn=select_level,
                                    inputs=[current_path_data, current_progress_id, level_selector_radio],
                                    outputs=[current_level_index, current_item_index]).then(fn=render_learn_view,
                                                                                            inputs=[current_path_data,
                                                                                                    current_level_index,
                                                                                                    current_item_index],
                                                                                            outputs=render_outputs)

        submit_quiz_button.click(fn=submit_quiz, inputs=[current_path_data, current_progress_id, current_level_index,
                                                         current_item_index, quiz_options_radio],
                                 outputs=[quiz_feedback_md])

        mint_nft_button.click(fn=mint_nft_for_path, inputs=[current_path_data, user_wallet],
                              outputs=[minting_output_md])

    demo.launch(server_name="0.0.0.0", server_port=port, share=True)