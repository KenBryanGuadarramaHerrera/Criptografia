from cryptography.hazmat.primitives.asymmetric import rsa as rsa_crypto, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature

import hashlib
import rsa  # python-rsa
from rsa.prime import are_relatively_prime
import secrets


# ========== Generación y serialización (PKCS#1) ==========

def generate_rsa_key_pair(key_size: int = 2048):
    """Genera una llave privada RSA con cryptography (para firma normal)."""
    return rsa_crypto.generate_private_key(public_exponent=65537, key_size=key_size)

def serialize_private_key(private_key) -> bytes:
    """
    Serializa la privada en PKCS#1 => '-----BEGIN RSA PRIVATE KEY-----'
    Compatible con rsa.PrivateKey.load_pkcs1(...)
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        encryption_algorithm=serialization.NoEncryption()
    )

def serialize_public_key(private_key) -> bytes:
    """
    Serializa la pública en PKCS#1 => '-----BEGIN RSA PUBLIC KEY-----'
    Compatible con rsa.PublicKey.load_pkcs1(...)
    """
    pub = private_key.public_key()
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )

# ========== Hash y firma/verificación con cryptography ==========

def hash_vote_data(data: str) -> str:
    """Hash SHAKE128 en hex (64 chars = 32 bytes)."""
    h = hashlib.shake_128(data.encode("utf-8"))
    return h.hexdigest(32)

def sign_hash(private_pem: bytes, hashed_hex: str) -> bytes:
    """
    Firma el hash (en hex) usando la privada (PKCS#1 o PKCS#8) con PSS+SHA256.
    """
    private_key = load_pem_private_key(private_pem, password=None)
    return private_key.sign(
        bytes.fromhex(hashed_hex),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )

def verify_signature(public_pem: bytes | str, hashed_hex: str, signature: bytes) -> bool:
    """
    Verifica firma PSS+SHA256. Acepta pública en PKCS#1 o SubjectPublicKeyInfo.
    """
    try:
        if isinstance(public_pem, str):
            public_pem = public_pem.encode("utf-8")
        public_key = load_pem_public_key(public_pem)
        public_key.verify(
            signature,
            bytes.fromhex(hashed_hex),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except (InvalidSignature, ValueError, TypeError) as e:
        print(f"Error de verificación: {e}")
        return False

# ========== Carga de llaves de autoridad (archivos .pem generados con python-rsa) ==========

def load_authority_public_key_text() -> str | None:
    try:
        with open("authority_public.pem", "rb") as f:
            return f.read().decode("utf-8")
    except FileNotFoundError:
        print("ERROR: authority_public.pem no encontrado.")
        return None

def load_authority_private_key_text() -> str | None:
    try:
        with open("authority_private.pem", "rb") as f:
            return f.read().decode("utf-8")
    except FileNotFoundError:
        print("ERROR: authority_private.pem no encontrado.")
        return None

# ========== Firma ciega (python-rsa) ==========

def _load_rsa_public_for_blind(public_pem_text: str) -> rsa.PublicKey:
    """
    Carga pública para blind firma.
    - Si viene como '-----BEGIN RSA PUBLIC KEY-----' => PKCS#1 -> load_pkcs1
    - Si viene como '-----BEGIN PUBLIC KEY-----'     => SPKI/PKCS#8 -> load_pkcs1_openssl_pem
    """
    pem = public_pem_text.strip().encode("utf-8")
    if b"BEGIN RSA PUBLIC KEY" in pem:
        return rsa.PublicKey.load_pkcs1(pem)  # PKCS#1
    else:
        # 'BEGIN PUBLIC KEY' (SPKI)
        return rsa.PublicKey.load_pkcs1_openssl_pem(pem)

def _load_rsa_private_for_blind(private_pem_text: str) -> rsa.PrivateKey:
    """
    Carga privada PKCS#1 para blind firma.
    """
    pem = private_pem_text.strip().encode("utf-8")
    return rsa.PrivateKey.load_pkcs1(pem)

def blind_hash(public_pem_text: str, hashed_hex: str) -> tuple[bytes, int]:
    """
    Ciega el hash (hex) con la pública de la autoridad.
    Devuelve (blinded_bytes, r) donde r es el factor de cegado coprimo con n.
    """
    pub = _load_rsa_public_for_blind(public_pem_text)

    # Mensaje como entero a partir de los bytes reales del hash
    m = int.from_bytes(bytes.fromhex(hashed_hex), "big")

   # Generar un r aleatorio coprimo con n
    while True:
        # Usa secrets para generar números seguros criptográficamente
        r = secrets.randbelow(pub.n - 1) + 1  # 1 ≤ r < n
        if are_relatively_prime(r, pub.n):
            break

    # m_blind = m * (r^e mod n) mod n
    blinded = (m * pow(r, pub.e, pub.n)) % pub.n
    blinded_bytes = blinded.to_bytes((blinded.bit_length() + 7) // 8, "big") or b"\x00"
    return blinded_bytes, r

def sign_blinded_hash(private_pem_text: str, blinded_hash_bytes: bytes) -> bytes:
    """
    La autoridad firma el hash cegado: s_blind = (m_blind)^d mod n
    """
    priv = _load_rsa_private_for_blind(private_pem_text)
    m_blind = int.from_bytes(blinded_hash_bytes, "big")
    s_blind = pow(m_blind, priv.d, priv.n)
    return s_blind.to_bytes((priv.n.bit_length() + 7) // 8, "big") or b"\x00"

def unblind_signature(s_blind_bytes: bytes, r: int, public_pem_text: str) -> bytes:
    """
    Descegado: s = s_blind * r^{-1} mod n
    """
    pub = _load_rsa_public_for_blind(public_pem_text)
    s_blind = int.from_bytes(s_blind_bytes, "big")
    r_inv = rsa.common.inverse(r, pub.n)
    s = (s_blind * r_inv) % pub.n
    return s.to_bytes((s.bit_length() + 7) // 8, "big") or b"\x00"

def verify_anonymous_signature(public_pem_text: str, hashed_hex: str, signature_bytes: bytes) -> bool:
    """
    Verifica la firma anónima comparando m == sig^e mod n sobre los BYTES del hash.
    """
    try:
        pub = _load_rsa_public_for_blind(public_pem_text)
        sig_int = int.from_bytes(signature_bytes, "big")
        m_recovered = pow(sig_int, pub.e, pub.n)
        # Normalizar a bytes y comparar con el hash original (en bytes)
        m_bytes = m_recovered.to_bytes((m_recovered.bit_length() + 7) // 8, "big")
        # Atender ceros a la izquierda: comparar como hex
        return m_bytes.hex().lstrip("0") == bytes.fromhex(hashed_hex).hex().lstrip("0")
    except Exception as e:
        print(f"Error de verificación anónima: {e}")
        return False
