#include <SPI.h>
#include <RH_RF95.h>
#include <SD.h>

#define CS_PIN 10
#define RH_RF95_FREQ 434.0

RH_RF95 rf95;

File myFile;

void setup()
{
    Serial.begin(9600);
    while (!Serial)
        ;

    if (!rf95.init())
    {
        Serial.println("LoRa init failed");
        while (1)
            ;
    }
    rf95.setFrequency(RH_RF95_FREQ);

    if (!SD.begin(CS_PIN))
    {
        Serial.println("SD card initialization failed!");
        while (1)
            ;
    }
}

void loop()
{
    myFile = SD.open("test.jpg");
    if (myFile)
    {
        Serial.println("Opened test.jpg");
        byte buffer[RH_RF95_MAX_MESSAGE_LEN];
        int packetNumber = 0;
        int bytesRead;

        while (myFile.available())
        {
            bytesRead = myFile.read(buffer, sizeof(buffer));
            bool ackReceived = false;

            while (!ackReceived)
            {
                rf95.send(buffer, bytesRead);
                rf95.waitPacketSent();
                Serial.print("Packet ");
                Serial.print(packetNumber);
                Serial.println(" sent");

                uint8_t ackBuf[RH_RF95_MAX_MESSAGE_LEN];
                uint8_t len = sizeof(ackBuf);
                if (rf95.waitAvailableTimeout(1000))
                {
                    if (rf95.recv(ackBuf, &len))
                    {
                        if (strncmp((char *)ackBuf, "ACK", 3) == 0)
                        {
                            Serial.print("ACK received for packet ");
                            Serial.println(packetNumber);
                            ackReceived = true;
                        }
                    }
                }
                if (!ackReceived)
                {
                    Serial.print("No ACK for packet ");
                    Serial.println(packetNumber);
                }
            }
            packetNumber++;
        }
        myFile.close();
        Serial.println("Done sending image");
    }
    else
    {
        Serial.println("Error opening test.jpg");
    }

    delay(10000); // Wait before sending again
}
