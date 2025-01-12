from cryptography.hazmat.primitives import serialization
import hashlib
import base64

class KeyManager:
    """Singleton to manage RSA keys and precomputed values."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeyManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, private_key_path="/run/secrets/jwt_signing_key"):
        if not self._initialized:
            self.private_key_path = private_key_path
            self.private_key = None
            self.public_key = None
            self.n = None
            self.e = None
            self.kid = None
            self._load_keys()
            self._initialized = True

    def _load_keys(self):
        """Load the private key and precompute n and e."""
        with open(self.private_key_path, "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(), password=None
            )
            self.public_key = self.private_key.public_key()
            numbers = self.public_key.public_numbers()
            self.n = base64.urlsafe_b64encode(
                numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
            ).decode("utf-8").rstrip("=")
            self.e = base64.urlsafe_b64encode(
                numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
            ).decode("utf-8").rstrip("=")
            self.kid = base64.urlsafe_b64encode(
                hashlib.sha256(
                    self.n.encode() + self.e.encode()
                ).digest()
            ).decode("utf-8").rstrip("=")

    def get_private_key(self):
        """Return the private key."""
        return self.private_key

    def get_public_key_info(self):
        """Return n and e for JWKS."""
        return {"n": self.n, "e": self.e}
    
    def get_kid(self):
        return self.kid