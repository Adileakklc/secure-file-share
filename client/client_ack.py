import socket
import struct
import hashlib
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from datetime import datetime

# === Ayarlar ===
HOST = '127.0.0.1'
PORT = 5050
CHUNK_SIZE = 8192

# === Anahtar üretimi (PBKDF2) ===
password = input("Parolanızı girin: ").encode()
salt = b'salty_salt'
key = PBKDF2(password, salt, dkLen=32, count=100000)
iv = os.urandom(16)

# === Dosya yolları ===
BASE_DIR = Path(__file__).resolve().parent.parent
sample_path = BASE_DIR / "test_files" / "sample.txt"
logs_dir = Path(__file__).resolve().parent / "logs"
logs_dir.mkdir(exist_ok=True)  # klasör yoksa oluştur
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"log_{timestamp}.csv"

# === Sunucuya bağlan ve IV gönder ===
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(struct.pack("<I", len(iv)))
    s.sendall(iv)

    with sample_path.open("rb") as f, log_file.open("w") as log:
        index = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            padded_chunk = pad(chunk, AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(padded_chunk)
            data_len = len(cipher)
            header = struct.pack("<II", index, data_len)
            packet = header + cipher

            ack_received = False
            for attempt in range(3):
                try:
                    s.sendall(packet)
                    s.settimeout(2.0)
                    ack_data = s.recv(4)
                    ack_index = struct.unpack("<I", ack_data)[0]
                    if ack_index == index:
                        print(f"[✓] Parça {index} onaylandı.")
                        ack_received = True
                        log.write(f"{index},{data_len},OK\n")
                        break
                except socket.timeout:
                    print(f"[!] Parça {index} için ACK beklenmedi! Deneme {attempt + 1}")
                except Exception as e:
                    print(f"[!] Parça {index} için hata oluştu: {e}")
                    break

            if not ack_received:
                print(f"[X] Parça {index} gönderilemedi. Bağlantı kesiliyor.")
                log.write(f"{index},{data_len},FAIL\n")
                break

            index += 1

# === SHA-256 Özeti ===
with sample_path.open("rb") as f:
    hash_plain = hashlib.sha256(f.read()).hexdigest()
print("SHA-256 (plain):", hash_plain)
