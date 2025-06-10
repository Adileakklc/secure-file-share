import socket
import struct
import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Protocol.KDF import PBKDF2

# —————————— AYARLAR ——————————
HOST = '127.0.0.1'
PORT = 5050
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "test_files" / "received.txt"

# —————————— YARDIMCI FONKSİYON ——————————
def recv_exact(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

# —————————— BAĞLANTIYI DİNLE ——————————
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("[*] Dinleniyor...")
    conn, addr = s.accept()
    with conn:
        print("[+] Bağlandı:", addr)
        password = input("Parolanızı girin (aynı olmalı): ").encode()
        salt = b'salty_salt'
        key = PBKDF2(password, salt, dkLen=32, count=100000)

        # IV alma
        iv_len_data = conn.recv(4)
        iv_len = struct.unpack("<I", iv_len_data)[0]
        iv = conn.recv(iv_len)

        with OUTPUT_FILE.open("wb") as f:
            while True:
                header = conn.recv(8)
                if not header:
                    print("[*] Tüm parçalar başarıyla alındı, bağlantı kapatıldı.")
                    break

                index, data_len = struct.unpack("<II", header)
                cipher = recv_exact(conn, data_len)
                if cipher is None:
                    print(f"[X] Parça {index} eksik alındı, bağlantı kesildi.")
                    break

                plain = AES.new(key, AES.MODE_CBC, iv).decrypt(cipher)
                try:
                    plain = unpad(plain, AES.block_size)
                except ValueError:
                    pass  # dolgu hatası olabilir, göz ardı et
                f.write(plain)
                conn.sendall(struct.pack("<I", index))
                print(f"[✓] Parça {index} alındı, ACK gönderildi.")

# —————————— SHA-256 Doğrulama ——————————
hash_plain = hashlib.sha256(OUTPUT_FILE.read_bytes()).hexdigest()
print("SHA-256 (plain):", hash_plain)
