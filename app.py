from flask import Flask, render_template, request, jsonify
import os
import json
import math
from dotenv import load_dotenv
import openai
import glob
from datetime import datetime

# .env dosyasını yükle
load_dotenv()

# OpenAI API anahtarını ayarla
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Kullanıcı bilgilerini dosyadan oku
def read_user_data(user_code):
    try:
        with open(f'data/users/{user_code}.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Kullanıcı bilgilerini güncelle
def update_user_data(user_code, user_data):
    try:
        with open(f'data/users/{user_code}.json', 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Kullanıcı bilgisi güncellenirken hata oluştu: {e}")
        return False

# Yeni kullanıcı oluştur
def create_new_user(user_info):
    # Yeni kullanıcı kodu oluştur
    existing_codes = [os.path.basename(f).split('.')[0] for f in glob.glob('data/users/*.json')]
    
    # Örnek: BMW kullanıcıları için BMW kodu, diğerleri için USR kodu
    if "bmw" in user_info.get('car_info', {}).get('model', '').lower():
        prefix = "BMW"
    else:
        prefix = "USR"
    
    # Yeni kod numarası
    code_number = 1
    while f"{prefix}{code_number:03d}" in existing_codes:
        code_number += 1
    
    user_code = f"{prefix}{code_number:03d}"
    
    # Kullanıcı şablonu oluştur
    user_data = {
        "user_id": user_code,
        "personal_info": {
            "name": user_info.get('name', ''),
            "surname": user_info.get('surname', ''),
            "email": user_info.get('email', ''),
            "phone": user_info.get('phone', '')
        },
        "car_info": {
            "model": user_info.get('car_model', ''),
            "year": user_info.get('car_year', 2023),
            "plate": user_info.get('plate', ''),
            "color": user_info.get('car_color', '')
        },
        "membership": {
            "type": "Standart",
            "remaining_washes": 0,
            "start_date": "",
            "end_date": ""
        },
        "wash_history": [],
        "favorite_locations": [],
        "last_known_location": {
            "city": "",
            "district": "",
            "coordinates": {
                "lat": 0,
                "lng": 0
            }
        }
    }
    
    # Kullanıcı bilgisini kaydet
    update_user_data(user_code, user_data)
    
    return user_code, user_data

# JSON dosyasını okuma fonksiyonu (eski, geri uyumluluk için)
def read_users_data():
    try:
        with open('data/users.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Dosya yoksa veya bozuksa boş bir veri yapısı döndür
        return {"users": []}

# JSON dosyasını güncelleme fonksiyonu (eski, geri uyumluluk için)
def update_users_data(data):
    try:
        with open('data/users.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"JSON dosyası güncellenirken hata oluştu: {e}")
        return False

# Yıkama istasyonlarını oku
def read_stations_data():
    try:
        with open('data/washing_stations.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Dosya yoksa veya bozuksa, örnek veri döndür
        return {
            "stations": [
                {
                    "id": "ANK001",
                    "name": "Atakule Oto Yıkama",
                    "type": "premium",
                    "city": "Ankara",
                    "location": "Çankaya",
                    "address": "Çankaya Kızılırmak Mah. No:12, Atakule, Ankara",
                    "coordinates": {
                        "lat": 39.8837,
                        "lng": 32.8597
                    },
                    "rating": 4.6,
                    "wash_time_minutes": 30,
                    "services": ["İç Yıkama", "Dış Yıkama", "Cilalama"]
                },
                {
                    "id": "ANK002",
                    "name": "Çankaya Premium Oto Bakım",
                    "type": "premium",
                    "city": "Ankara",
                    "location": "Çankaya",
                    "address": "Çankaya Cad. No:45, Çankaya, Ankara",
                    "coordinates": {
                        "lat": 39.9031,
                        "lng": 32.8041
                    },
                    "rating": 4.9,
                    "wash_time_minutes": 40,
                    "services": ["İç Yıkama", "Dış Yıkama", "Cilalama", "Motor Yıkama", "Koltuk Temizliği"]
                },
                {
                    "id": "ANK003",
                    "name": "Kızılay Oto Bakım",
                    "type": "normal",
                    "city": "Ankara",
                    "location": "Çankaya",
                    "address": "Kızılay Mah. Ziya Gökalp Cad. No:7, Çankaya, Ankara",
                    "coordinates": {
                        "lat": 39.9487,
                        "lng": 32.8361
                    },
                    "rating": 4.3,
                    "wash_time_minutes": 25,
                    "services": ["İç Yıkama", "Dış Yıkama"]
                },
                {
                    "id": "IST001",
                    "name": "Kadıköy Oto Yıkama",
                    "type": "premium",
                    "city": "İstanbul",
                    "location": "Kadıköy",
                    "address": "Caferağa Mah. Moda Cad. No:22, Kadıköy, İstanbul",
                    "coordinates": {
                        "lat": 40.9901,
                        "lng": 29.0253
                    },
                    "rating": 4.7,
                    "wash_time_minutes": 35,
                    "services": ["İç Yıkama", "Dış Yıkama", "Cilalama", "Dezenfeksiyon"]
                },
                {
                    "id": "IST002",
                    "name": "Beşiktaş Premium Oto Bakım",
                    "type": "premium",
                    "city": "İstanbul",
                    "location": "Beşiktaş",
                    "address": "Sinanpaşa Mah. Şehit Asım Cad. No:23, Beşiktaş, İstanbul",
                    "coordinates": {
                        "lat": 41.0419,
                        "lng": 29.0083
                    },
                    "rating": 4.8,
                    "wash_time_minutes": 45,
                    "services": ["İç Yıkama", "Dış Yıkama", "Cilalama", "Motor Yıkama", "Koltuk Temizliği"]
                },
                {
                    "id": "IST003",
                    "name": "Üsküdar Oto Kuaför",
                    "type": "normal",
                    "city": "İstanbul",
                    "location": "Üsküdar",
                    "address": "Mimar Sinan Mah. Hakimiyet Cad. No:35, Üsküdar, İstanbul",
                    "coordinates": {
                        "lat": 41.0264,
                        "lng": 29.0149
                    },
                    "rating": 4.5,
                    "wash_time_minutes": 30,
                    "services": ["İç Yıkama", "Dış Yıkama", "Cilalama"]
                }
            ]
        }

# İki konum arasındaki mesafeyi hesapla (Haversine formülü)
def calculate_distance(lat1, lon1, lat2, lon2):
    # Dünya yarıçapı (km)
    R = 6371.0
    
    # Radyana çevir
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Enlem ve boylam farkları
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formülü
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Mesafe (km)
    distance = R * c
    
    return round(distance, 2)

# En iyi istasyonu öner
def recommend_best_station(nearby_stations):
    if not nearby_stations:
        return None
    
    # Puanı yüksek olan istasyonlar
    high_rated = [s for s in nearby_stations if s['rating'] >= 4.5]
    
    if high_rated:
        # Premium servisi olan ve puanı yüksek istasyonlar
        premium_high_rated = [s for s in high_rated if s['type'] == 'premium']
        if premium_high_rated:
            # En yakın premium ve yüksek puanlı istasyon
            return min(premium_high_rated, key=lambda x: x['distance'])
        # En yakın yüksek puanlı istasyon
        return min(high_rated, key=lambda x: x['distance'])
    
    # Sadece mesafeye göre en yakın istasyonu öner
    return min(nearby_stations, key=lambda x: x['distance'])

# Belirli bir konum için en yakın istasyonları bul
def find_nearby_stations(location_info, limit=3, max_distance=20, exclude_stations=None, alternative_search=False):
    stations_data = read_stations_data()
    
    # Debug için log
    # print(f"DEBUG: Finding nearby stations for location: {location_info}")
    # print(f"DEBUG: Available stations: {len(stations_data.get('stations', []))}")
    
    # Kullanıcının konumu
    user_lat = location_info.get('coordinates', {}).get('lat', 0)
    user_lng = location_info.get('coordinates', {}).get('lng', 0)
    
    # Kullanıcı şehri/semti
    user_city = location_info.get('city', '').lower()
    user_district = location_info.get('district', '').lower()
    
    # Debug
    # print(f"DEBUG: User city: {user_city}, district: {user_district}")
    
    nearby_stations = []
    all_matching_stations = []  # Şehir eşleşmesi olan tüm istasyonlar
    
    # Önce tüm eşleşen istasyonları topla
    for station in stations_data.get('stations', []):
        # Şehir veya semt eşleşmesi varsa
        station_city = station.get('city', '').lower()
        station_location = station.get('location', '').lower()
        
        # Debug
        # print(f"DEBUG: Checking station: {station.get('name')} in {station_city}, {station_location}")
        
        # Hariç tutulacak istasyonları atla
        if exclude_stations and station.get('id') in exclude_stations:
            continue
        
        # Şehir eşleşmesi kontrolü - daha geniş eşleşme için contains kullan
        city_match = user_city and (user_city in station_city or station_city in user_city)
        
        if city_match:
            # Debug
            # print(f"DEBUG: City match found for station: {station.get('name')}")
            
            station_lat = station.get('coordinates', {}).get('lat', 0)
            station_lng = station.get('coordinates', {}).get('lng', 0)
            
            # Mesafeyi hesapla
            distance = calculate_distance(user_lat, user_lng, station_lat, station_lng)
            
            station_with_distance = station.copy()
            station_with_distance['distance'] = distance
            all_matching_stations.append(station_with_distance)
            
            # Eğer ayrıca semt eşleşmesi de varsa veya alternatif arama değilse ve mesafe uygunsa
            district_match = user_district and (user_district in station_location or station_location in user_district)
            
            if (district_match or not alternative_search) and distance <= max_distance:
                nearby_stations.append(station_with_distance)
    
    # Debug
    # print(f"DEBUG: Found {len(nearby_stations)} nearby stations")
    # print(f"DEBUG: Found {len(all_matching_stations)} total matching stations")
    
    # Mesafeye göre sırala
    nearby_stations.sort(key=lambda x: x.get('distance', float('inf')))
    
    # Eğer hiç istasyon bulunamazsa veya alternatif arama isteniyorsa
    if not nearby_stations or alternative_search:
        # Tüm şehir içindeki istasyonları al, en yakına göre değil farklı semtlerden al
        if alternative_search and all_matching_stations:
            # Mesafeye göre değil, farklı semtleri önceliklendirerek sırala
            all_matching_stations.sort(key=lambda x: (x.get('location', '').lower() == user_district.lower(), x.get('distance', float('inf'))))
            # Alternatif aramada, mesafeyi ikinci planda tut
            return all_matching_stations[:limit]
        
        # Arama mesafesini genişlet
        elif max_distance < 50:
            return find_nearby_stations(location_info, limit=limit, max_distance=max_distance+20, exclude_stations=exclude_stations)
        
        # Yine de bulamazsa dummy veri döndür
        if not nearby_stations and not all_matching_stations:
            # Debug - kontrol için
            # print(f"DEBUG: Using dummy data for {user_city}")
            
            dummy_data = []
            if "istanbul" in user_city:
                dummy_data = [
                    {
                        "id": "IST001",
                        "name": "Kadıköy Oto Yıkama",
                        "type": "premium",
                        "city": "İstanbul",
                        "location": "Kadıköy",
                        "address": "Caferağa Mah. Moda Cad. No:22, Kadıköy, İstanbul",
                        "coordinates": {
                            "lat": 40.9901,
                            "lng": 29.0253
                        },
                        "rating": 4.7,
                        "distance": 0.5,
                        "wash_time_minutes": 35,
                        "services": ["İç Yıkama", "Dış Yıkama", "Cilalama", "Dezenfeksiyon"]
                    }
                ]
                if "kadıköy" in user_district:
                    dummy_data[0]["distance"] = 0.1  # Çok yakın göster
                return dummy_data
    
    # Belirtilen sayıda istasyon döndür
    return nearby_stations[:limit]

# Popüler yerler ve konumları
popular_places = {
    "kentpark": {"city": "Ankara", "district": "Çankaya", "coordinates": {"lat": 39.903, "lng": 32.8059}},
    "kentpark avm": {"city": "Ankara", "district": "Çankaya", "coordinates": {"lat": 39.903, "lng": 32.8059}},
    "armada": {"city": "Ankara", "district": "Söğütözü", "coordinates": {"lat": 39.9175, "lng": 32.8048}},
    "armada avm": {"city": "Ankara", "district": "Söğütözü", "coordinates": {"lat": 39.9175, "lng": 32.8048}},
    "ankamall": {"city": "Ankara", "district": "Akköprü", "coordinates": {"lat": 39.9487, "lng": 32.8361}},
    "ankamall avm": {"city": "Ankara", "district": "Akköprü", "coordinates": {"lat": 39.9487, "lng": 32.8361}},
    "cepa": {"city": "Ankara", "district": "Çankaya", "coordinates": {"lat": 39.9031, "lng": 32.8041}},
    "cepa avm": {"city": "Ankara", "district": "Çankaya", "coordinates": {"lat": 39.9031, "lng": 32.8041}},
    "atakule": {"city": "Ankara", "district": "Çankaya", "coordinates": {"lat": 39.8837, "lng": 32.8597}},
    "forum istanbul": {"city": "İstanbul", "district": "Bayrampaşa", "coordinates": {"lat": 41.0183, "lng": 28.9095}},
    "kanyon": {"city": "İstanbul", "district": "Levent", "coordinates": {"lat": 41.0804, "lng": 29.0091}},
    "zorlu center": {"city": "İstanbul", "district": "Zincirlikuyu", "coordinates": {"lat": 41.0672, "lng": 29.0105}},
    "istinye park": {"city": "İstanbul", "district": "Sarıyer", "coordinates": {"lat": 41.1114, "lng": 29.0303}},
    "metrocity": {"city": "İstanbul", "district": "Levent", "coordinates": {"lat": 41.0774, "lng": 29.0123}},
    "akasya avm": {"city": "İstanbul", "district": "Üsküdar", "coordinates": {"lat": 41.0018, "lng": 29.0565}},
    "emaar square": {"city": "İstanbul", "district": "Üsküdar", "coordinates": {"lat": 41.0047, "lng": 29.0567}}
}

# Konum bilgisini analiz et
def analyze_location(location_text):
    """Kullanıcının gönderdiği konum bilgisini analiz eder"""
    print(f"Analyzing location: {location_text}")
    
    # Parse_location fonksiyonunu kullan
    location_info = parse_location(location_text)
    
    if location_info:
        print(f"Location parsed: {location_info}")
        return location_info
    
    # Konum bulunamadıysa, basit bir analiz yap
    location_text = location_text.lower()
    
    # Şehir ve ilçe analizi
    city = None
    district = None
    
    # Şehir kontrolü
    if "istanbul" in location_text:
        city = "İstanbul"
    elif "ankara" in location_text:
        city = "Ankara"
    elif "izmir" in location_text:
        city = "İzmir"
        
    # İlçe kontrolü
    if "kadıköy" in location_text or "kadikoy" in location_text:
        district = "Kadıköy"
        city = "İstanbul"
    elif "şişli" in location_text or "sisli" in location_text:
        district = "Şişli"
        city = "İstanbul"
    elif "beşiktaş" in location_text or "besiktas" in location_text:
        district = "Beşiktaş"
        city = "İstanbul"
    elif "ataşehir" in location_text or "atasehir" in location_text:
        district = "Ataşehir"
        city = "İstanbul"
    elif "üsküdar" in location_text or "uskudar" in location_text:
        district = "Üsküdar"
        city = "İstanbul"
    elif "çankaya" in location_text or "cankaya" in location_text:
        district = "Çankaya"
        city = "Ankara"
    elif "kızılay" in location_text or "kizilay" in location_text:
        district = "Kızılay"
        city = "Ankara"
    elif "kentpark" in location_text:
        district = "Çankaya"
        city = "Ankara"
    
    # Koordinat bilgileri
    coordinates = {
        "İstanbul": {"lat": 41.0082, "lng": 28.9784},
        "Ankara": {"lat": 39.9334, "lng": 32.8597},
        "İzmir": {"lat": 38.4192, "lng": 27.1287},
        "Kadıköy": {"lat": 40.9928, "lng": 29.0265},
        "Beşiktaş": {"lat": 41.0422, "lng": 29.0093},
        "Şişli": {"lat": 41.0630, "lng": 28.9916},
        "Ataşehir": {"lat": 40.9923, "lng": 29.1244},
        "Üsküdar": {"lat": 41.0212, "lng": 29.0547},
        "Çankaya": {"lat": 39.9030, "lng": 32.8059}
    }
    
    # Bir konum bulunamadıysa null dön
    if not city and not district:
        return None
    
    # Koordinat bilgisi
    coords = None
    if district and district in coordinates:
        coords = coordinates[district]
    elif city and city in coordinates:
        coords = coordinates[city]
    else:
        coords = {"lat": 0, "lng": 0}
    
    # Sonucu döndür
    result = {
        "city": city,
        "district": district if district else "",
        "coordinates": coords
    }
    
    return result

# Belirli bir tarih için istasyon bazlı dolu saatleri kontrol eden fonksiyon
def get_station_specific_booked_times(date_str, station_name):
    """Belirli bir tarihte ve istasyonda dolu saatleri belirler"""
    # Tarihten ve istasyon adından bir seed oluştur
    date_seed = sum(ord(c) for c in date_str)
    station_seed = sum(ord(c) for c in station_name)
    combined_seed = date_seed * station_seed
    
    # Dolu saatler listesi
    booked_times = []
    
    # Olası tüm saatler
    all_times = [f"{hour:02d}:{minute:02d}" for hour in range(8, 19) for minute in [0, 30]]
    
    # Her istasyon için farklı saatleri dolu yap
    for time in all_times:
        hour, minute = map(int, time.split(":"))
        time_seed = (hour * 60 + minute) * combined_seed
        
        # %30 ihtimalle bu saat bu istasyon için dolu olsun
        if (time_seed % 100) < 30:  
            booked_times.append(time)
    
    return booked_times

# Belirli bir tarih ve saatin dolu olup olmadığını kontrol et - garantili olarak çalışacak
def is_time_slot_booked(date_str, time_str, station_name):
    """Belirli bir tarih ve saatin dolu olup olmadığını kontrol eder"""
    try:
        # Parametrelerin boş olup olmadığını kontrol et
        if not date_str or not time_str or not station_name:
            return False
            
        # print(f"DEBUG: Checking is_time_slot_booked - Date: {date_str}, Time: {time_str}, Station: {station_name}")
        
        # Zamanın doğru formatta olduğundan emin ol
        if ':' not in time_str:
            try:
                # Eğer sadece saat sayı olarak verildiyse (örn: 14)
                hour = int(time_str.strip())
                time_str = f"{hour:02d}:00"
            except ValueError:
                # Sayı değilse, varsayılan değeri kullan
                time_str = "12:00"
    
        # İstasyona özel dolu saatleri kontrol et
        station_booked_times = get_station_specific_booked_times(date_str, station_name)
        
        # print(f"DEBUG: Station {station_name} booked times for {date_str}: {station_booked_times}")
        
        # Booked times içinde varsa dolu
        if time_str in station_booked_times:
            # print(f"DEBUG: Time {time_str} is booked for {station_name}")
            return True
            
        # Ayrıca zaman aralığı kontrolleri yapılabilir
        # Örneğin, bir yıkama 30 dakika sürüyorsa, 14:00 dolu ise 14:15 de doludur
        hour, minute = time_str.split(":")
        
        # Normal booklenmiş zamanlarla işiniz bitti, dolu değil
        # print(f"DEBUG: Normal check - slot is NOT booked")
        return False
        
    except Exception as e:
        print(f"DEBUG: Error in is_time_slot_booked: {e}")
        # Herhangi bir hata durumunda varsayılan olarak dolu değil döndür
        return False

# Belirli bir saatte uygun diğer istasyonları bul
def find_alternative_stations_for_time(date_str, time_str, current_station, location_info):
    """Belirli tarih ve saat için müsait alternatif istasyonlar önerir"""
    # Parametrelerin boş olmadığından emin ol
    if not date_str or not time_str or not current_station:
        return []
        
    # Tüm istasyonları oku
    stations_data = read_stations_data()
    nearby_stations = find_nearby_stations(location_info, limit=10, max_distance=30)
    
    # Şu anki istasyonu hariç tut
    alternative_stations = []
    
    for station in nearby_stations:
        # Eğer mevcut istasyonla aynı değilse
        if station.get('id') != current_station.get('id'):
            # Bu istasyon için belirtilen saatte müsait mi kontrol et
            if not is_time_slot_booked(date_str, time_str, station.get('name', '')):
                station_with_time = station.copy()
                station_with_time['time'] = time_str  # Zaman bilgisini kaydet
                alternative_stations.append(station_with_time)
    
    # En fazla 3 alternatif istasyon döndür
    return alternative_stations[:3]

# Belirli bir tarih ve saatte alternatif istasyonları bul (farklı saatleri de içerir)
def find_any_alternative_stations_and_times(date_str, time_str, current_station, location_info):
    """Belirli bir tarih ve saatte istasyon dolu ise, alternatif istasyon ve zamanlar önerir"""
    # Parametrelerin boş olmadığından emin ol
    if not date_str or not time_str or not current_station or not location_info:
        return []
        
    # Tüm istasyonları oku
    stations_data = read_stations_data()
    nearby_stations = find_nearby_stations(location_info, limit=10, max_distance=30)
    
    # Değişik tarih ve saatlerde istasyonlar
    alternatives = []
    
    # İlk olarak aynı saatte farklı istasyonlar ara
    for station in nearby_stations:
        if station.get('id') != current_station.get('id'):
            # Aynı saatte müsait mi kontrol et
            if not is_time_slot_booked(date_str, time_str, station.get('name', '')):
                station_with_time = station.copy()
                station_with_time['time'] = time_str  # Orijinal zamanı koru
                alternatives.append(station_with_time)
    
    # Eğer alternatif bulunamadıysa, farklı saatlere bak
    if not alternatives:
        # Tarih bilgisi - mesela "15 Mayıs 2023"
        base_date = date_str.split("saat")[0].strip() if "saat" in date_str else date_str
        time_hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        
        # Aynı istasyonda farklı saatler
        for alt_time in time_hours:
            if alt_time != time_str and not is_time_slot_booked(date_str, alt_time, current_station.get('name', '')):
                # Şu anki istasyonda farklı saat
                current_copy = current_station.copy()
                current_copy['time'] = alt_time
                alternatives.append(current_copy)
                
                # 3 alternatif bulduk, yeterli
                if len(alternatives) >= 3:
                    break
    
    # En fazla 3 alternatif döndür
    return alternatives[:3]

# Belirli bir tarih için hava durumu tahmini (pseudocode)
def get_weather_forecast(date_str):
    """Belirli bir tarih için hava durumu tahmini yapar"""
    # Gerçek uygulamada burada bir hava durumu API'si kullanılabilir
    # Şimdilik basit bir demo yapacağız
    
    try:
        # Tarihten bir seed oluştur
        date_seed = sum(ord(c) for c in date_str)
        
        # Hava durumu tipleri
        weather_types = ["güneşli", "parçalı bulutlu", "bulutlu", "yağmurlu", "hafif yağmurlu", "fırtınalı"]
        
        # Sıcaklık aralığı (15-35 derece)
        temperature = (date_seed % 20) + 15
        
        # Hava durumu tipi (seed'e göre belirle)
        weather_type = weather_types[date_seed % len(weather_types)]
        
        # Araç yıkamak için uygunluk
        if weather_type in ["güneşli", "parçalı bulutlu"]:
            comment = f"Hava {weather_type} ve {temperature}°C, araç yıkama için mükemmel bir gün olacak!"
        elif weather_type == "bulutlu":
            comment = f"Hava {weather_type} ve {temperature}°C, araç yıkama için uygun koşullar."
        elif weather_type == "hafif yağmurlu":
            comment = f"Hava {weather_type} ve {temperature}°C, kapalı istasyonumuzda aracınız korunaklı olacak."
        else:
            comment = f"Hava {weather_type} ve {temperature}°C, kapalı istasyonumuzda yıkama yapılacaktır."
        
        return {
            "weather": weather_type,
            "temperature": temperature,
            "comment": comment
        }
    except:
        return {
            "weather": "güneşli",
            "temperature": 25,
            "comment": "Hava araç yıkamak için çok uygun olacak!"
        }

# Dolu olan saatler için her koşulda öneri yapan yardımcı fonksiyon
def get_forced_alternatives(date_str, location_info):
    """Dolu olan saatler için her koşulda alternatif öneriler yapar"""
    stations_data = read_stations_data()
    
    # 3 sabit saati öner
    alternative_times = ["09:30", "14:00", "16:30"]
    
    # 2 sabit istasyonu öner
    available_stations = stations_data.get('stations', [])[:3]  # İlk 3 istasyonu al
    
    alternatives = []
    
    # Her istasyon için bir zaman öner
    for i, station in enumerate(available_stations):
        if i < len(alternative_times):
            alternative = station.copy()
            alternative['time'] = alternative_times[i]
            alternatives.append(alternative)
    
    # En fazla 3 alternatif döndür
    return alternatives[:3]

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Chatbot API
@app.route('/api/chat', methods=['POST'])
def chat():
    # Gelen isteği al
    data = request.json
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    user_state = data.get('state', {})
    
    # Debug için
    print(f"Received message: {user_message}")
    print(f"Current state: {user_state}")
    
    # Başlangıçta time_str ve date_time değişkenlerini tanımla (güvenlik için)
    time_str = "12:00"  # Varsayılan değer
    date_time = "Bugün"  # Varsayılan değer
    date_analysis = "Bugün"  # Varsayılan değer
    
    # Kullanıcı mesajını chat geçmişine ekle
    chat_history.append({"role": "user", "content": user_message})
    
    # OpenAI API ile chatbot yanıtı al
    try:
        # Özel durumları işle
        if 'verify_code' in user_state and user_state['verify_code'] == True:
            # Kod doğrulama
            user_data = read_user_data(user_message)
            if user_data:
                name = user_data['personal_info']['name']
                surname = user_data['personal_info']['surname']
                car_model = user_data['car_info']['model']
                plate = user_data['car_info']['plate']
                remaining_washes = user_data['membership']['remaining_washes']
                
                bot_message = f"Merhaba {name} {surname}! 🎉\n\n"
                bot_message += f"BMW Prime üyeliğiniz başarıyla doğrulandı.\n\n"
                bot_message += f"🚘 Aracınız: {car_model} (Plaka: {plate})\n\n"
                bot_message += "Yıkama randevunuzu kendi aracınız için mi, yoksa başka bir araç için mi oluşturmak istersiniz? 😊"
                
                # Durum güncellemesi
                user_state = {
                    'verified': True,
                    'verify_code': False,
                    'user_code': user_message,
                    'asking_car_selection': True
                }
            else:
                bot_message = "Girdiğiniz kod geçersiz. Lütfen tekrar deneyin veya farklı bir seçenek seçin."
                user_state = {
                    'verified': False,
                    'verify_code': True
                }
        
        elif 'asking_car_selection' in user_state and user_state['asking_car_selection'] == True:
            if "kendi" in user_message.lower() or "benim" in user_message.lower():
                user_code = user_state.get('user_code', '')
                user_data = read_user_data(user_code)
                
                if user_data:
                    remaining_washes = user_data['membership']['remaining_washes']
                    
                    if remaining_washes > 0:
                        # Yıkama hakkını güncelle
                        user_data['membership']['remaining_washes'] = remaining_washes - 1
                        updated = update_user_data(user_code, user_data)
                        
                        bot_message = f"Kendi aracınız için randevu oluşturulacak. Kalan yıkama hakkınız: {remaining_washes-1}.\n\n"
                        bot_message += "Lütfen bulunduğunuz konumu belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
                        
                        user_state = {
                            'verified': True,
                            'asking_car_selection': False,
                            'asking_location': True,
                            'own_car': True
                        }
                    else:
                        bot_message = "📝 Üzgünüm, kalan yıkama hakkınız bulunmamaktadır. Yeni yıkama hakkı satın almak veya başka bir araç için randevu oluşturmak isterseniz bana bildirebilirsiniz. 😊"
                        
                        user_state = {
                            'verified': True,
                            'asking_car_selection': False,
                            'asking_location': False,  # Konuma geçmesini engelle
                            'own_car': True
                        }
                else:
                    bot_message = "Kullanıcı bilgilerinize erişilemiyor. Lütfen tekrar giriş yapın."
                    user_state = {}
            else:
                bot_message = "Başka bir araç için randevu oluşturacaksınız. Öncelikle isim ve soyisim bilgilerinizi yazabilir misiniz?"
                
                user_state = {
                    'verified': True,
                    'asking_car_selection': False,
                    'asking_other_name': True,
                    'other_car_info': {}
                }
        
        elif 'asking_other_name' in user_state and user_state['asking_other_name'] == True:
            # İsim soyisim bilgisini analiz et
            analysis_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Kullanıcı isim soyisim girdi. Bu girdiden isim ve soyisim bilgisini çıkar. Format: {\"name\": \"İsim\", \"surname\": \"Soyisim\"}"},
                    {"role": "user", "content": user_message}
                ]
            )
            
            name_analysis = analysis_response.choices[0].message['content']
            
            try:
                # JSON formatına çevir
                name_data = json.loads(name_analysis)
                
                # Other car info güncellemesi
                other_car_info = user_state.get('other_car_info', {})
                other_car_info['name'] = name_data.get('name', '')
                other_car_info['surname'] = name_data.get('surname', '')
                
                bot_message = f"İsim bilginiz kaydedildi: {name_data.get('name', '')} {name_data.get('surname', '')}\n\n"
                bot_message += "Şimdi lütfen aracın plaka numarasını girin:"
                
                user_state = {
                    'verified': True,
                    'asking_other_name': False,
                    'asking_other_plate': True,
                    'other_car_info': other_car_info
                }
            except json.JSONDecodeError:
                bot_message = "İsim bilginizi anlayamadım. Lütfen isim ve soyisminizi 'Ahmet Yılmaz' formatında girin:"
                user_state = {
                    'verified': True,
                    'asking_other_name': True
                }
        
        elif 'asking_other_plate' in user_state and user_state['asking_other_plate'] == True:
            # Plaka bilgisini kaydet
            other_car_info = user_state.get('other_car_info', {})
            other_car_info['plate'] = user_message.strip().upper()
            
            bot_message = f"Plaka bilgisi kaydedildi: {other_car_info['plate']}\n\n"
            bot_message += "Şimdi lütfen aracın markasını ve modelini yazın (örn: BMW 3 Serisi, Audi A4):"
            
            user_state = {
                'verified': True,
                'asking_other_plate': False,
                'asking_other_model': True,
                'other_car_info': other_car_info
            }
        
        elif 'asking_other_model' in user_state and user_state['asking_other_model'] == True:
            # Model bilgisini kaydet
            other_car_info = user_state.get('other_car_info', {})
            other_car_info['model'] = user_message.strip()
            
            # Telefon numarası iste
            bot_message = f"Araç bilgileri alındı:\n"
            bot_message += f"- İsim Soyisim: {other_car_info.get('name', '')} {other_car_info.get('surname', '')}\n"
            bot_message += f"- Plaka: {other_car_info.get('plate', '')}\n"
            bot_message += f"- Model: {other_car_info.get('model', '')}\n\n"
            bot_message += "Rezervasyon ve randevu hatırlatma mesajı için lütfen telefon numaranızı (5XX XXX XX XX formatında) yazınız:"
            
            user_state = {
                'verified': True,
                'asking_other_model': False,
                'asking_other_phone': True,
                'other_car_info': other_car_info
            }
        
        elif 'asking_other_phone' in user_state and user_state['asking_other_phone'] == True:
            # Telefon numarası bilgisini kaydet
            other_car_info = user_state.get('other_car_info', {})
            phone_number = user_message.strip().replace(" ", "")
            
            # Telefon numarası validasyonu
            if phone_number.startswith("+90"):
                phone_number = phone_number[3:]
                
            if len(phone_number) >= 10 and phone_number.isdigit():
                other_car_info['phone'] = phone_number
                
                bot_message = f"Telefon numaranız kaydedildi. Şimdi lütfen bulunduğunuz konumu belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
                
                user_state = {
                    'verified': True,
                    'asking_other_phone': False,
                    'asking_location': True,
                    'own_car': False,
                    'other_car_info': other_car_info
                }
            else:
                bot_message = "Geçerli bir telefon numarası girmediniz. Lütfen telefon numaranızı 5XX XXX XX XX formatında giriniz:"
                user_state = {
                    'verified': True,
                    'asking_other_phone': True,
                    'other_car_info': other_car_info
                }
        
        elif 'collecting_other_car' in user_state and user_state['collecting_other_car'] == True:
            # Eski kod, geri uyumluluk için bırakıldı
            analysis_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Kullanıcı araç bilgilerini girdi. Bu girdiyi analiz et ve aşağıdaki formatta bilgileri çıkar: marka, model, plaka, isim, soyisim. Eğer bir bilgi eksikse, bunu belirt."},
                    {"role": "user", "content": user_message}
                ]
            )
            
            analysis = analysis_response.choices[0].message['content']
            
            # Plaka bilgisi eksik mi kontrol et
            if "plaka" in analysis.lower() and "eksik" in analysis.lower():
                bot_message = "Girdiğiniz bilgilerde plaka numarası eksik. Lütfen aracın plaka numarasını da belirtin:"
                user_state = {
                    'verified': True,
                    'collecting_other_car': True,
                    'car_info_partial': analysis,
                    'asking_plate': True
                }
            else:
                # Bilgileri işle
                bot_message = "Araç bilgileriniz kaydedildi. Şimdi lütfen bulunduğunuz konumu belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
                
                user_state = {
                    'verified': True,
                    'collecting_other_car': False,
                    'asking_location': True,
                    'own_car': False,
                    'other_car_info': analysis
                }
        
        elif 'asking_plate' in user_state and user_state['asking_plate'] == True:
            # Plaka bilgisini ekle
            car_info = user_state.get('car_info_partial', '')
            updated_info = f"{car_info}\nPlaka: {user_message}"
            
            bot_message = "Plaka bilgisi eklendi. Şimdi lütfen bulunduğunuz konumu belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
            
            user_state = {
                'verified': True,
                'asking_plate': False,
                'asking_location': True,
                'own_car': False,
                'other_car_info': updated_info
            }
        
        elif 'asking_location' in user_state and user_state['asking_location'] == True:
            # Konum bilgisini analiz et
            location_info = analyze_location(user_message)
            
            if location_info:
                # Konumu doğrula
                confirmation_message = f"Konumunuzu '{location_info['city']} {location_info['district']}' olarak algılıyorum. "
                
                # En yakın istasyonları bul
                nearby_stations = find_nearby_stations(location_info)
                
                if nearby_stations:
                    # En iyi istasyonu öner
                    recommended_station = recommend_best_station(nearby_stations)
                    
                    bot_message = f"{confirmation_message}\n\n"
                    bot_message += "📍 Size en yakın yıkama istasyonları:\n\n"
                    
                    for i, station in enumerate(nearby_stations, 1):
                        # Premium istasyonlar için yıldız ekle
                        star_rating = "⭐" * int(station['rating'])
                        station_type = "🔹 NORMAL" if station['type'] == 'normal' else "🔸 PREMIUM"
                        
                        bot_message += f"<div class='station-card'>\n"
                        bot_message += f"  <h4>{i}. {station['name']}</h4>\n"
                        bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                        bot_message += f"  <div class='station-rating'>{star_rating} ({station['rating']})</div>\n"
                        bot_message += f"  <div class='station-address'>📍 {station['address']}</div>\n"
                        bot_message += f"  <div class='station-distance'>🚗 {station['distance']} km</div>\n"
                        bot_message += f"  <div class='station-time'>⏱️ {station['wash_time_minutes']} dakika</div>\n"
                        
                        # Servisler için ikon ekle
                        services = station.get('services', [])
                        if services:
                            bot_message += f"  <div class='station-services'>🧼 {', '.join(services)}</div>\n"
                        
                        bot_message += f"</div>\n\n"
                    
                    # Önerilen istasyon
                    if recommended_station:
                        rec_index = nearby_stations.index(recommended_station) + 1
                        bot_message += f"\n<div class='recommendation'>💡 <strong>ÖNERİM:</strong> Konum ve hizmet kalitesine göre size #{rec_index} numaralı istasyonu öneriyorum.</div>\n\n"
                    
                    bot_message += "Hangi istasyonda randevu oluşturmak istersiniz? (1, 2 veya 3 yazarak seçebilirsiniz)"
                    
                    user_state = {
                        'verified': True,
                        'asking_location': False,
                        'selecting_station': True,
                        'location_info': location_info,
                        'nearby_stations': nearby_stations,
                        'recommended_station': recommended_station
                    }
                else:
                    bot_message = f"Üzgünüm, {location_info['city']}, {location_info['district']} bölgesinde yıkama istasyonu bulunamadı. Lütfen başka bir konum deneyin."
                    user_state = {
                        'verified': True,
                        'asking_location': True
                    }
                
            else:
                bot_message = "Konumunuzu anlayamadım. Lütfen şehir ve semt/ilçe bilgisini daha açık belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
                user_state = {
                    'verified': True,
                    'asking_location': True
                }
        
        elif 'selecting_station' in user_state and user_state['selecting_station'] == True:
            nearby_stations = user_state.get('nearby_stations', [])
            previous_stations = user_state.get('previous_stations', [])
            all_available_stations = nearby_stations.copy()
            
            # Önceki istasyonları da listeye ekle (eğer varsa ve hali hazırda listede değilse)
            if previous_stations:
                for station in previous_stations:
                    if not any(s.get('id') == station.get('id') for s in all_available_stations):
                        all_available_stations.append(station)
            
            # Eğer istasyonlar boşsa veya çok az sayıda ise
            if not nearby_stations:
                bot_message = "Üzgünüm, şu anda bu bölgede istasyon bulunamadı. Lütfen başka bir konum deneyin."
                user_state = {
                    'verified': True,
                    'asking_location': True
                }
            # Başka konum veya istasyon araması için
            elif "başka" in user_message.lower() or "öner" in user_message.lower() or "farklı" in user_message.lower():
                location_info = user_state.get('location_info', {})
                
                if location_info:
                    # Önceki istasyonları kaydet
                    user_state['previous_stations'] = nearby_stations.copy()
                    
                    # Mevcut istasyon ID'lerini hariç tut
                    exclude_stations = [station.get('id') for station in nearby_stations]
                    
                    # Alternatif istasyonlar bul
                    alternative_stations = find_nearby_stations(
                        location_info, 
                        limit=3, 
                        exclude_stations=exclude_stations,
                        alternative_search=True
                    )
                    
                    if alternative_stations:
                        bot_message = f"Size farklı konumlarda bulunan istasyonları öneriyorum:\n\n"
                        
                        for i, station in enumerate(alternative_stations, 1):
                            # Premium istasyonlar için yıldız ekle
                            star_rating = "⭐" * int(station['rating'])
                            station_type = "🔹 NORMAL" if station['type'] == 'normal' else "🔸 PREMIUM"
                            
                            bot_message += f"<div class='station-card'>\n"
                            bot_message += f"  <h4>{i}. {station['name']}</h4>\n"
                            bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                            bot_message += f"  <div class='station-rating'>{star_rating} ({station['rating']})</div>\n"
                            bot_message += f"  <div class='station-address'>📍 {station['address']}</div>\n"
                            bot_message += f"  <div class='station-distance'>🚗 {station['distance']} km</div>\n"
                            bot_message += f"  <div class='station-time'>⏱️ {station['wash_time_minutes']} dakika</div>\n"
                            
                            # Seçme butonu ekle - time referansını kaldırıyorum
                            bot_message += f"  <button class='btn btn-sm btn-primary mt-2' onclick='selectNewStation(\"{station['name']}\", \"\")'>Bu İstasyonu Seç</button>\n"
                            bot_message += f"</div>\n\n"
                        
                        bot_message += "Hangi istasyonda randevu oluşturmak istersiniz? (İstasyon adını yazabilir veya numara seçebilirsiniz)"
                        
                        user_state = {
                            'verified': True,
                            'selecting_station': True,
                            'location_info': location_info,
                            'nearby_stations': alternative_stations,
                            'previous_stations': user_state.get('previous_stations', [])
                        }
                    else:
                        bot_message = "Üzgünüm, bu bölgede başka istasyon bulunamadı. Farklı bir konum denemek ister misiniz?"
                        user_state = {
                            'verified': True,
                            'asking_location': True
                        }
                else:
                    bot_message = "Farklı bir konum için arama yapmak istiyorsunuz. Lütfen yeni konumunuzu belirtin (örn: İstanbul Kadıköy, Ankara Çankaya):"
                    user_state = {
                        'verified': True,
                        'asking_location': True
                    }
            # Önceki istasyonları göster
            elif "önceki" in user_message.lower() and ("istasyon" in user_message.lower() or "göster" in user_message.lower()):
                previous_stations = user_state.get('previous_stations', [])
                
                if previous_stations:
                    bot_message = f"Önceki istasyon önerileriniz:\n\n"
                    
                    for i, station in enumerate(previous_stations, 1):
                        # Premium istasyonlar için yıldız ekle
                        star_rating = "⭐" * int(station['rating'])
                        station_type = "🔹 NORMAL" if station['type'] == 'normal' else "🔸 PREMIUM"
                        
                        bot_message += f"<div class='station-card'>\n"
                        bot_message += f"  <h4>{i}. {station['name']}</h4>\n"
                        bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                        bot_message += f"  <div class='station-rating'>{star_rating} ({station['rating']})</div>\n"
                        bot_message += f"  <div class='station-address'>📍 {station['address']}</div>\n"
                        bot_message += f"  <div class='station-distance'>🚗 {station['distance']} km</div>\n"
                        bot_message += f"  <div class='station-time'>⏱️ {station['wash_time_minutes']} dakika</div>\n"
                        
                        # Servisler için ikon ekle
                        services = station.get('services', [])
                        if services:
                            bot_message += f"  <div class='station-services'>🧼 {', '.join(services)}</div>\n"
                        
                        bot_message += f"</div>\n\n"
                    
                    bot_message += "Hangi istasyonda randevu oluşturmak istersiniz? (İstasyon adını yazabilir veya numara seçebilirsiniz)"
                    
                    user_state = {
                        'verified': True,
                        'selecting_station': True,
                        'location_info': user_state.get('location_info', {}),
                        'nearby_stations': previous_stations,
                        'previous_stations': user_state.get('nearby_stations', [])  # Mevcut ve öncekini değiştir
                    }
                else:
                    bot_message = "Daha önce gösterilen istasyon bulunamadı. Yeni bir arama yapmak ister misiniz?"
                    user_state = {
                        'verified': True,
                        'selecting_station': True,
                        'nearby_stations': nearby_stations
                    }
            else:
                # Eğer istasyon ismine göre seçim yapılmaya çalışılıyor mu kontrol et
                selected_station = None
                
                # İlk olarak tam eşleşme kontrol et
                if 'nearby_stations' in user_state:
                    nearby_stations = user_state['nearby_stations']
                    for station in nearby_stations:
                        # Kullanıcının yazdığı mesajda istasyon adı tam olarak geçiyorsa
                        if station['name'].lower() in user_message.lower():
                            selected_station = station
                            print(f"DEBUG: Exact station name match found: {station['name']}")
                            break
                
                # Tam eşleşme yoksa, istasyon ismi ile arama
                if not selected_station:
                    for station in all_available_stations:
                        station_name = station.get('name', '').lower()
                        station_location = station.get('location', '').lower()
                        
                        # İstasyon adının önemli kısmı mesajda geçiyorsa
                        if ("çankaya" in user_message.lower() and "çankaya" in station_name) or ("kızılay" in user_message.lower() and "kızılay" in station_name) or ("atakule" in user_message.lower() and "atakule" in station_name):
                            selected_station = station
                            print(f"DEBUG: Keyword match found: {station['name']}")
                            break
                        # İstasyon adı veya semti mesajda geçiyorsa
                        elif (station_name in user_message.lower() or 
                            station_location in user_message.lower() or
                            any(word in station_name for word in user_message.lower().split())):
                            selected_station = station
                            print(f"DEBUG: Partial station name match found: {station['name']}")
                            break
                
                # Eğer isim ile bir istasyon bulunmadıysa, sayı ile seçmeyi deneyin
                if not selected_station:
                    # Önce mesajın içinde 1, 2, 3 gibi bir sayı var mı diye bak 
                    number_match = None
                    for word in user_message.strip().split():
                        if word.isdigit() and 1 <= int(word) <= len(nearby_stations):
                            number_match = int(word)
                            print(f"DEBUG: Number match found in word: {word} -> {number_match}")
                            break
                        # "1." veya "2." şeklinde de olabilir
                        elif word.endswith('.') and word[:-1].isdigit() and 1 <= int(word[:-1]) <= len(nearby_stations):
                            number_match = int(word[:-1])
                            print(f"DEBUG: Number match with dot found: {word} -> {number_match}")
                            break
                    
                    # Sayı bulunduysa, o indeksteki istasyonu seç
                    if number_match is not None:
                        selected_station = nearby_stations[number_match-1]
                        print(f"DEBUG: Selected station by number: {selected_station['name']}")
                    else:
                        # Tüm mesaj bir sayı mı diye kontrol et
                        try:
                            selection = int(user_message.strip())
                            if 1 <= selection <= len(nearby_stations):
                                selected_station = nearby_stations[selection-1]
                                print(f"DEBUG: Selected station by full number: {selected_station['name']}")
                            else:
                                bot_message = f"Lütfen 1 ile {len(nearby_stations)} arasında bir sayı girin."
                                user_state = {
                                    'verified': True,
                                    'selecting_station': True
                                }
                        except ValueError:
                            # Sayı ya da istasyon ismi girilmediyse
                            bot_message = "Lütfen listedeki istasyonlardan birini seçmek için sayı girin (1, 2, 3) veya istasyon adını yazın.\nYeni bir konum aramak için 'başka yer öner' diyebilirsiniz."
                            user_state = {
                                'verified': True,
                                'selecting_station': True
                            }
                
                # Eğer bir istasyon seçildiyse
                if selected_station:
                    # Debug mesajı
                    print(f"DEBUG: Final selected station: {selected_station['name']}")
                    
                    bot_message = f"'{selected_station['name']}' istasyonu seçildi.\n\n"
                    bot_message += "Lütfen randevu için tarih ve saat belirtin (örn: 25 Mayıs saat 14:30):"
                    
                    user_state = {
                        'verified': True,
                        'selecting_station': False,
                        'scheduling': True,
                        'selected_station': selected_station
                    }
                    
                    # İstasyon seçildiğinde tarih kontrolü yapılmamalı, doğrudan randevu için tarih istenmeli
                    # Bu yüzden burada işlemi kesip yanıtı dönmeliyiz
                    return jsonify({
                        'response': bot_message,
                        'history': chat_history,
                        'state': user_state
                    })
                
                # Güvenlik kontrolü - kullanmadan önce değişkenlerin tanımlı olduğundan emin ol
                if 'time_str' not in locals() or not time_str:
                    time_str = "12:00"  # Varsayılan değer
                    
                if 'date_time' not in locals() or not date_time:
                    date_time = "Bugün"  # Varsayılan değer
                    
                if 'date_analysis' not in locals() or not date_analysis:
                    date_analysis = "Bugün"  # Varsayılan değer
                
                # Dolu tarih/saat kontrolü
                if time_str and is_time_slot_booked(date_time, time_str, station_name):
                    # Seçilen tarih ve saat dolu, alternatif öneriler yap
                    
                    # 1. Aynı istasyonda farklı saatler öner
                    bot_message = f"Üzgünüm, {station_name} istasyonunda {date_analysis} tarihi ve saati <b>dolu</b>.\n\n"
                    
                    # İlk olarak aynı saatte farklı istasyonlar öner
                    location_info = user_state.get('location_info', {})
                    
                    # Güvenlik kontrolü
                    if 'date_time' not in locals() or not date_time:
                        date_time = "Bugün"
                        
                    if not time_str:
                        time_str = "12:00"
                        
                    alternative_stations = find_alternative_stations_for_time(
                        date_time, 
                        time_str, 
                        selected_station, 
                        location_info
                    )
                    
                    if alternative_stations:
                        bot_message += f"<h5>Aynı saatte farklı istasyonlar:</h5>\n"
                        for i, station in enumerate(alternative_stations, 1):
                            bot_message += f"<div class='station-card'>\n"
                            bot_message += f"  <h4>{i}. {station['name']}</h4>\n"
                            # Premium istasyonlar için yıldız ekle
                            star_rating = "⭐" * int(station['rating'])
                            station_type = "🔹 NORMAL" if station['type'] == 'normal' else "🔸 PREMIUM"
                            bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                            bot_message += f"  <div class='station-rating'>{star_rating} ({station['rating']})</div>\n"
                            bot_message += f"  <div class='station-address'>📍 {station['address']}</div>\n"
                            bot_message += f"  <div class='station-distance'>🚗 {station['distance']} km</div>\n"
                            bot_message += f"  <div class='station-time'>⏱️ {station['wash_time_minutes']} dakika</div>\n"
                            
                            # Station'da zaman bilgisi varsa onu kullan, yoksa dışarıdaki time_str'yi kullan
                            station_time = station.get('time', time_str)
                            
                            # Seçme butonu ekle
                            bot_message += f"  <button class='btn btn-sm btn-primary mt-2' onclick='selectNewStation(\"{station['name']}\", \"{station_time}\")'>{station_time} için Bu İstasyonu Seç</button>\n"
                            bot_message += f"</div>\n\n"
                    
                    # 2. Aynı istasyonda farklı saatler öner
                    # Aynı günde alternatif saatler
                    now = datetime.now()
                    alternative_times = []
                    
                    # Mesaj içindeki tarihi kullan
                    # Güvenlik kontrolü - date_part değişkeni kullanımını kaldırıp date_time ile değiştiriyorum
                    if 'date_time' in locals() and date_time:
                        if "saat" in date_time:
                            base_date = date_time.split('saat')[0].strip()
                        else:
                            # "14 Mart 2025 09:00" gibi formatlar için
                            parts = date_time.split()
                            if len(parts) >= 3:  # En az "gün ay yıl" formatında olmalı
                                base_date = " ".join(parts[:-1])  # Son parça (saat) hariç
                            else:
                                base_date = date_time
                    else:
                        base_date = "Bugün"  # Varsayılan değer
                    
                    # Tam saatleri ve yarım saatleri oluştur
                    base_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
                    for hour in base_hours:
                        for minute in [0, 30]:
                            alt_time_str = f"{hour:02d}:{minute:02d}"
                            # Bu saat dolu mu kontrol et
                            if not is_time_slot_booked(date_time, alt_time_str, station_name):
                                alternative_times.append(alt_time_str)
                    
                    if alternative_times:
                        bot_message += f"<h5>Aynı istasyonda farklı saatler:</h5>\n"
                        bot_message += "<div class='alternative-times'>\n"
                        for i, alt_time in enumerate(alternative_times[:4], 1):
                            bot_message += f"<button class='alt-time-btn' onclick='selectAlternativeTime(\"{base_date} saat {alt_time}\")'>{i}. {base_date} saat {alt_time}</button>\n"
                        bot_message += "</div>\n\n"
                    
                    # Alternatif bulunamadıysa daha geniş bir arama yap
                    if not alternative_times and not alternative_stations:
                        # Daha geniş bir arama yap
                        wider_alternatives = find_any_alternative_stations_and_times(
                            date_time if 'date_time' in locals() and date_time else "Bugün", 
                            time_str if 'time_str' in locals() and time_str else "12:00",
                            selected_station if selected_station else {"name": station_name, "id": "unknown"},
                            location_info if location_info else {}
                        )
                        
                        if wider_alternatives:
                            bot_message += "<h5>Alternatif İstasyon/Saatler:</h5>\n"
                            for i, alt in enumerate(wider_alternatives, 1):
                                alt_time = alt['time']
                                bot_message += f"<div class='station-card'>\n"
                                bot_message += f"  <h4>{i}. {alt['name']} - {alt_time}</h4>\n"
                                
                                # Premium istasyonlar için yıldız ekle
                                star_rating = "⭐" * int(alt['rating'])
                                station_type = "🔹 NORMAL" if alt['type'] == 'normal' else "🔸 PREMIUM"
                                bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                                bot_message += f"  <div class='station-rating'>{star_rating} ({alt['rating']})</div>\n"
                                bot_message += f"  <div class='station-address'>📍 {alt['address']}</div>\n"
                                bot_message += f"  <div class='station-distance'>🚗 {alt['distance']} km</div>\n"
                                bot_message += f"  <div class='station-time'>⏱️ {alt['wash_time_minutes']} dakika</div>\n"
                                
                                # Seçme butonu ekle
                                bot_message += f"  <button class='btn btn-sm btn-primary mt-2' onclick='selectNewStation(\"{alt['name']}\", \"{alt_time}\")'>{alt_time}'de Bu İstasyonu Seç</button>\n"
                                bot_message += f"</div>\n\n"
                        else:
                            # Her zaman alternatif göster (zorla)
                            forced_alternatives = get_forced_alternatives(date_time, location_info)
                            
                            bot_message += "<h5>Farklı saatlerdeki uygun alternatifler:</h5>\n"
                            for i, alt in enumerate(forced_alternatives, 1):
                                alt_time = alt['time']
                                bot_message += f"<div class='station-card'>\n"
                                bot_message += f"  <h4>{i}. {alt['name']} - {alt_time}</h4>\n"
                                
                                # Premium istasyonlar için yıldız ekle
                                star_rating = "⭐" * int(alt['rating'])
                                station_type = "🔹 NORMAL" if alt['type'] == 'normal' else "🔸 PREMIUM"
                                bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                                bot_message += f"  <div class='station-rating'>{star_rating} ({alt['rating']})</div>\n"
                                bot_message += f"  <div class='station-address'>📍 {alt['address']}</div>\n"
                                bot_message += f"  <div class='station-distance'>🚗 {alt['distance']} km</div>\n"
                                bot_message += f"  <div class='station-time'>⏱️ {alt['wash_time_minutes']} dakika</div>\n"
                                
                                # Seçme butonu ekle
                                bot_message += f"  <button class='btn btn-sm btn-primary mt-2' onclick='selectNewStation(\"{alt['name']}\", \"{alt_time}\")'>{alt_time}'de Bu İstasyonu Seç</button>\n"
                                bot_message += f"</div>\n\n"
                    
                    bot_message += "\nFarklı bir tarih/saat seçmek için takvimi kullanabilirsiniz."
                    
                    user_state = {
                        'verified': True,
                        'scheduling': True,
                        'calendar_needed': True,
                        'alternatives_offered': True,
                        'selected_station': selected_station,
                        'location_info': location_info
                    }
                else:
                    bot_message = "<div class='confirmation-card'>\n"
                    bot_message += f"  <h3>🎉 Randevunuz Onaylandı!</h3>\n"
                    bot_message += f"  <div class='confirmation-detail'><strong>Tarih:</strong> {date_analysis}</div>\n"
                    bot_message += f"  <div class='confirmation-detail'><strong>İstasyon:</strong> {station_name}</div>\n"
                    bot_message += f"  <div class='confirmation-detail'><strong>Adres:</strong> {selected_station.get('address', '')}</div>\n"
                    bot_message += f"  <div class='confirmation-detail'><strong>Tahmini Süre:</strong> {selected_station.get('wash_time_minutes', 30)} dakika</div>\n"
                    
                    # Hava durumu tahmini
                    weather_forecast = get_weather_forecast(date_analysis)
                    weather_emoji = "☀️" if "güneşli" in weather_forecast["weather"] else "🌤️" if "parçalı" in weather_forecast["weather"] else "☁️" if "bulutlu" in weather_forecast["weather"] else "🌧️" if "yağmur" in weather_forecast["weather"] else "⛈️"
                    
                    bot_message += f"  <div class='confirmation-detail weather-forecast'><strong>{weather_emoji} Hava Durumu:</strong> {weather_forecast['weather'].capitalize()}, {weather_forecast['temperature']}°C</div>\n"
                    bot_message += f"  <div class='weather-comment'>{weather_forecast['comment']}</div>\n"
                    
                    # Hatırlatma mesajı
                    bot_message += f"  <div class='reminder-note mt-3'>🔔 Hatırlatma:\nRandevunuzdan 30 dakika önce size bir hatırlatma mesajı gönderilecektir.</div>\n"
                    bot_message += f"</div>\n\n"
                    bot_message += "✅ Randevunuz başarıyla oluşturuldu!\nSana en iyi deneyimi yaşatmak için istasyonumuzu bildiriyoruz. Memnun kalmadığın durumlarda bize 08503036291 numaralı müşteri hizmetlerimizden bize ulaşmaktan lütfen çekinme 🫡"
                    
                    # Kullanıcı kodu varsa, kullanıcı bilgilerini güncelle
                    if user_state.get('own_car') and user_state.get('user_code'):
                        user_code = user_state.get('user_code')
                        user_data = read_user_data(user_code)
                        
                        if user_data:
                            # Son konum bilgisini güncelle
                            location_info = user_state.get('location_info', {})
                            if location_info:
                                user_data['last_known_location'] = location_info
                            
                            # Güncelle
                            update_user_data(user_code, user_data)
                    
                    user_state = {
                        'verified': True,
                        'scheduling': False,
                        'completed': True
                    }
        
        elif 'scheduling' in user_state and user_state['scheduling'] == True:
            # Tarih analizi
            try:
                analysis_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Kullanıcı randevu için tarih ve saat belirtiyor. Bu girdiyi analiz et ve anlaşılır bir formata çevir. ÖNEMLİ: Eğer kullanıcı tam bir tarih ve saat belirtmişse (örneğin '14 Mart 2025 09:00' gibi), BU TARİHİ OLDUĞU GİBİ KABUL ET VE AYNEN DÖNDÜR. Göreceli terimleri (bugün, yarın, vb.) mevcut tarihe göre çözümle. Yarım saatli ifadeleri doğru algıla. Format olarak şunları kullan: tam saatler için 'xx:00', yarım saatler için 'xx:30'. Eğer girdi geçerli bir tarih belirtmiyorsa, hangi kısımların eksik olduğunu belirt."},
                        {"role": "user", "content": f"Bugünün tarihi: {datetime.now().strftime('%d %B %Y')}. Kullanıcının belirttiği tarih: {user_message}"}
                    ]
                )
                
                date_analysis = analysis_response.choices[0].message['content']
                
                if "geçerli bir tarih belirtilmedi" in date_analysis.lower() or "eksik" in date_analysis.lower():
                    bot_message = "Üzgünüm, tarihinizi tam olarak anlayamadım. Lütfen gün, ay ve saati açık bir şekilde belirtin (örn: 25 Mayıs saat 14:30).\n\nAşağıdaki takvimden de seçim yapabilirsiniz."
                    user_state = {
                        'verified': True,
                        'scheduling': True,
                        'calendar_needed': True
                    }
                    return jsonify({
                        'response': bot_message,
                        'history': chat_history,
                        'state': user_state
                    })
                else:
                    selected_station = user_state.get('selected_station', {})
                    station_name = selected_station.get('name', 'Seçilen istasyon')
                    
                    # İstasyon adı kontrolü - eğer "Seçilen istasyon" ise kullanıcı mesajından bulmaya çalış
                    if station_name == 'Seçilen istasyon' and 'Kızılay Oto Bakım' in user_message:
                        station_name = 'Kızılay Oto Bakım'
                        # Seçilen istasyonu güncelle
                        selected_station = {
                            'name': station_name,
                            'type': 'normal',
                            'rating': 4.3,
                            'wash_time_minutes': 25,
                            'services': ['İç Yıkama', 'Dış Yıkama']
                        }
                        user_state['selected_station'] = selected_station
                    
                    # Tarih ve saat bilgisini al
                    date_time = date_analysis
                    time_str = ""  # Varsayılan değer
                    
                    # Saat bilgisini çıkar
                    if "saat" in date_analysis:
                        time_parts = date_analysis.split("saat")
                        if len(time_parts) > 1:
                            time_str = time_parts[1].strip().split(",")[0].strip()
                    elif ":" in date_analysis:
                        # "14 Mart 2025 09:00" gibi formatlar için
                        time_parts = date_analysis.split()
                        for part in time_parts:
                            if ":" in part:
                                time_str = part.strip()
                                break
                    
                    # İstasyon ve zaman dolu kontrolü
                    if is_time_slot_booked(date_time, time_str, station_name):
                        # Seçilen tarih ve saat dolu, alternatif öneriler yap
                        bot_message = f"Üzgünüm, {station_name} istasyonunda {date_analysis} tarihi ve saati <b>dolu</b>.\n\n"
                        
                        # İlk olarak aynı saatte farklı istasyonlar öner
                        location_info = user_state.get('location_info', {})
                        
                        alternative_stations = find_alternative_stations_for_time(
                            date_time, 
                            time_str, 
                            selected_station, 
                            location_info
                        )
                        
                        # Alternatif istasyonları listele
                        if alternative_stations:
                            bot_message += f"<h5>Aynı saatte farklı istasyonlar:</h5>\n"
                            for i, station in enumerate(alternative_stations, 1):
                                bot_message += f"<div class='station-card'>\n"
                                bot_message += f"  <h4>{i}. {station['name']}</h4>\n"
                                # Premium istasyonlar için yıldız ekle
                                star_rating = "⭐" * int(station['rating'])
                                station_type = "🔹 NORMAL" if station['type'] == 'normal' else "🔸 PREMIUM"
                                bot_message += f"  <div class='station-type'>{station_type}</div>\n"
                                bot_message += f"  <div class='station-rating'>{star_rating} ({station['rating']})</div>\n"
                                bot_message += f"  <div class='station-address'>📍 {station['address']}</div>\n"
                                bot_message += f"  <div class='station-distance'>🚗 {station['distance']} km</div>\n"
                                bot_message += f"  <div class='station-time'>⏱️ {station['wash_time_minutes']} dakika</div>\n"
                                
                                # Station'da zaman bilgisi varsa onu kullan, yoksa dışarıdaki time_str'yi kullan
                                station_time = station.get('time', time_str)
                                
                                # Seçme butonu ekle
                                bot_message += f"  <button class='btn btn-sm btn-primary mt-2' onclick='selectNewStation(\"{station['name']}\", \"{station_time}\")'>{station_time} için Bu İstasyonu Seç</button>\n"
                                bot_message += f"</div>\n\n"
                    else:
                        # Seçilen tarih ve saat uygun, randevu onayı göster
                        bot_message = f"<div class='confirmation-card'>\n"
                        bot_message += f"  <h3>Randevu Onayı</h3>\n"
                        bot_message += f"  <div class='confirmation-detail'><strong>İstasyon:</strong> {station_name}</div>\n"
                        bot_message += f"  <div class='confirmation-detail'><strong>Tarih:</strong> {date_analysis}</div>\n"
                        
                        # Saat bilgisini çıkar
                        if not time_str:
                            # "14 Mart 2025 09:00" gibi formatlar için
                            if ":" in date_analysis:
                                time_parts = date_analysis.split()
                                for part in time_parts:
                                    if ":" in part:
                                        time_str = part.strip()
                                        break
                            # Eğer hala boşsa ve kullanıcı mesajında varsa oradan al
                            if not time_str and ":" in user_message:
                                time_parts = user_message.split()
                                for part in time_parts:
                                    if ":" in part:
                                        time_str = part.strip()
                                        break
                            # Son çare olarak varsayılan bir değer kullan
                            if not time_str:
                                time_str = "10:00"  # Varsayılan değer
                                
                        bot_message += f"  <div class='confirmation-detail'><strong>Saat:</strong> {time_str}</div>\n"
                        bot_message += f"  <div class='confirmation-detail'><strong>Tahmini Süre:</strong> {selected_station.get('wash_time_minutes', 30)} dakika</div>\n"
                        
                        # Hava durumu tahmini
                        weather_forecast = get_weather_forecast(date_analysis)
                        weather_emoji = "☀️" if "güneşli" in weather_forecast["weather"] else "🌤️" if "parçalı" in weather_forecast["weather"] else "☁️" if "bulutlu" in weather_forecast["weather"] else "🌧️" if "yağmur" in weather_forecast["weather"] else "⛈️"
                        
                        bot_message += f"  <div class='confirmation-detail weather-forecast'><strong>{weather_emoji} Hava Durumu:</strong> {weather_forecast['weather'].capitalize()}, {weather_forecast['temperature']}°C</div>\n"
                        bot_message += f"  <div class='weather-comment'>{weather_forecast['comment']}</div>\n"
                        
                        # Hatırlatma mesajı
                        bot_message += f"  <div class='reminder-note mt-3'>🔔 Hatırlatma:\nRandevunuzdan 30 dakika önce size bir hatırlatma mesajı gönderilecektir.</div>\n"
                        bot_message += f"</div>\n\n"
                        bot_message += "✅ Randevunuz başarıyla oluşturuldu!\nSana en iyi deneyimi yaşatmak için istasyonumuzu bildiriyoruz. Memnun kalmadığın durumlarda bize 08503036291 numaralı müşteri hizmetlerimizden bize ulaşmaktan lütfen çekinme 🫡"
                        
                        # Kullanıcı kodu varsa, kullanıcı bilgilerini güncelle
                        if user_state.get('own_car') and user_state.get('user_code'):
                            user_code = user_state.get('user_code')
                            user_data = read_user_data(user_code)
                            
                            if user_data:
                                # Son konum bilgisini güncelle
                                location_info = user_state.get('location_info', {})
                                if location_info:
                                    user_data['last_known_location'] = location_info
                                
                                # Güncelle
                                update_user_data(user_code, user_data)
                        
                        user_state = {
                            'verified': True,
                            'scheduling': False,
                            'completed': True
                        }
            except Exception as e:
                print(f"DEBUG: Error in date analysis: {e}")
                date_analysis = "Bugün"
                date_time = date_analysis
                time_str = "12:00"
                bot_message = "Üzgünüm, tarih işleme sırasında bir hata oluştu. Takvimden seçim yapabilirsiniz."
                user_state = {
                    'verified': True,
                    'scheduling': True,
                    'calendar_needed': True
                }
                return jsonify({
                    'response': bot_message,
                    'history': chat_history,
                    'state': user_state
                })
        
        else:
            # Normal chatbot yanıtı
            if "bmw prime" in user_message.lower():
                bot_message = "Hoş geldin, Seçkin BMW Prime Üyesi ✨En az aracındaki sürüş konforu kadar harika bir oto yıkama deneyimi yaşatacağız sana🫧🚘\nLütfen BMW Prime Card Numaranızı Yazın"
                user_state = {
                    'verify_code': True
                }
            else:
                # Randevu iptal etme talebi kontrol et
                if "randevu iptal" in user_message.lower() or ("iptal" in user_message.lower() and "randevu" in user_message.lower()) or ("iptal etmek" in user_message.lower()):
                    bot_message = "📝 Randevu iptal talebiniz alınmıştır. Teknik ekibimiz en kısa sürede sizinle iletişime geçecektir. İptal onayı için bir müşteri temsilcimiz sizi arayacaktır. Başka bir konuda yardıma ihtiyacınız var mı? 😊"
                else:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Sen 'arabamiyika.com AI Asistanı' web sitesinin samimi, yardımcı ve uzman chatbotusun. Araç yıkama ve bakım konusunda detaylı bilgiye sahipsin. \n\n1. Kullanıcılarla samimi ve dostça konuş. Uygun emojiler kullan (😊, 👍, 🚗, 🧼, ✨, vs.) ama abartma, mesaj başına 1-2 emoji yeterli.\n\n2. Yanıtların kısa, öz ve samimi olsun. Sanki bir arkadaşla konuşur gibi doğal bir dil kullan.\n\n3. İstasyonlar hakkında bilgi verirken:\n- Çankaya Premium Oto Bakım: Premium hizmet sunan, el ile detaylı yıkama yapan, özel nano-seramik koruma ve cilalama hizmetleri sunan üst segment bir istasyon. Mikrofiber bez ve özel formüllü ürünler kullanılarak fırçasız yıkama tekniği uygulanır. ✨\n- Kızılay Oto Bakım: Standart hizmetler sunan, yarı otomatik yıkama sistemlerine sahip orta segment bir istasyon. 🧽\n- Atakule Oto Yıkama: Premium özellikler taşıyan, özellikle jant ve motor temizliğinde uzmanlaşmış bir istasyon. İç temizlikte buharlı temizlik sistemleri kullanır. 💫\n\n4. Yıkama tekniklerini açıklarken:\n- Fırçasız yıkama (touchless): Mikrofiber bezler ve yüksek kaliteli ürünlerle yapılan el yıkaması 🧤\n- Otomatik yıkama: Yumuşak fırçalı, boyaya zarar vermeyen sistemler 🚿\n- Detaylı temizlik: Özel temizleyiciler, buharlı temizlik, vakumlu sistemler 🔍\n\n5. Randevu ve bakım işlemlerinde tüm detayları açıkla ve ne zaman hazır olacağını belirt.\n\n6. Randevu iptal veya değişiklik taleplerine şu şekilde yanıt ver: 'Randevu iptal/değişiklik talebiniz alınmıştır. Teknik ekibimiz sizi en kısa sürede arayacaktır. 📞'\n\n7. Türkçe karakterleri doğru kullan ve samimi bir tonla yaz. 'Siz' yerine 'sen' diye hitap et. Sanki bir arkadaşınla konuşur gibi samimi ol."},
                            *chat_history
                        ]
                    )
                    
                    bot_message = response.choices[0].message['content']
        
        # Bot mesajını chat geçmişine ekle
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return jsonify({
            "response": bot_message,
            "history": chat_history,
            "state": user_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# BMW Prime kod doğrulama
def verify_bmw_code(code):
    user_data = read_user_data(code)
    if user_data:
        return user_data
    
    # Eski sistem için kontrol (geri uyumluluk)
    users_data = read_users_data()
    
    for user in users_data['users']:
        if user['code'] == code:
            return user
    
    return None

# Eskiden kalan kod doğrulama API'si (örnek olarak bırakılmıştır)
@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get('code', '')
    
    # Örnek olarak, varsayılan geçerli kodlar
    valid_codes = {
        "ABC123": "Ahmet Yılmaz",
        "DEF456": "Fatma Demir",
        "GHI789": "Mehmet Kaya",
    }
    
    if code in valid_codes:
        return jsonify({
            "valid": True,
            "user": valid_codes[code]
        })
    else:
        return jsonify({
            "valid": False,
            "message": "Geçersiz kod. Lütfen tekrar deneyin."
        })

# Konum bilgisini işleme
def parse_location(location_text):
    """Kullanıcının belirttiği konum bilgisini işler"""
    location_text = location_text.lower()
    
    # Yardımcı fonksiyon: Şehir ve ilçe tespiti
    def extract_city_district(text):
        # Büyük şehirleri listele
        cities = ["istanbul", "ankara", "izmir", "bursa", "antalya", "adana"]
        
        # İstanbul'un ilçeleri
        istanbul_districts = ["kadıköy", "beşiktaş", "şişli", "sarıyer", "beyoğlu", "ataşehir", 
                            "üsküdar", "fatih", "bakırköy", "bahçelievler", "beylikdüzü", 
                            "esenyurt", "maltepe", "pendik", "kartal", "tuzla", "ümraniye"]
        
        # Ankara'nın ilçeleri
        ankara_districts = ["çankaya", "keçiören", "etimesgut", "yenimahalle", "mamak", 
                           "sincan", "altındağ", "gölbaşı", "polatlı", "kızılay", "eryaman"]
        
        city = None
        district = None
        
        # Şehir tespiti
        for c in cities:
            if c in text:
                city = c.title()  # İlk harfi büyük
                break
        
        # İlçe tespiti
        istanbul_match = None
        ankara_match = None
        
        for d in istanbul_districts:
            if d in text:
                istanbul_match = d.title()
                break
                
        for d in ankara_districts:
            if d in text:
                ankara_match = d.title()
                break
        
        # Şehir-ilçe eşleştirmesi
        if city == "Istanbul" or istanbul_match:
            city = "İstanbul"
            district = istanbul_match
        elif city == "Ankara" or ankara_match:
            city = "Ankara"
            district = ankara_match
        
        return city, district

    # Şehir ve ilçe çıkarma
    city, district = extract_city_district(location_text)
    
    # Özel konum eşleştirmeleri
    if "kentpark" in location_text and not city:
        city = "Ankara"
        district = "Çankaya"
    elif "istinye park" in location_text and not city:
        city = "İstanbul"
        district = "Sarıyer"
    
    # Genel konum bilgisi kontrolü
    if not city and not district:
        return None
    
    # Koordinat bilgileri (merkez koordinatları)
    coordinates = {
        "İstanbul": {"lat": 41.0082, "lng": 28.9784},
        "Ankara": {"lat": 39.9334, "lng": 32.8597},
        "İzmir": {"lat": 38.4192, "lng": 27.1287}
    }
    
    # İlçelerin koordinatları
    district_coordinates = {
        "Kadıköy": {"lat": 40.9928, "lng": 29.0265},
        "Beşiktaş": {"lat": 41.0422, "lng": 29.0093},
        "Şişli": {"lat": 41.0630, "lng": 28.9916},
        "Ataşehir": {"lat": 40.9923, "lng": 29.1244},
        "Üsküdar": {"lat": 41.0212, "lng": 29.0547},
        "Çankaya": {"lat": 39.9030, "lng": 32.8059},
        "Sarıyer": {"lat": 41.1700, "lng": 29.0500},
        "Maslak": {"lat": 41.1700, "lng": 29.0500}
    }
    
    # Geri dönüş değeri için koordinat seçimi
    selected_coords = None
    if district and district in district_coordinates:
        selected_coords = district_coordinates[district]
    elif city and city in coordinates:
        selected_coords = coordinates[city]
    
    # Sonuç
    result = {
        "city": city,
        "district": district if district else "",
        "coordinates": selected_coords if selected_coords else {"lat": 0, "lng": 0}
    }
    
    return result

if __name__ == '__main__':
    app.run(debug=True) 