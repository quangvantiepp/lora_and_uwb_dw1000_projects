# Thư viện time sử dụng để tạo độ trễ cho chương trình
from time import sleep  

# Import thư viện sx127x  
from SX127x.LoRa import*
from SX127x.board_config import BOARD

'''Thư viện MQTT để gửi các giá trị nhiệt độ và độ ẩm lên nền tảng Cayenne
import paho.mqtt.client as mqtt

Thông tin đăng nhập cho giao tiếp MQTT gữi Raspberry Pi và Cayenne
username = "9cb45ff0-5589-11ec-8da3-474359af83d7"
password = "702411f70b66f85dd78ba37e6c7c7b08fe7bd4b9"
clientid = "ce7a7aa0-5756-11ec-8da3-474359af83d7"

mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()

Tạo kênh 1 cho giá trị nhiệt độ
topic_dht11_temp = "v1/" + username + "/things/" + clientid + "/data/1"

Tạo kênh 2 cho giá trị độ ẩm
topic_dht11_humidity = "v1/" + username + "/things/" + clientid + "/data/2"'''

# Thiết lập các cấu hình cần thiết cho bảng mạch trước khi sử dụng
BOARD.setup() 

# Định nghĩ lớp LoRaRcvCont kế thừa từ lớp LoRa
class LoRaRcvCont(LoRa):
    # Tạo mộ lớp LoRa gồm 3 hàm; init, start va on_rx_done

    # Hàm init được sử dụng để khởi tạo module LoRa  433Mhz với băng thông 125kHz (thông số mặc định)
    # Hàm khởi tạo của class LoRaRcvCont
    # Tham số verbose (mặc định False) dùng để bật tắt chế độ hiển thị thông tin chi tiết trong quá trình hoạt động.
    def __init__(self, verbose=False):
        # Gọi hàm khởi tạo của lớp LoRa để khởi tạo các thuộc tính mặc định
        super(LoRaRcvCont, self).__init__(verbose)
        # Thiết lập chế ban đầu cho module LoRa
        self.set_mode(MODE.SLEEP)
        # Cấu hình các chân ngắt (DIO) của module LoRa. Giá trị [0] * 6 thiết lập tất cả các chân ngắt thành không sử dụng.
        self.set_dio_mapping([0] * 6)
    
        """
        - self luôn đại diện cho đối tượng của lớp LoRaRcvCont.
          nói cách khác, self tham chiếu đến instance của lớp LoRaRcvCont được tạo ra khi bạn khởi tạo lớp đó
        - instance của lớp LoRaRcvCont (ví dụ: lora = LoRaRcvCont(verbose=False)), 
          Python sẽ tự động tạo một object và gắn nó vào tham số self của các hàm trong lớp đó.
          
        """
    
    # Hàm start được sử dụng để định cấu hình module như một bộ thu và nhận giá trị tần số hoạt động
    # Hàm bắt đầu quá trình nhận dữ liệu liên tục
    def start(self):
        # Reset con trỏ nhận, chuẩn bị để nhận dữ liệu mới.
        self.reset_ptr_rx()
        # Thiết lập chế độ hoạt động của module LoRa thành RXCONT (nhận liên tục).
        self.set_mode(MODE.RXCONT)
        # Lặp vô hạn để liên tục kiểm tra và nhận dữ liệu.
        while True:
            # Dừng chương trình trong 0,5s
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            print("RSSI value:", rssi_value)
            print("Status value:", status)
    
    # Hàm on_rx_done được sử dụng để đọc các giá trịn nhận được, sau đó các giá trị nhận được sẽ được chuyển vào một biến gọi là "payload" 
    # và được giải mã bằng "utf-8" và gán vào một biến được gọi là "data"
    # Hàm được gọi tự động khi module LoRa nhận được một gói dữ liệu hoàn chỉnh.
    def on_rx_done(self):

        print ("\nReceived: ")

        # Xóa cờ ngắt báo hiệu nhận xong.
        self.clear_irq_flags(RxDone=1)
        
        # Đọc dữ liệu (payload) từ gói tin nhận được.
        # Tham số nocheck=True bỏ qua việc kiểm tra CRC (kiểm tra lỗi).
        payload = self.read_payload(nocheck=True)
        
        #print (bytes(payload).decode("utf-8",'ignore'))
        # Giải mã dữ liệu từ dạng byte sang chuỗi ký tự theo chuẩn utf-8, bỏ qua các ký tự không giải mã được.
        # - bytes(payload): Chuyển đổi payload thành kiểu byte.
        # - decode("utf-8",'ignore'): Giải mã dữ liệu byte sang chuỗi sử dụng mã hóa UTF-8, bỏ qua các ký tự không hợp lệ.
        data = bytes(payload).decode("utf-8",'ignore')
        print("data:", data)
        # lấy dữ liệu trong chuỗi string gán vào 2 biến temp, và humidity
        temp = (data[0:4])
        humidity = (data[4:6])

        print ("Temperature:")
        print (temp)
        print ("Humidity:")
        print (humidity)

        print ("RSSI value:")
        print (self.get_rssi_value())

        print ("Packet RSSI value:")
        print (self.get_rssi_value())

        print ("Packet SNR value")
        print (self.get_pkt_snr_value())

        """
        # Tách các giá trị nhiệt độ và độ ẩm và gửi chúng lên nền tảng Cayenne
        mqttc.publish(topic_dht11_temp, payload=temp, retain=True)
        mqttc.publish(topic_dht11_humidity, payload=humidity, retain=True)
        print ("Sent to Cayenne") 
        """
        
        # Thiết lập lại chế độ hoạt động thành SLEEP để chuẩn bị nhận gói tin tiếp theo.
        self.set_mode(MODE.SLEEP)
        
        # Reset lại con trỏ nhận.
        self.reset_ptr_rx()
        
        # Quay lại chế độ nhận liên tục.
        self.set_mode(MODE.RXCONT) 


# Khởi tạo một đối tượng lora thuộc lớp LoRaRcvCont để điều khiển module LoRa.
lora = LoRaRcvCont(verbose=False)

# Thiết lập chế độ hoạt động ban đầu của module LoRa thành STDBY STAND BY (chờ).
lora.set_mode(MODE.STDBY)

# Giá trị mặc định trung mình sau init là: 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128 chips/symbol, CRC on 13 dBm
# Cấu hình công suất phát của module LoRa. pa_select: Tham số này dùng để chọn cấu hình công suất
lora.set_pa_config(pa_select=1)

''' Thay đổi config ban đầu nếu không dùng module LoRa SX1278 434.0MHz

# Thay đổi tần số sang 920MHz
lora.set_freq(920.0)

# Thay đổi băng thông sang 250kHz
lora.set_bw(250)

# Thay đổi tỷ lệ mã hóa 
lora.set_coding_rate(4)

# Thay đổi số chip mỗi symbol 
lora.set_spreading_factor(128)

# Thay đổi mức công suất phát
# lora.set_pa_config(pa_select=0, max_power=20)

'''

try:
    # Khởi động module giao tiếp LoRa
    lora.start()

# Bắt lỗi khi người dùng nhấn tổ hợp phím Ctrl+C trên bàn phím
# Thường hay dùng tổ hợp phím này trên terminal để stop chương trình
except KeyboardInterrupt:
    # sys.stdout.flush() đảm bảo bất kỳ dữ liệu nào đang được lưu trong bộ đệm stdout sẽ được in ra ngay lập tức
    sys.stdout.flush()
    print ("")
    # In ra thông báo vào luồng chuẩn lỗi stderr, Stderr thường được dùng để in ra các lỗi hoặc thông tin gỡ rối.
    sys.stderr.write("KeyboardInterrupt\n")

# Khối này sẽ luoon được thực thi bất kể có lỗi sảy ra trong khối try hay không
finally:
    sys.stdout.flush()
    print ("")
    # Gọi hàm set_mode trong đối tượng LoRa và đưa module LoRa vào chế độ ngủ
    lora.set_mode(MODE.SLEEP)
    # Giải phóng tài nguyên trên BOARD
    BOARD.teardown()
    
"""
- Tần số (Frequency): Tần số LoRa được cấp phép có thể khác nhau tùy theo khu vực. Bạn cần đảm bảo sử dụng tần số phù hợp với quy định của địa phương.
- Băng thông (Bandwidth): Băng thông cao hơn cho phép truyền dữ liệu nhanh hơn nhưng cũng giảm phạm vi.
                          Băng thông thấp hơn cho phép truyền xa hơn nhưng tốc độ dữ liệu chậm hơn.
- Tỷ lệ mã hóa (Coding Rate) : Tỷ lệ mã hóa cao hơn giúp tăng khả năng chống nhiễu nhưng cũng làm giảm tốc độ dữ liệu.
- Số chip mỗi symbol (Spreading Factor): Số chip mỗi symbol quyết định thời gian truyền một symbol.
                                         Giá trị cao hơn cho phép truyền xa hơn nhưng tốc độ dữ liệu chậm hơn.
- Kiểm tra CRC (Cyclic Redundancy Check): Bật - CRC là một thuật toán kiểm tra lỗi giúp phát hiện lỗi trong dữ liệu được truyền.
                                          Bật CRC sẽ giúp đảm bảo tính chính xác của dữ liệu được nhận.
- Công suất (Output Power): Công suất cao hơn cho phép truyền xa hơn nhưng cũng tiêu thụ nhiều pin hơn.

"""

"""
*** Luồng chạy của chương trình :

1, Thiết lập môi trường và cấu hình bảng mạch:

    import các thư viện cần thiết.
    BOARD.setup() thiết lập cấu hình cần thiết cho bảng mạch.

2, Khởi tạo lớp LoRaRcvCont:

   - Đối tượng LoRaRcvCont được khởi tạo lora = LoRaRcvCont(verbose=False).
   - Trong hàm khởi tạo (__init__), các thiết lập ban đầu của module LoRa được thực hiện:
        self.set_mode(MODE.SLEEP) đặt module LoRa vào chế độ ngủ.
        self.set_dio_mapping([0] * 6) cấu hình các chân DIO.

3, Đặt chế độ hoạt động và công suất phát:

    - lora.set_mode(MODE.STDBY) đặt module LoRa vào chế độ chờ (standby).
    - lora.set_pa_config(pa_select=1) cấu hình công suất phát của module LoRa.

4, Bắt đầu chương trình chính:
    + đây là khối lệnh chính để chạy chương trình (try-except-finally)
            try:
                lora.start()
            except KeyboardInterrupt:
                sys.stdout.flush()
                print("")
                sys.stderr.write("Bị ngắt bởi bàn phím\n")
            finally:
                sys.stdout.flush()
                print("")
                lora.set_mode(MODE.SLEEP)
                BOARD.teardown()
    
    - lora.start() được gọi để bắt đầu quá trình nhận dữ liệu liên tục.
    - Trong phương thức start:
        + self.reset_ptr_rx() đặt lại con trỏ nhận.
        + self.set_mode(MODE.RXCONT) đặt module LoRa vào chế độ nhận liên tục (continuous receive mode).
        + Một vòng lặp vô hạn (while True) bắt đầu để kiểm tra giá trị RSSI và trạng thái modem mỗi 0.5 giây:
            sleep(.5) tạo độ trễ 0.5 giây.
            rssi_value = self.get_rssi_value() lấy giá trị RSSI hiện tại.
            status = self.get_modem_status() lấy trạng thái hiện tại của modem.

  4.1 Xử lý khi có dữ liệu nhận được:

    - Khi có dữ liệu nhận được, phương thức on_rx_done sẽ được gọi (do cơ chế ngắt hoặc sự kiện trong thư viện LoRa):

        + self.clear_irq_flags(RxDone=1) xóa các cờ ngắt liên quan đến việc nhận dữ liệu.
        
        + payload = self.read_payload(nocheck=True) đọc payload (dữ liệu) nhận được.
        
        + self.set_mode(MODE.SLEEP) đặt module LoRa vào chế độ ngủ.
        
        + self.reset_ptr_rx() đặt lại con trỏ nhận.
        
        + self.set_mode(MODE.RXCONT) đặt lại module LoRa vào chế độ nhận liên tục.

  4.2 Xử lý ngoại lệ và kết thúc chương trình:

    - Khối try bao quanh lệnh lora.start() để bắt và xử lý ngoại lệ KeyboardInterrupt (khi người dùng nhấn Ctrl+C để dừng chương trình):
        + Khi KeyboardInterrupt xảy ra, thông báo được in ra và chương trình chuyển sang khối finally.
    - Trong khối finally:
        + lora.set_mode(MODE.SLEEP) đặt module LoRa vào chế độ ngủ.
        + BOARD.teardown() Giải phóng tài nguyên phần cứng được sử dụng bởi module LoRa.
  
"""

''' Tài liệu tham khảo
- Thư viện pyLoRa: https://pypi.org/project/pyLoRa/
- https://circuitdigest.com/microcontroller-projects/diy-raspberry-pi-lora-hat-for-lora-communication-between-raspberry-pi-and-arduino
- https://github.com/NguyenThongHUST/ThingsboardGateway/blob/main/lora_receive.py

'''