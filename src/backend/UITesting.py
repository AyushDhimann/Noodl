import gradio as gr
import requests
import json

# --- Configuration ---
BACKEND_URL = "http://localhost:5000"

# --- API Client Functions ---
def generate_path(topic, wallet_address):
    if not topic or not wallet_address: return {"error": "Please provide both a topic and a wallet address."}
    endpoint = f"{BACKEND_URL}/paths/generate"
    payload = {"topic": topic, "creator_wallet": wallet_address}
    try:
        response = requests.post(endpoint, json=payload, timeout=300)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}

def get_all_paths():
    endpoint = f"{BACKEND_URL}/paths"
    try:
        response = requests.get(endpoint, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}

def get_level_content(path_id, level_num):
    if not path_id or not level_num: return {"error": "Please provide both a Path ID and a Level Number."}
    endpoint = f"{BACKEND_URL}/paths/{path_id}/levels/{level_num}"
    try:
        response = requests.get(endpoint, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}

def mint_nft(path_id, user_wallet):
    if not path_id or not user_wallet: return {"error": "Please provide both a Path ID and a User Wallet address."}
    endpoint = f"{BACKEND_URL}/paths/{path_id}/complete"
    payload = {"user_wallet": user_wallet}
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "Connection to backend failed.", "details": str(e)}

# --- Gradio UI Definition ---
with gr.Blocks(theme=gr.themes.Soft(), title="Noodl Backend Tester") as demo:
    gr.Markdown("# 🍜 Noodl Backend Tester")
    gr.Markdown("A simple interface to test the core functionalities of the Noodl Flask API.")

    with gr.Tabs():
        with gr.TabItem("1. Generate New Path"):
            gr.Markdown("### Create a new learning path using AI.")
            with gr.Row():
                topic_input = gr.Textbox(label="Learning Topic", placeholder="e.g., The History of Ancient Egypt")
                wallet_input_gen = gr.Textbox(label="Creator's Wallet Address", placeholder="0x...")
            generate_btn = gr.Button("✨ Generate Path", variant="primary")
            generate_output = gr.JSON(label="API Response")
            generate_btn.click(fn=generate_path, inputs=[topic_input, wallet_input_gen], outputs=generate_output)

        with gr.TabItem("2. View Content"):
            gr.Markdown("### Fetch existing paths and the content of their levels.")
            with gr.Row():
                with gr.Column(scale=1):
                    refresh_paths_btn = gr.Button("🔄 Refresh Path List")
                    path_list_output = gr.JSON(label="Available Paths")
                with gr.Column(scale=2):
                    path_id_input = gr.Number(label="Path ID", precision=0)
                    level_num_input = gr.Number(label="Level Number", precision=0)
                    get_content_btn = gr.Button("📚 Get Level Content")
                    level_content_output = gr.JSON(label="Level Content (Slides & Quiz)")
            refresh_paths_btn.click(fn=get_all_paths, inputs=[], outputs=path_list_output)
            get_content_btn.click(fn=get_level_content, inputs=[path_id_input, level_num_input], outputs=level_content_output)

        with gr.TabItem("3. Mint NFT Certificate"):
            gr.Markdown("### Mint an NFT certificate for completing a path.")
            with gr.Row():
                path_id_nft_input = gr.Number(label="Completed Path ID", precision=0)
                user_wallet_nft_input = gr.Textbox(label="User's Wallet to Receive NFT", placeholder="0x...")
            mint_btn = gr.Button("🏆 Mint NFT", variant="primary")
            mint_output = gr.JSON(label="API Response")
            mint_btn.click(fn=mint_nft, inputs=[path_id_nft_input, user_wallet_nft_input], outputs=mint_output)

if __name__ == "__main__":
    demo.launch()