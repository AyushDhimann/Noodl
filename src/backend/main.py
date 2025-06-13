from app import app, config
from ui.live_demo import create_and_launch_demo_ui
import threading

if __name__ == '__main__':
    # For clarity, let's print the configuration being used
    print("--- Noodl Backend Configuration ---")
    print(f"RUN_API_SERVER: {config.RUN_API_SERVER}")
    print(f"RUN_LIVE_DEMO: {config.RUN_LIVE_DEMO}")
    print("-----------------------------------")

    run_api = config.RUN_API_SERVER
    run_demo = config.RUN_LIVE_DEMO

    # Start API server in a background thread if the live demo UI is active
    if run_api and run_demo:
        print("--- Mode: API in Background ---")
        print("Starting Flask API server in a background thread...")
        api_thread = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        )
        api_thread.daemon = True
        api_thread.start()
        print("--- Flask API Server is running on http://localhost:5000 ---")

    # Launch the Live Demo UI in the main thread
    if run_demo:
        print("\n--- Mode: Live Demo UI ---")
        print(f"--- Starting Gradio Live Demo UI on http://localhost:{config.LIVE_DEMO_PORT} ---")
        create_and_launch_demo_ui(config.LIVE_DEMO_PORT)
    # If only the API is enabled, run it in the main thread
    elif run_api:
        print("--- Mode: API Only ---")
        print("--- Starting Flask API Server on http://localhost:5000 ---")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("--- Mode: Disabled ---")
        print("All servers and UIs are disabled in the .env file. Exiting.")