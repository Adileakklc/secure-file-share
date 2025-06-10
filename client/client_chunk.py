# client_chunk.py – parçalayıp sırayla yolla (AES-256 şifreli)

import socket
import struct
import hashlib
import time
from pathlib import Path
from Crypto.Cipher import AES

# —————————— AYARLAR ——————————
HOST = "127.0.0.1"
PORT = 5050
FILE = Path("test_files/sample.txt")       # Gönderilecek dosya yolu
CHUNK_SIZE = 8 * 1024                      # 8 KB
KEY = Path("client/key.bin").read_bytes()
IV = Path("client/iv.bin").read_bytes()

# —————————— SHA256 FONKSİYONU ——————————
def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# —————————— ŞİFRELEME ——————————
t0 = time.time()
plain = FILE.read_bytes()
pad_len = 16 - len(plain) % 16
plain += bytes([pad_len]) * pad_len         # PKCS-7 uyumlu dolgu
cipher = AES.new(KEY, AES.MODE_CBC, IV).encrypt(plain)

# —————————— PARÇALAMA ——————————
chunks = [cipher[i:i + CHUNK_SIZE] for i in range(0, len(cipher), CHUNK_SIZE)]
total = len(chunks)

# —————————— AĞA GÖNDERİM ——————————
with socket.socket() as s:
    s.connect((HOST, PORT))
    s.sendall(struct.pack("!I", total))  # Toplam parça sayısı

    for seq, part in enumerate(chunks):
        s.sendall(struct.pack("!II", seq, len(part)))  # Başlık
        s.sendall(part)                                # Veri

# —————————— BİLGİLENDİRME ——————————
print(f"[✓] {total} parça gönderildi")
print("SHA-256 (plain):", sha256_of_file(FILE))
print("Geçen süre:", round(time.time() - t0, 3), "sn")
