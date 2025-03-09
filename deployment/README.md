# arabamiyika.duftech.com.tr Yükleme Kılavuzu

Bu dosya, Flask uygulamasının arabamiyika.duftech.com.tr adresine nasıl yükleneceğini açıklar.

## ISPManager ile Yükleme

1. ISPManager kontrol panelinize giriş yapın.
2. Web Domains (Web Alanları) bölümüne gidin.
3. "arabamiyika.duftech.com.tr" domain'i seçin veya yeni ekleyin.
4. Bu dizindeki tüm dosyaları FTP ile hosting'deki web kök dizinine yükleyin.
5. Kök dizindeki `.env` dosyasını güncellediğinizden emin olun (API anahtarları, vb.).
6. ISPManager'den Python modüllerini yüklemek için SSH erişimi kullanın veya ISPManager'in Python modülü yükleme özelliğini kullanın:
   ```
   pip install -r requirements.txt
   ```
7. Domain ayarlarında, CGI/FastCGI/FCGID desteğinin açık olduğundan emin olun.
8. Python yolu doğru ayarlandığından emin olun.

## SSH ile Yükleme

1. SSH ile sunucuya bağlanın:
   ```
   ssh kullanıcı_adı@sunucu_adresi
   ```

2. Web dizinine gidin:
   ```
   cd /var/www/arabamiyika.duftech.com.tr
   ```

3. Dosyaları yükleyin (yerel bilgisayardan):
   ```
   scp -r * kullanıcı_adı@sunucu_adresi:/var/www/arabamiyika.duftech.com.tr/
   ```
   
4. Gerekli Python paketlerini yükleyin:
   ```
   pip install -r requirements.txt
   ```
   
5. Python uygulamasını başlatmak için uygun bir yöntem kullanın:
   - Apache ile mod_wsgi
   - Nginx ile uWSGI veya Gunicorn
   - Supervisor ile process yönetimi

## Önerilen Sunucu Yapılandırması

Aşağıdaki sunucu yapılandırmasını kullanmanızı öneririz:

- Python 3.6 veya üstü
- Apache/Nginx web sunucusu
- mod_wsgi (Apache için) veya uWSGI/Gunicorn (Nginx için)
- Supervisor (Flask uygulamasını daemon olarak çalıştırmak için)

## Sorun Giderme

Yükleme sırasında sorun yaşarsanız, sunucu loglarını kontrol edin:
- Apache: `/var/log/apache2/error.log`
- Nginx: `/var/log/nginx/error.log`
- Flask uygulaması: Uygulama dizininde log dosyası oluşturmayı düşünün 