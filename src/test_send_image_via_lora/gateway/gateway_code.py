from time import sleep
import sys
import os
from datetime import datetime
from SX127x.LoRa import *
from SX127x.board_config import BOARD

# Setup LoRa board
BOARD.setup()

class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.init_file()

    def init_file(self):
        # Create directory if it does not exist
        self.directory = "received_images"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # Create a new file with a unique name
        self.filepath = os.path.join(self.directory, datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg")
        self.file = open(self.filepath, "wb")  # Open file in write binary mode

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            print("RSSI value:", rssi_value)
            print("Status value:", status)

    def on_rx_done(self):
        print("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        self.file.write(payload)  # Write received payload to file
        self.send_ack()  # Send ACK back to Arduino
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def send_ack(self):
        ack_payload = b'ACK'
        self.set_mode(MODE.STDBY)
        self.write_payload(ack_payload)
        self.set_mode(MODE.TX)
        while self.get_irq_flags()['tx_done'] == 0:
            sleep(0.1)
        self.clear_irq_flags(TxDone=1)

    def __del__(self):
        self.file.close()  # Ensure the file is closed properly

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
