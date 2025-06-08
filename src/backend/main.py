import multiprocessing
import sys
import time
from app import app, socketio
from app.config import config
from ui.testing_ui import create_and_launch_ui

def run_api():
    """Runs the Flask API server with SocketIO."""
    print("--- Starting API Server on http://localhost:5000 ---")
    # THE FIX: When running in a multiprocessing context on Windows,
    # we must disable the reloader to prevent the EOFError.
    # The debugger can remain active.
    # `debug=True` implies `use_reloader=True`, so we explicitly set it to False.
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False, # This is the critical change
        allow_unsafe_werkzeug=True
    )

def run_ui():
    """Runs the Gradio Testing UI."""
    print("--- Starting Gradio UI on http://localhost:7000 ---")
    create_and_launch_ui()

if __name__ == '__main__':
    # Set the start method for multiprocessing, recommended for cross-platform compatibility
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass

    # Use a basic argument parser to choose what to run
    if len(sys.argv) > 1:
        if sys.argv[1] == 'api':
            run_api()
        elif sys.argv[1] == 'ui':
            run_ui()
        else:
            print("Invalid argument. Use 'api' or 'ui'.")
    else:
        # Default behavior: run both if enabled in .env
        api_process = None
        ui_process = None

        if config.RUN_API_SERVER:
            print("API Server is enabled. Starting process...")
            api_process = multiprocessing.Process(target=run_api)
            api_process.start()
        else:
            print("API Server is disabled in .env file.")

        if config.RUN_TESTING_UI:
            # This check ensures the UI doesn't start if the API isn't meant to.
            if api_process:
                print("Testing UI is enabled. Starting process...")
                # Give the API a moment to start up before launching the UI
                time.sleep(5)
                ui_process = multiprocessing.Process(target=run_ui)
                ui_process.start()
            else:
                print("Testing UI is disabled because the API server is not running.")
        else:
            print("Testing UI is disabled in .env file.")

        # Keep the main script alive to manage child processes
        try:
            if api_process:
                api_process.join()
            if ui_process:
                ui_process.join()
        except KeyboardInterrupt:
            print("\nCaught KeyboardInterrupt, terminating processes.")
            if api_process and api_process.is_alive():
                api_process.terminate()
                api_process.join()
            if ui_process and ui_process.is_alive():
                ui_process.terminate()
                ui_process.join()