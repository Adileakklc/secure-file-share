from flask import Flask, render_template, request, redirect, flash
from pathlib import Path
import socket, struct, hashlib, os
from Crypto.Cipher import AES
from datetime import datetime

app = Flask(__name__)
app.secret_key = "guvenli-dosya-aktarimi"

# —————————— AYARLAR ——————————
HOST = "127.0.0.1"
PORT = 5050
KEY_PATH = Path("key.bin")
IV_PATH = Path("iv.bin")
UPLOAD_DIR = Path("test_files")
RECEIVED_FILE = Path("../test_files/received.txt")
SHA_LOG = Path("logs/sha_mismatch.log")
UPLOAD_DIR.mkdir(exist_ok=True)
SHA_LOG.parent.mkdir(exist_ok=True)  # logs/ klasörü yoksa oluştur

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dosya = request.files['dosya']
        if not dosya:
            flash("❌ Dosya seçilmedi.", "danger")
            return redirect('/')

        # Dosyayı geçici olarak kaydet
        temp_path = UPLOAD_DIR / "temp_upload.txt"
        dosya.save(temp_path)

        # Dosya içeriğini oku ve SHA hesapla
        plain = temp_path.read_bytes()
        sha_gonderilen = hashlib.sha256(plain).hexdigest()

        # PKCS-7 padding
        pad_len = 16 - len(plain) % 16
        plain += bytes([pad_len]) * pad_len

        # AES şifreleme
        key = KEY_PATH.read_bytes()
        iv = IV_PATH.read_bytes()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(plain)

        try:
            # Sunucuya gönder
            with socket.socket() as s:
                s.connect((HOST, PORT))
                s.sendall(struct.pack("!I", len(ciphertext)))
                s.sendall(ciphertext)

            # SHA eşleşmesi kontrolü
            if RECEIVED_FILE.exists():
                sha_alici = hashlib.sha256(RECEIVED_FILE.read_bytes()).hexdigest()
                if sha_alici == sha_gonderilen:
                    flash(f"✅ Dosya başarıyla gönderildi! SHA-256 eşleşti.", "success")
                    flash(f"Gönderilen SHA: {sha_gonderilen}", "secondary")
                else:
                    flash(f"⚠️ Gönderim tamamlandı ancak SHA-256 eşleşmedi!", "warning")
                    flash(f"Gönderilen SHA: {sha_gonderilen}", "secondary")
                    flash(f"Alınan SHA   : {sha_alici}", "secondary")

                    # 🔐 SHA uyuşmazlık logu
                    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with SHA_LOG.open("a", encoding="utf-8") as f:
                        f.write(f"Tarih: {zaman}, SHA eşleşmedi\n")

            else:
                flash("❌ Gönderim yapıldı ancak sunucu çıktısı bulunamadı (received.txt yok).", "danger")

        except Exception as e:
            flash(f"❌ Gönderim hatası: {str(e)}", "danger")

        # Temp dosyayı sil
        temp_path.unlink(missing_ok=True)
        return redirect('/')

    return render_template('index.html')
