# server_chunk.py – parçaları topla, sırala, çöz (AES-CBC şifreli)

import socket
import struct
import hashlib
from pathlib import Path
from Crypto.Cipher import AES

# —————————— AYARLAR ——————————
HOST = "0.0.0.0"
PORT = 5050
CHUNK_SIZE = 8 * 1024
KEY = Path("../client/key.bin").read_bytes()
IV  = Path("../client/iv.bin").read_bytes()
OUTPUT_FILE = Path("../test_files/received.txt")

# —————————— SHA256 ——————————
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# —————————— BAĞLANTI BEKLE ——————————
with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("[*] Dinleniyor…")
    conn, addr = s.accept()
    print("[+] Bağlandı:", addr)

    with conn:
        total, = struct.unpack("!I", conn.recv(4))
        print("Parça sayısı:", total)
        chunks = [b""] * total

        for _ in range(total):
            hdr = conn.recv(8)
            seq, length = struct.unpack("!II", hdr)
            data = b""
            while len(data) < length:
                data += conn.recv(min(length - len(data), 4096))
            chunks[seq] = data

# —————————— VERİYİ ÇÖZ ——————————
cipher = b"".join(chunks)
plain = AES.new(KEY, AES.MODE_CBC, IV).decrypt(cipher)
plain = plain[:-plain[-1]]  # PKCS-7 padding çıkar

# —————————— DOSYAYA YAZ & ÖZET ——————————
OUTPUT_FILE.write_bytes(plain)
print("[✓] Birleştirme tamam")
print("SHA-256 (plain):", sha256(plain))
