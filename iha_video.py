###########################################################################################################
###  Jetson'da (İHA) çalışacak. Video yakalamayı ve alınan kareleri istemciye (yerdeki PC'ye) gönderir. ###
###########################################################################################################

import socket
import cv2
import pickle
import struct
import imutils

# UDP için socket oluştur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sunucunun IP adresi ve port numarası belirleniyor (Jetson'nun IP adresi olabilir)
host_ip = "192.168.1.20"
port = 5050
print("Sunucu {0}:{1} adresine kuruldu".format(host_ip, port))
socket_address = (host_ip, port)

server_socket.bind(socket_address)

while True:
    try:
        # Video dosyası okuyucu (reader) oluşturuluyor (her döngüde yeniden oluşturulması gerekiyor)
        vid = cv2.VideoCapture(0)

        while True:
            # İstemciden gelen isteği al
            data, client_address = server_socket.recvfrom(65535)  # 65535 maksimum veri boyutu
            
            # Görüntü oku ve boyutlandır
            _, frame = vid.read()
            frame = imutils.resize(frame, width=320)
            
            # Görüntüyü seri hale getir (pickle)
            frame_data = pickle.dumps(frame)
            
            # Serileştirilmiş verinin boyutunu paketle (struct)
            message = struct.pack("Q", len(frame_data)) + frame_data
            
            # Veriyi istemciye gönder
            server_socket.sendto(message, client_address)
            
            # Gönderilen görüntüyü ekranda göster
            cv2.imshow("Server Frame", frame)
            
            # Çıkış için 'q' tuşuna basılması kontrolü
            key = cv2.waitKey(25) & 0xFF
            if key == ord("q"):
                break
        
        # Video yakalayıcısını serbest bırak
        vid.release()

    except Exception as e:
        print(e)

cv2.destroyAllWindows()
