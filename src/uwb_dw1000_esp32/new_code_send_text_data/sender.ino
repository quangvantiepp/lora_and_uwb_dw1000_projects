#include <SPI.h>
#include <DW1000.h>

// For ESP32 UWB Pro with Display this code run ok and send message ok

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4

// Cấu hình chân UWB cho ESP32 UWB Pro
const uint8_t PIN_RST = 27; // Chân reset
const uint8_t PIN_IRQ = 34; // Chân IRQ
const uint8_t PIN_SS = 4;   // Chân SPI select

// Biến để lưu trạng thái gửi dữ liệu
boolean sentAck = false;
int16_t sentNum = 0;

void setup()
{
    Serial.begin(115200);
    Serial.println(F("### ESP32 UWB Pro Sender ###"));
    delay(2000); // Đợi 2 giây để ESP32 sẵn sàng

    // Khởi tạo DW1000
    DW1000.begin(PIN_IRQ, PIN_RST);
    DW1000.select(PIN_SS);
    Serial.println(F("DW1000 initialized..."));

    // Cấu hình module DW1000
    DW1000.newConfiguration();
    DW1000.setDefaults();
    DW1000.setDeviceAddress(0x7D);                          // Địa chỉ thiết bị gửi (có thể thay đổi)
    DW1000.setNetworkId(0x10);                              // Network ID (giống với thiết bị nhận)
    DW1000.enableMode(DW1000.MODE_LONGDATA_RANGE_LOWPOWER); // Chế độ truyền dài
    DW1000.commitConfiguration();
    Serial.println(F("Committed configuration..."));

    // Gắn callback khi gửi tin nhắn thành công
    DW1000.attachSentHandler(handleSent);
}

void handleSent()
{
    sentAck = true;
    Serial.println("Message sent successfully.");
}

void transmitter()
{
    String msg = "Minh" + String(sentNum + 1);
    Serial.print("Transmitting message: ");
    Serial.println(msg);

    // Chuyển dữ liệu thành mảng byte thủ công
    const char *msgData = msg.c_str(); // Sử dụng c_str để lấy mảng ký tự từ chuỗi

    DW1000.newTransmit();
    DW1000.setDefaults();
    DW1000.setData((byte *)msgData, strlen(msgData) + 1); // Gửi dữ liệu và bao gồm '\0'

    DW1000.startTransmit();

    while (!DW1000.isTransmitDone())
    {
        delay(100);
    }

    if (DW1000.isTransmitDone())
    {
        Serial.println("Message sent successfully.");
    }
    else
    {
        Serial.println("Transmit error occurred.");
    }
}

void loop()
{
    // Gửi tin nhắn mỗi 3 giây
    transmitter();
    delay(3000); // Đợi 3 giây trước khi gửi tiếp

    // Tăng số thứ tự tin nhắn
    sentNum++;
}
