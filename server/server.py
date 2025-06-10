# server.py – Tek seferlik şifreli veri alımı ve çözme (AES-CBC)

import socket
import struct
import hashlib
from pathlib import Path
from Crypto.Cipher import AES

# —————————— AYARLAR ——————————
HOST = "0.0.0.0"
PORT = 5050
KEY = Path("../client/key.bin").read_bytes()
IV = Path("../client/iv.bin").read_bytes()
OUTPUT_FILE = Path("../test_files/received.txt")

# —————————— SHA256 ——————————
def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# —————————— BAĞLANTIYI DİNLE ——————————
with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("[*] Dinleniyor…")
    conn, addr = s.accept()
    print("[+] Bağlandı:", addr)

    with conn:
        # İlk 4 baytı al (şifreli veri uzunluğu)
        size_bytes = conn.recv(4)
        if len(size_bytes) < 4:
            print("[-] Uzunluk bilgisi eksik alındı.")
            exit(1)

        size = struct.unpack("!I", size_bytes)[0]
        print(f"[*] Şifreli veri boyutu: {size} bayt")

        # Şifreli veriyi al
        data = b""
        while len(data) < size:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk

# —————————— ŞİFRE ÇÖZME ——————————
cipher = AES.new(KEY, AES.MODE_CBC, IV)
plain = cipher.decrypt(data)

# PKCS-7 dolgu çıkar
pad_len = plain[-1]
plain = plain[:-pad_len]

# —————————— KAYDET & SHA-256 ——————————
OUTPUT_FILE.write_bytes(plain)
print("[✓] Çözüm tamam")
print("SHA-256 (plain):", sha256(plain))
