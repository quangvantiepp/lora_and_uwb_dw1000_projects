// Để giao tiếp giữa Arduino và Raspberry Pi,  thư viện Radiohead được sử dụng
#include <SPI.h>      // Thư viện SPI được sử dụng để giao tiếp SPI giữa các mô-đun Arduino và LoRa
#include <RH_RF95.h>  // Thư viện RH_RF95 được sử dụng cho giao tiếp LoRa
#include "DHT.h"      //  Thư viện DHT được sử dụng để đọc các giá trị nhiệt độ và độ ẩm từ cảm biến DHT.
#define DHTPIN A1     //  Chân cắm kết nối cảm biến DHT
#define DHTTYPE DHT11 // Xác định loại DHT
DHT dht(DHTPIN, DHTTYPE);
int hum;  // Lưu trữ giá trị độ ẩm
int temp; // Lưu trữ giá trị độ ẩm
RH_RF95 rf95;

void setup()
{
    Serial.begin(9600);
    dht.begin();
    if (!rf95.init())
        Serial.println("init failed");
}
void loop() //  Vòng lặp
{
    temp = dht.readTemperature();  // Đọc các giá trị nhiệt độ
    hum = dht.readHumidity();      // Đọc các giá trị độ ẩm.
    String humidity = String(hum); // Chuyển đổi các giá trị số nguyên thành một chuỗi
    String temperature = String(temp);
    String data = temperature + humidity; // Ghép 2 chuỗi lại với nhau
    Serial.println(data);                 //  Hiển thị chuỗi dữ liệu
    char d[5];                            //  Chuyển đổi các giá trị chuỗi thành một mảng char. Ở đây " data " là chuỗi và " d " là mảng char
    data.toCharArray(d, 5);               // String to char array
    Serial.println("Sending to Gateway"); // Hiển thị thông báo gửi
    rf95.send(d, sizeof(d));              // Gửi dữ liệu
    rf95.waitPacketSent();                // Đợi gói dữ liệu gửi
    Serial.println("Successfully");       // Thông báo hoàn thành
    delay(5000);                          // Tạo trễ 5 giây
}

/*
 Tài liệu tham khảo về thư viện
1. RH_RF95:
   - Trang web GitHub của thư viện: https://github.com/adafruit/RadioHead/blob/master/RH_RF95.h
   - Wiki của thư viện: https://github.com/adafruit/RadioHead/blob/master/RH_RF95.h
   - Các ví dụ về mã: https://github.com/adafruit/RadioHead/blob/master/RH_RF95.h
*/