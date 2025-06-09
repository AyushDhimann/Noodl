from app import app, config
from ui.testing_ui import create_and_launch_ui
import threading

if __name__ == '__main__':
    # For clarity, let's print the configuration being used
    print("--- Noodl Backend Configuration ---")
    print(f"RUN_API_SERVER: {config.RUN_API_SERVER}")
    print(f"RUN_TESTING_UI: {config.RUN_TESTING_UI}")
    print("-----------------------------------")

    run_api = config.RUN_API_SERVER
    run_ui = config.RUN_TESTING_UI

    if run_api and run_ui:
        print("--- Mode: API + UI ---")
        print("Starting Flask API server in a background thread...")
        # When running both, it's crucial to disable Flask's reloader to avoid issues with threading.
        api_thread = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        )
        api_thread.daemon = True
        api_thread.start()
        print("--- Flask API Server is running on http://localhost:5000 ---")

        print("\nStarting Gradio UI in the main thread...")
        print("--- Gradio UI will be available at http://localhost:7000 ---")
        create_and_launch_ui()

    elif run_api:
        print("--- Mode: API Only ---")
        print("--- Starting Flask API Server on http://localhost:5000 ---")
        # The reloader is fine here since it's the only process.
        app.run(host='0.0.0.0', port=5000, debug=True)

    elif run_ui:
        print("--- Mode: UI Only ---")
        print("--- Starting Gradio UI on http://localhost:7000 ---")
        create_and_launch_ui()

    else:
        print("--- Mode: Disabled ---")
        print("Both API server and UI are disabled in the .env file. Exiting.")