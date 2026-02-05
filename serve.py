from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/market-summary':
            try:
                # Run the script
                result = subprocess.run(
                    ['python', r'C:\scripts\investment-summary\daily_market_summary.py'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result.stdout.encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

print("Market Summary API running on http://localhost:8080")
print("Endpoint: http://localhost:8080/market-summary")
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()