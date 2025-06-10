# client.py – AES-CBC ile şifreli aktarım (tek parça TCP)

import socket
import struct
import hashlib
from pathlib import Path
from Crypto.Cipher import AES

# —————————— AYARLAR ——————————
HOST = "127.0.0.1"
PORT = 5050
FILE = Path("test_files/sample.txt")            # Gönderilecek dosya
KEY  = Path("client/key.bin").read_bytes()
IV   = Path("client/iv.bin").read_bytes()

# —————————— SHA256 FONKSİYONU ——————————
def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# —————————— VERİYİ OKU VE ŞİFRELE ——————————
plain = FILE.read_bytes()
pad_len = 16 - len(plain) % 16
plain += bytes([pad_len]) * pad_len             # PKCS-7 uyumlu dolgu

cipher = AES.new(KEY, AES.MODE_CBC, IV)
ciphertext = cipher.encrypt(plain)

# —————————— AĞ ÜZERİNDEN GÖNDER ——————————
with socket.socket() as s:
    s.connect((HOST, PORT))
    s.sendall(struct.pack("!I", len(ciphertext)))  # Uzunluk (4 bayt)
    s.sendall(ciphertext)                          # Verinin tamamı

# —————————— SONUÇ ——————————
print("[✓] Gönderim tamam")
print("SHA-256 (plain):", sha256_of_file(FILE))
