# Python ile Geliştirilen Temel Güvenlikli Dosya Paylaşım Sistemi  
## Şifreleme • Paket Parçalama • Ağ Trafiği Analizi

Bu depo, **AES-256 şifreleme**, **parça-tabanlı aktarım**, **isteğe bağlı ACK mekanizması** ve **paket sertleştirme** özellikleriyle uçtan uca güvenli dosya paylaşımı sunar. Araç; gerçekçi ağ koşullarını (gecikme/kayıp) taklit ederek performans testine, Wireshark/Scapy ile trafiği incelemeye ve eğitim amaçlı kriptografi denemelerine elverişlidir.

---

## 📂 Dizin Yapısı

| Yol | Amaç |
|-----|------|
| **`client/`** | CLI ve Tkinter istemcileri |
| `client/client.py` | Tek seferlik (küçük) dosya aktarımı |
| `client/client_chunk.py` | Parça-tabanlı aktarım |
| `client/client_ack.py` | Parça + ACK temelli güvenilir aktarım |
| `client/client_chunk_ttl.py` | TTL manipülasyonlu ağ testi |
| `client/flask_gui.py` | TK tabanlı butonlu arayüz |
| **`server/`** | Flask API ve yardımcı modüller |
| `server/server.py` | Temel alıcı |
| `server/server_chunk.py` | Parça-birleştiren alıcı |
| `server/server_ack.py` | ACK destekli alıcı |
| `server/crypto.py` | AES-256-CBC/GCM ve PBKDF2 yardımcıları |
| `server/network.py` | IP ID/TTL rastgeleleştirme, pcap kayıt |
| **`run_flask.sh`** | Sunucuyu 0.0.0.0:5050’da ayağa kaldırır |
| **`requirements.txt`** | pycryptodome, scapy, flask, vb. |

---

## 🚀 Hızlı Başlangıç
```bash
git clone https://github.com/Adileakklc/secure-file-share.git
cd secure-file-share
python -m venv .venv && source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

./run_flask.sh                                          # sunucuyu başlat (5050)
python client/client_chunk.py --file örnek.pdf --host 127.0.0.1 --port 5050
# GUI isteyenler için: python client/flask_gui.py
```

---

## 🔑 Temel Özellikler

| Özellik | Açıklama |
|---------|----------|
| **AES-256 + PBKDF2** | Rastgele IV, ≥100 000 iterasyon | 
| **Parça-tabanlı aktarım** | Varsayılan 1 MiB parçalar; kesintiden sonra devam |
| **ACK modu** | Her parça için onay; kayıp parça 3 kez yeniden gönderilir |
| **tc netem testi** | `loss`, `delay`, `corrupt` ile gerçek ağ koşulları |
| **Paket sertleştirme** | Scapy ile IP ID & TTL rastgele + adli etiketler |
| **Wireshark kayıtları** | `.pcapng` dosyaları `logs/` altında otomatik tutulur |
| **TK GUI** | Dosya seçici, ilerleme çubuğu, SHA-256 özeti |

---

## 🧪 Test & Analiz

### Kayıp + Gecikme Senaryosu
```bash
sudo tc qdisc add dev lo root netem loss 5% delay 50ms
python client/client_ack.py --file büyük.iso ...
sudo tc qdisc del dev lo root netem
```
Aktarımı takiben `logs/*.pcapng` dosyasını Wireshark ile açıp  
`tcp.port == 5050 && ip.ttl == 1` filtresiyle düşük-TTL paketlerini inceleyin.

---

## ➕ Gelecek Geliştirme Fikirleri
- **AES-GCM** moduna geçiş (şifre + bütünlük tek adım)  
- **Çoklu soket** ile paralel parça gönderimi  
- **PySide6 arayüz**: modern, karanlık tema, geriye sayım grafikleri  

---

  katkılarınızı bekliyorum!
