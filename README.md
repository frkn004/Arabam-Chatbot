# Arabamı Yıka Chatbot

OpenAI API kullanarak geliştirilmiş, araç yıkama hizmeti sunan bir web sitesi için chatbot uygulaması.

## Özellikler

- Kullanıcılara hoş geldin mesajı ve seçenekler sunma
- BMW Premium Selection üyelerine özel yıkama hizmeti
- Garanti BBVA yıkama hizmeti
- Yıkama randevusu oluşturma
- Kişiye özel kod doğrulama sistemi
- OpenAI API entegrasyonu ile akıllı yanıtlar
- JSON dosyasında kullanıcı verilerini saklama
- Kalan yıkama haklarını takip etme
- Başka araçlar için randevu oluşturma
- AI destekli form doldurma ve tarih analizi

## Kurulum

1. Projeyi bilgisayarınıza klonlayın:
```
git clone <repo-url>
cd arabamiyika-chatbot
```

2. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```

3. `.env` dosyasını düzenleyin ve OpenAI API anahtarınızı ekleyin:
```
OPENAI_API_KEY=your-openai-api-key
```

4. Uygulamayı çalıştırın:
```
python app.py
```

5. Tarayıcınızda `http://127.0.0.1:5000` adresine giderek uygulamayı kullanabilirsiniz.

## Kullanım

- Uygulama açıldığında size üç seçenek sunulacak:
  - BMW Premium Selection'luyum
  - Garanti BBVA yıkama
  - Yıkama randevusu
  
- BMW Premium Selection'luyum seçeneğini seçtikten sonra:
  1. Size özel BMW kodunuzu girmeniz istenecek (Örnek: BMW123, BMW456, BMW789)
  2. Doğru kod girildiğinde, aracınız, plaka ve kalan yıkama hakkı bilgileriniz gösterilecek
  3. Kendi aracınız veya başka bir araç için randevu oluşturma seçeneği sunulacak
  4. Kendi aracınız için seçim yaparsanız, randevu için tarih/saat belirlemeniz istenecek
  5. Başka araç seçerseniz, araç bilgilerini (marka, model, plaka, isim, soyisim) girmeniz istenecek
  6. Son olarak randevu tarihi belirleyeceksiniz

## JSON Dosyasında Saklanan Veriler

users.json dosyasında şu bilgiler saklanır:

- Kullanıcı kodu (BMW üyeliği)
- İsim ve soyisim
- Araç plakası
- Kalan yıkama hakkı
- Araç modeli

Bu bilgiler kod doğrulama ve randevu oluşturma süreçlerinde kullanılır.

## Geliştirme

Bu proje, daha sonra gerçek bir veritabanına bağlanacak şekilde geliştirilecektir. Şu anda JSON dosyasında saklanan örnek veriler kullanılmaktadır. 