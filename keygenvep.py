from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate VAPID keys
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Encode the keys
private_key_encoded = urlsafe_b64encode(
    private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
).rstrip(b'=').decode('utf-8')

public_key_encoded = urlsafe_b64encode(
    public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
).rstrip(b'=').decode('utf-8')

print("Public key: ", public_key_encoded)
print("Private key: ", private_key_encoded)
