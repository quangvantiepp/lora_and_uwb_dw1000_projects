// Receiver new code for test
#include <SPI.h>
#include "DW1000Ranging.h"
#include "DW1000.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define ANCHOR_ADD "86:17:5B:D5:A9:9A:E2:9C"
#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define UWB_RST 27 // reset pin
#define UWB_IRQ 34 // irq pin
#define UWB_SS 21  // spi select pin

#define I2C_SDA 4
#define I2C_SCL 5

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup()
{
    Serial.begin(115200);

    Wire.begin(I2C_SDA, I2C_SCL);
    delay(1000);

    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
    {
        Serial.println(F("SSD1306 allocation failed"));
        for (;;)
            ;
    }
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println(F("Receiver Ready"));
    display.display();

    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(UWB_RST, UWB_SS, UWB_IRQ);

    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachBlinkDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    DW1000Ranging.startAsAnchor(ANCHOR_ADD, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);
}

void loop()
{
    DW1000Ranging.loop();
    // Check Received Data
    checkForReceivedData();
}

void newRange()
{
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print(", ");
    Serial.println(DW1000Ranging.getDistantDevice()->getRange());
}

void newDevice(DW1000Device *device)
{
    Serial.print("Device added: ");
    Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device)
{
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);
}

void checkForReceivedData()
{
    if (DW1000.available())
    {
        uint8_t message[128];
        // Receive data
        int len = DW1000.getData(message, 128);
        // Add a flag to the end index of the message array
        message[len] = '\0';
        Serial.print("Received message: ");
        // Show message on serial Monitor in Arduino IDE
        Serial.println((char *)message);

        display.clearDisplay();
        display.setCursor(0, 0);
        display.setTextSize(2);
        // Show message on display
        display.println((char *)message);
        display.display();
    }
}
