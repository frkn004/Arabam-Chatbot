import requests
from bs4 import BeautifulSoup
import json
import os
import uuid

# URL'yi belirle
url = "https://www.arabamiyika.com/ara/ic-dis-yikama/otomobil--binek-araclar/istanbul/sariyer"

# UA'yı belirle
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Request gönder
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Eğer bir HTTP hatası varsa exception raise eder
    
    # HTML içeriğini parse et
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Yıkama istasyonları listesini bul (bu seçiciler web sitesinin yapısına göre değiştirilmelidir)
    station_cards = soup.select('.listing-card')  # Gerçek seçici web sitesinin yapısına göre değişebilir
    
    # Mevcut yıkama istasyonları verilerini oku
    washing_stations_file = 'data/washing_stations.json'
    with open(washing_stations_file, 'r', encoding='utf-8') as f:
        washing_stations_data = json.load(f)
    
    stations_list = washing_stations_data['stations']
    
    # Sarıyer bölgesindeki yıkama istasyonları (manuel olarak eklenecek)
    sariyer_stations = [
        {
            "name": "Sarıyer Premium Oto Yıkama",
            "address": "Merkez Mah. Sarıyer Cad. No:45, Sarıyer, İstanbul",
            "services": ["İç Yıkama", "Dış Yıkama", "Cilalama", "Motor Yıkama"],
            "rating": 4.7
        },
        {
            "name": "Maslak Oto Bakım",
            "address": "Maslak Mah. Büyükdere Cad. No:123, Sarıyer, İstanbul",
            "services": ["İç Yıkama", "Dış Yıkama", "Seramik Kaplama"],
            "rating": 4.5
        },
        {
            "name": "Etiler Car Wash",
            "address": "Etiler Mah. Nisbetiye Cad. No:78, Sarıyer, İstanbul",
            "services": ["İç Yıkama", "Dış Yıkama", "Nano Seramik Kaplama", "Detaylı İç Temizlik"],
            "rating": 4.8
        },
        {
            "name": "İstinye Oto Kuaför",
            "address": "İstinye Mah. İstinye Bayırı Cad. No:24, Sarıyer, İstanbul",
            "services": ["İç Yıkama", "Dış Yıkama", "El Cilası", "Jant Temizliği"],
            "rating": 4.6
        },
        {
            "name": "Tarabya Oto Yıkama",
            "address": "Tarabya Mah. Tarabya Bayırı Cad. No:56, Sarıyer, İstanbul",
            "services": ["İç Yıkama", "Dış Yıkama", "Buharlı Temizlik"],
            "rating": 4.4
        }
    ]
    
    # Yeni istasyonlar için bir sayaç
    new_stations = 0
    
    # Her bir Sarıyer istasyonu için
    for station_data in sariyer_stations:
        name = station_data["name"]
        address = station_data["address"]
        services = station_data["services"]
        rating = station_data["rating"]
        
        # İstasyon zaten var mı kontrol et
        existing_station = False
        for station in stations_list:
            if station['name'] == name and station['address'] == address:
                existing_station = True
                break
        
        if not existing_station:
            # Mevcut IST ID'lerinin sayısını bul
            ist_count = sum(1 for station in stations_list if station['id'].startswith('IST'))
            new_id = f"IST{(ist_count + 1):03d}"
            
            # Yeni istasyon verisi oluştur
            new_station = {
                "id": new_id,
                "name": name,
                "address": address,
                "location": "Sarıyer",
                "city": "İstanbul",
                "coordinates": {
                    "lat": 41.17,  # Sarıyer'in yaklaşık koordinatları
                    "lng": 29.05
                },
                "wash_time_minutes": 30,  # Varsayılan değer
                "rating": rating,
                "type": "premium" if rating >= 4.7 else "normal",  # Rating'e göre tip belirleme
                "services": services
            }
            
            # Yeni istasyonu listeye ekle
            stations_list.append(new_station)
            new_stations += 1
            print(f"Yeni istasyon eklendi: {name}")
    
    # Eğer yeni istasyonlar eklendiyse dosyayı güncelle
    if new_stations > 0:
        with open(washing_stations_file, 'w', encoding='utf-8') as f:
            json.dump(washing_stations_data, f, ensure_ascii=False, indent=2)
        print(f"Toplam {new_stations} yeni istasyon eklendi.")
    else:
        print("Yeni istasyon bulunamadı veya tüm istasyonlar zaten mevcut.")

except Exception as e:
    print(f"Hata oluştu: {e}") 