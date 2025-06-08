from flask import request
from app import logger

def register_events(socketio):
    @socketio.on('connect', namespace='/pathProgress')
    def handle_connect():
        logger.info(f"SOCKET.IO: Client connected with sid: {request.sid}")

    @socketio.on('disconnect', namespace='/pathProgress')
    def handle_disconnect():
        logger.info(f"SOCKET.IO: Client disconnected with sid: {request.sid}")