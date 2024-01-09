# services/websocket_services.py

from app import socketio
import json 

def send_message_to_scrapy_namespace(message_data):
    socketio.emit("message", json.dumps(message_data), namespace="/scrapy")
