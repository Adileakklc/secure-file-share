#!/bin/bash

echo "🌐 Flask sunucusu başlatılıyor..."
cd client

# Eğer FLASK_APP tanımlı değilse, burada tanımlanır:
export FLASK_APP=flask_gui.py

# Geliştirici modu (otomatik yeniden başlatma)
export FLASK_ENV=development

# Sunucuyu başlat
flask run --host=127.0.0.1 --port=5000
