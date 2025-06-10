# client_chunk_ttl.py – TTL=32 IP paketleriyle şifreli parça gönderimi
from pathlib import Path
import struct
import hashlib
import time
from Crypto.Cipher import AES
from scapy.all import IP, TCP, send

# —————————— AYARLAR ——————————
HOST = "127.0.0.1"
PORT = 5050
FILE = Path("test_files/sample.txt")  # gönderilecek dosya yolu
CHUNK_SIZE = 8 * 1024                 # 8 KB
TTL_VALUE = 32                        # sabit TTL değeri

# —————————— ŞİFRELEME ——————————
key = Path("client/key.bin").read_bytes()
iv  = Path("client/iv.bin").read_bytes()

plain = FILE.read_bytes()
pad = 16 - len(plain) % 16
plain += bytes([pad]) * pad  # PKCS-7 benzeri dolgu

cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(plain)

# —————————— PARÇALAMA ——————————
chunks = [cipher[i: i + CHUNK_SIZE] for i in range(0, len(cipher), CHUNK_SIZE)]
total = len(chunks)

# —————————— KONTROL PAKETİ (toplam parça sayısı) ——————————
ctrl = IP(dst=HOST, ttl=TTL_VALUE) / TCP(dport=PORT) / struct.pack("!I", total)
send(ctrl, verbose=False)

# —————————— VERİ PARÇALARINI GÖNDER ——————————
for seq, part in enumerate(chunks):
    header = struct.pack("!II", seq, len(part))
    payload = header + part
    pkt = IP(dst=HOST, ttl=TTL_VALUE) / TCP(dport=PORT) / payload
    send(pkt, verbose=False)

# —————————— TAMAMLAMA BİLGİLERİ ——————————
print(f"[✓] {total} parça yollandı")
print("SHA-256 (plain):", hashlib.sha256(FILE.read_bytes()).hexdigest())
print("Geçen süre:", round(time.time() - time.time() + t0, 3), "sn")
