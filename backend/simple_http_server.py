#!/usr/bin/env python3
"""
Simple HTTP Server for CKEmpire
"""

import http.server
import socketserver
import json
import threading
import time

class CKEmpireHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "CKEmpire API",
                "status": "running",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/v1/finance/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy", "module": "finance"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/v1/finance/roi':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "roi_percentage": 150.0,
                "annualized_roi": 75.0,
                "payback_period": 0.8,
                "status": "calculated"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/v1/finance/cac-ltv':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "cac": 50.0,
                "ltv": 200.0,
                "ltv_cac_ratio": 4.0,
                "profitability_score": "Excellent",
                "status": "calculated"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    PORT = 8015
    with socketserver.TCPServer(("", PORT), CKEmpireHandler) as httpd:
        print(f"🚀 Starting CKEmpire HTTP Server on port {PORT}")
        print(f"📍 URL: http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server() 