from flask import Flask, redirect, request, session
import requests
import jwt
import base64
import os
from urllib.parse import urlencode
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
CLIENT_ID = 'c__5ntHSdcTcCe64XMX4kGKA'
CLIENT_SECRET = 'test-secret'
AUTHORIZATION_BASE_URL = 'http://localhost:8091/authorize'
TOKEN_URL = 'http://localhost:8091/oauth2/token'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Helper function to encode a nonce
def create_nonce():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    session['private_key'] = private_key.decode()
    return base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')

@app.route('/')
def home():
    return '<h1>Welcome</h1><a href="/login">Login with OAuth2</a>'

@app.route('/login')
def login():
    nonce = create_nonce()
    next_page = request.args.get('next_page', '/')
    state = base64.urlsafe_b64encode(f"{nonce}:{next_page}".encode()).decode('utf-8')
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid profile email',
        'state': state
    }
    authorization_url = f"{AUTHORIZATION_BASE_URL}?{urlencode(params)}"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    print(f"Received callback with code: {code}")
    
    if not code or not state:
        return 'Authorization failed!', 400

    # Decode state and extract nonce and next_page
    decoded_state = base64.urlsafe_b64decode(state).decode('utf-8')
    nonce, next_page = decoded_state.split(':')

    # Exchange authorization code for tokens
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
#        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    token_response = requests.post(TOKEN_URL, data=token_data)
    print(f"Status Code: {token_response.status_code}")
    print(f"Response Body: {token_response.text}")

    if token_response.status_code != 200:
        print(token_response)
        return 'Token exchange failed!', 400

    tokens = token_response.json()
    id_token = tokens.get('id_token')
    
    # Decode JWT
    try:
        decoded_jwt = jwt.decode(id_token, options={"verify_signature": False})
    except Exception as e:
        return f"Failed to decode JWT: {str(e)}", 400

    return f'<h1>JWT Contents</h1><pre>{decoded_jwt}</pre>'

if __name__ == '__main__':
    app.run(debug=True)

