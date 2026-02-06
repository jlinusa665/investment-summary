from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/market-summary':
            try:
                # Build command with optional timing flag
                cmd = ['python', r'C:\scripts\investment-summary\daily_market_summary.py']

                timing = query_params.get('timing', [None])[0]
                if timing in ('morning', 'close'):
                    cmd.extend(['--timing', timing])

                # Run the script
                result = subprocess.run(
                    cmd,
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
print("Endpoints:")
print("  http://localhost:8080/market-summary")
print("  http://localhost:8080/market-summary?timing=morning")
print("  http://localhost:8080/market-summary?timing=close")
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()