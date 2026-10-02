import hashlib
import secrets
import string
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

CLIENT_KEY = "
awlrdla37rmus58l"
REDIRECT_URI = "http://127.0.0.1:3455/callback/"

PORT = 3455

state = secrets.token_urlsafe(32)

characters = string.ascii_letters + string.digits + "-._~"
code_verifier = "".join(secrets.choice(characters) for _ in range(64))

code_challenge = hashlib.sha256(
    code_verifier.encode()
).hexdigest()

params = {
    "client_key": CLIENT_KEY,
    "response_type": "code",
    "scope": "user.info.basic",
    "redirect_uri": REDIRECT_URI,
    "state": state,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
}

auth_url = (
    "https://www.tiktok.com/v2/auth/authorize/?"
    + urlencode(params)
)

print("\nOpening TikTok login...")
print("\nIf the browser doesn't open automatically, use this URL:\n")
print(auth_url)

class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        returned_state = query.get("state", [None])[0]
        code = query.get("code", [None])[0]
        error = query.get("error", [None])[0]
        error_description = query.get(
            "error_description", [None]
        )[0]

        if returned_state != state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid state.")
            return

        if error:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                f"TikTok error: {error}\n{error_description}".encode()
            )
            return

        if code:
            print("\nSUCCESS!")
            print("Authorization code received.")
            print("\nCode:")
            print(code)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"Login successful. You can return to Termux."
            )

            self.server.code = code
            return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"No authorization code received.")


server = HTTPServer(("127.0.0.1", PORT), CallbackHandler)

webbrowser.open(auth_url)

print("\nWaiting for TikTok authorization...")
server.handle_request()

if hasattr(server, "code"):
    print("\nYour authorization code was received.")
    print("Keep it private.")
