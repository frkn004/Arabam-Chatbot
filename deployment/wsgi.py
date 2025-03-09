import sys
import os

# Uygulama dizinini sys.path'e ekle
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

# .env dosyasını yükle
from dotenv import load_dotenv
load_dotenv()

# Flask uygulamasını içe aktar
from app import app as application

# WSGI uygulaması
if __name__ == "__main__":
    application.run() 