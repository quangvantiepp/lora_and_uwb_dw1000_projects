#include <SPI.h>
#include <DW1000.h>

// For ESP32 UWB Pro with Display this code run ok and send message ok

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define UWB_RST 27 // reset pin
#define UWB_IRQ 34 // irq pin
#define UWB_SS 21  // spi select pin

#define I2C_SDA 4
#define I2C_SCL 5

// Cấu hình chân UWB cho ESP32 UWB Pro
const uint8_t PIN_RST = 27; // Chân reset
const uint8_t PIN_IRQ = 34; // Chân IRQ
const uint8_t PIN_SS = 21;  // Chân SPI select

// Biến điều khiển trạng thái
volatile boolean received = false;
volatile boolean error = false;
volatile int16_t numReceived = 0;
String message;

void setup()
{
    // Khởi tạo Serial
    Serial.begin(115200);
    Serial.println(F("### ESP32 UWB Pro Receiver ###"));

    // Khởi tạo DW1000
    DW1000.begin(PIN_IRQ, PIN_RST);
    DW1000.select(PIN_SS);
    Serial.println(F("DW1000 initialized ..."));

    // Cấu hình DW1000
    DW1000.newConfiguration();
    DW1000.setDefaults();
    DW1000.setDeviceAddress(0x86);                          // Địa chỉ thiết bị nhận (có thể thay đổi)
    DW1000.setNetworkId(0x10);                              // Network ID giống với Sender
    DW1000.enableMode(DW1000.MODE_LONGDATA_RANGE_LOWPOWER); // Chế độ truyền dài
    DW1000.commitConfiguration();
    Serial.println(F("Committed configuration ..."));

    // In thông tin thiết bị
    char msg[128];
    DW1000.getPrintableDeviceIdentifier(msg);
    Serial.print("Device ID: ");
    Serial.println(msg);
    DW1000.getPrintableExtendedUniqueIdentifier(msg);
    Serial.print("Unique ID: ");
    Serial.println(msg);
    DW1000.getPrintableNetworkIdAndShortAddress(msg);
    Serial.print("Network ID & Device Address: ");
    Serial.println(msg);
    DW1000.getPrintableDeviceMode(msg);
    Serial.print("Device mode: ");
    Serial.println(msg);

    // Gắn callback khi nhận hoặc lỗi
    DW1000.attachReceivedHandler(handleReceived);
    DW1000.attachReceiveFailedHandler(handleError);
    DW1000.attachErrorHandler(handleError);

    // Bắt đầu nhận
    receiver();
}

void handleReceived()
{
    received = true;
}

void handleError()
{
    error = true;
}

void receiver()
{
    DW1000.newReceive();
    DW1000.setDefaults();
    DW1000.receivePermanently(true); // Tự động nhận lại
    DW1000.startReceive();
}

void loop()
{
    if (received)
    {
        numReceived++;
        byte data[128];
        int len = DW1000.getDataLength(); // Lấy chiều dài dữ liệu nhận
        DW1000.getData(data, len);        // Lấy dữ liệu thô

        // Kiểm tra nếu dữ liệu không rỗng
        if (len > 0)
        {
            String receivedMsg = "";
            for (int i = 0; i < len; i++)
            {
                receivedMsg += (char)data[i];
            }

            // Hiển thị dữ liệu nhận được
            Serial.print("Received message #");
            Serial.println(numReceived);
            Serial.print("Data: ");
            Serial.println(receivedMsg);
            Serial.print("FP power (dBm): ");
            Serial.println(DW1000.getFirstPathPower());
            Serial.print("RX power (dBm): ");
            Serial.println(DW1000.getReceivePower());
            Serial.print("Signal quality: ");
            Serial.println(DW1000.getReceiveQuality());
        }
        else
        {
            Serial.println("Received empty data.");
        }

        received = false; // Đặt lại cờ
    }

    if (DW1000.isReceiveDone())
    {                                     // Kiểm tra xem đã nhận xong chưa
        byte data[128];                   // Buffer chứa dữ liệu nhận
        int len = DW1000.getDataLength(); // Lấy chiều dài dữ liệu nhận
        DW1000.getData(data, len);        // Lấy dữ liệu từ buffer

        // In ra dữ liệu nhận được
        Serial.print("Received data: ");
        for (int i = 0; i < len; i++)
        {
            Serial.print((char)data[i]);
        }
        Serial.println();

        DW1000.startReceive(); // Bắt đầu quá trình nhận tiếp theo
    }

    if (error)
    {
        Serial.println("Error receiving a message.");
        error = false; // Đặt lại cờ
    }
}
