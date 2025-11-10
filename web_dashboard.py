"""
================================================================================
PROJECT: Live AI 3D Printer Monitor
FILE: web_dashboard.py
PURPOSE: Flask + SocketIO web server for live dashboard.
Based on: SECTION 6: LIVE WEB DASHBOARD STRUCTURE
================================================================================
"""

import threading
import base64
import time
import cv2
from flask import Flask, render_template, Response
from flask_socketio import SocketIO

class LiveWebDashboard:
    """
    Runs a Flask server in a background thread to provide a live
    web interface with SocketIO for real-time updates.
    """
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates')
        # Allow all origins for simplicity in this solo project
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.clients = 0
        
        self._setup_routes()
        self._setup_socketio()
        
        # Start Flask server in a background thread
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True,
            name="WebThread"
        )
        self.server_thread.start()
        
    def _run_server(self):
        print("[WEB] Web Dashboard starting on http://0.0.0.0:5000")
        try:
            # Use 'werkzeug' for development, 'gunicorn' or 'waitress' for production
            self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
        except Exception as e:
            print(f"[WEB] Server failed to start: {e}")
            print("[WEB] Is port 5000 already in use?")
    
    def _setup_routes(self):
        """Defines the main HTML page routes."""
        @self.app.route('/')
        def index():
            # Renders the live.html template
            return render_template('live.html')
        
        @self.app.route('/logs')
        def logs():
            # Placeholder for a future logs page
            log_content = "Log file not found."
            try:
                with open('print_monitor.log', 'r') as f:
                    log_content = f.read()
            except FileNotFoundError:
                pass
            return f"<html><body style='background:#111; color: #eee; font-family: monospace; white-space: pre-wrap;'><h1>Print Logs</h1>{log_content}</body></html>"
    
    def _setup_socketio(self):
        """Defines SocketIO event handlers."""
        @self.socketio.on('connect')
        def handle_connect():
            self.clients += 1
            print(f"[WEB] Client connected. Total clients: {self.clients}")
            self.socketio.emit('live_status', {'status': 'Connected', 'clients': self.clients})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.clients -= 1
            print(f"[WEB] Client disconnected. Total clients: {self.clients}")

        @self.socketio.on('ping')
        def handle_ping():
            self.socketio.emit('pong')
            
        # TODO: Add handlers for buttons (Pause, Resume, Stop)
        # This requires passing the 'printer' object to this class from main.py
        
        # @self.socketio.on('printer_pause')
        # def handle_pause():
        #     print("[WEB] Pause command received!")
        #     # self.printer.pause_live("WEB_PAUSE")
            
        # @self.socketio.on('printer_stop')
        # def handle_stop():
        #     print("[WEB] STOP command received!")
        #     # self.printer.emergency_stop_live()

    def broadcast_live_frame(self, frame, metadata):
        """
        Encodes and broadcasts a live frame and metadata to all clients.
        """
        if self.clients == 0:
            return  # No clients connected, skip encoding
        
        try:
            # Resize frame for web to save bandwidth (960x540 is 16:9)
            web_frame = cv2.resize(frame, (960, 540))
            
            # Encode as JPEG (fast, good compression)
            _, buffer = cv2.imencode('.jpg', web_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            
            # Convert to base64 string
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Emit data packet
            self.socketio.emit('live_frame', {
                'image': image_base64,
                'layer': metadata.get('layer', 0),
                'temp': metadata.get('temp', {}),
                'defect': metadata.get('defect', None),
                'timestamp': time.time()
            })
        except Exception as e:
            print(f"[WEB] Error broadcasting frame: {e}")
    
    def broadcast_live_status(self, status_dict):
        """Broadcast a generic status update."""
        if self.clients > 0:
            self.socketio.emit('live_status', status_dict)