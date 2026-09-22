import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and caching headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = CustomHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}"
            print("=" * 60)
            print(f"  Fudali Studio Local Clone Running at: {url}")
            print("  Animations, local assets, styles & interactions active!")
            print("  Press Ctrl+C to stop the server.")
            print("=" * 60)
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except OSError as e:
        print(f"Error binding to port {PORT}: {e}")
        print("Try changing the port or ensuring another instance isn't running.")

if __name__ == "__main__":
    run_server()
