from app import app
from app.config import config
from ui.testing_ui import create_and_launch_ui
import threading

if __name__ == '__main__':
    if config.RUN_API_SERVER:
        # Run Flask in a separate thread if UI is also running
        if config.RUN_TESTING_UI:
            api_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
            api_thread.daemon = True
            api_thread.start()
            print("--- Flask API Server started in background thread ---")
        else:
            print("--- Starting Flask API Server on http://localhost:5000 ---")
            app.run(host='0.0.0.0', port=5000, debug=True)

    if config.RUN_TESTING_UI:
        print("--- Starting Gradio UI on http://localhost:7000 ---")
        create_and_launch_ui()