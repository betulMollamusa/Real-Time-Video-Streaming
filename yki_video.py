###########################################################################################################
### Jetson'dan gönderilen videoyu alıp hem ekranda gösterir hem de .avi olarak kaydeder### her ikisinde aynı port olmalı (iha, yki)
###########################################################################################################


import socket
import cv2
import pickle
import struct

# UDP soket oluşturma
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sunucunun (videonun kaynağı) WiFi ağındaki IP adresi
host_ip = "169.254.54.38"
port = 5050
server_address = (host_ip, port)

# Mesaj boyutu için kullanılacak yapı
payload_size = struct.calcsize("Q")

# Video kaydı için VideoWriter nesnesi oluştur
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while True:
    try:
        # Veri gönderme
        datas = "client gönderildi".encode()
        client_socket.sendto(datas, server_address)

        # Veri alma
        data, server = client_socket.recvfrom(65507)  # Max UDP veri boyutu

        # Veri boyutunu al
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        # Gelen veriyi tamamlamak için yeterince al
        while len(data) < msg_size:
            packet, server = client_socket.recvfrom(65507)  # Max UDP veri boyutu
            data += packet

        # Veriyi pickle kullanarak yükle
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)

        # Görüntüyü işle, göster ve kaydet
        b = cv2.resize(frame, (640, 480), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        cv2.imshow("Client Frame", b)
        out.write(b)  # Video dosyasına görüntüyü yaz

        # Çıkış için q tuşuna bas
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    except struct.error as e:
        print(e)

# Kayıt işlemi tamamlandıktan sonra dosyayı kapat
out.release()

# Soketi kapat
client_socket.close()

# OpenCV penceresini kapat
cv2.destroyAllWindows()



#Videounun anlık olarak sunucuya basılması işlemini terminal üzerinden aşağıdaki kod ile olacak.
### “ffmpeg.exe –i udp://@127.0.0.1:1111 –c:v h264 –b:v 2M –g 12 –c:a aac –b:a 128k –f mpegts udp://@235.10.10.10:1001” 