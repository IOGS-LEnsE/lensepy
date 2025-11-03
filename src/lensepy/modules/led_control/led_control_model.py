import serial
from serial.tools import list_ports

# Exemples de VID/PID connus (optionnel) :
KNOWN_ARDUINO_VIDS = {0x2341, 0x2A03}     # Arduino officiel (varie selon modèle/édition)
KNOWN_CH340_VID = 0x1A86                  # CH340 (clones très courants)
KNOWN_FTDI_VID = 0x0403                   # FTDI USB-serial


class RGBLedWrapper:
    """
    Wrapper class for the RGB LED, via Arduino (or Nucleo).

    Commands :
        :L,W1,W2,R,G,B;  - send light value - return :L!
        :T;              - send test command - return :T!
    """

    def __init__(self, parent=None):
        self.serial_port = None


    def find_arduino_ports(self):
        """Find if an Arduino board is connected to a serial port."""
        result = []
        for p in list_ports.comports():
            info = {
                "device": p.device,
                "description": p.description,
                "hwid": p.hwid,
                "vid": p.vid,
                "pid": p.pid,
                "manufacturer": p.manufacturer,
                "product": p.product,
                "serial_number": p.serial_number,
            }

            is_arduino = False

            keywords = ("arduino", "arduino uno", "leonardo", "mega", "micro", "pro", "uno")
            combined = " ".join(filter(None, [p.description, p.manufacturer, p.product])).lower()
            if any(k in combined for k in keywords):
                is_arduino = True

            if p.vid in KNOWN_ARDUINO_VIDS or p.vid == KNOWN_CH340_VID or p.vid == KNOWN_FTDI_VID:
                is_arduino = True

            if p.device and (p.device.startswith("/dev/ttyACM") or p.device.startswith("/dev/ttyUSB")):
                is_arduino = True

            if is_arduino:
                result.append(p.device)
        return result