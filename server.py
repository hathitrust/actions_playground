from http.server import SimpleHTTPRequestHandler
import socketserver

PORT = 7000

def run_server():
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
         print(f"Serving on port {PORT}")
         httpd.serve_forever()