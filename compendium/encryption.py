import base64
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_key(salt: str, password: str) -> bytes:
    # From: https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#nist
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode("utf-8"),
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def verify_file(key: bytes, infile: Path, outfile: Path):
    decrypted = read_decrypted(key, outfile)
    plaintext = infile.open('rb').read()
    return decrypted == plaintext


def read_decrypted(key: bytes, file: Path):
    fernet = Fernet(key)
    ciphertext = file.open('rb').read()
    return fernet.decrypt(ciphertext)


def decrypt_file(key: bytes, infile: Path, outfile: Path):
    """Decrypt infile and save as outfile"""
    plaintext = read_decrypted(key, infile)
    outfile.open('wb').write(plaintext)


def encrypt_file(key: bytes, infile: Path, outfile: Path):
    """Encrypt infile and save as outfile"""
    fernet = Fernet(key)
    plaintext = infile.open('rb').read()
    ciphertext = fernet.encrypt(plaintext)
    outfile.open('wb').write(ciphertext)
