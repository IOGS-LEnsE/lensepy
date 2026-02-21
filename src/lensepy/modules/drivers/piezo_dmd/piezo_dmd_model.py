import time
import serial
from serial.tools import list_ports
from .pycrafter.pycrafter6500 import dmd


class DMDWrapper:
    """
    Wrapper class for a DMD xxx.

    # DMD operating modes:
        - mode=0 for normal video mode
        - mode=1 for pre stored pattern mode
        - mode=2 for video pattern mode
        - mode=3 for pattern on the fly mode

    """

    def __init__(self, parent=None):
        self.image = [None]*3
        self.dmd_hardware = None

    def init_dmd(self):
        if self.dmd_hardware is None:
            self.dmd_hardware = dmd()
        if self.dmd_hardware.is_dmd():
            self.dmd_hardware.reset()
            time.sleep(0.5)
            self.dmd_hardware.stopsequence()
            self.dmd_hardware.changemode(3)
            return True
        return False

    def _is_dmd_connected(self):
        """Test if the DMD is connected."""
        if self.dmd_hardware is None:
            return False
        else:
            # Send Status command
            # .command('r',0xff,0x11,0x00,[])
            #         self.readreply()
            self.dmd_hardware.command('r', 0x00, 0x1a, 0x0a, [])
            ans_list = []
            for i in self.dmd_hardware.ans:
                ans_list.append(i)
                print(hex(i))
            # Test Hardware Status Command :
            #   bit 0 = 0/Error-1/Success, bits 1/2/3 = 0/No Error
            if ans_list[0] and 0x0F == 0x01:
                return True
            else:
                return False


    def set_image(self, image, number=1):
        """
        Set image to send to the DMD.
        :param image:   2D array containing the image to send to the DMD.
        :param number:   Number of the image to set.
        """
        self.image[number-1] = image

    def get_image(self, number):
        """Get an image with its number."""
        return self.image[number-1]

    def is_images_opened(self):
        """All images are opened"""
        images_cnt = 0
        for k in range(3):
            if self.image[k] is not None:
                images_cnt += 1
        return images_cnt == 3





class PiezoWrapper:
    """Class for controlling piezoelectric motion system,
	using an interface of type Nucleo-G431KB.

    This class uses PySerial library to communicate with Nucleo board.
	The baudrate is 115200 bds.


    """

    def __init__(self):
        """
        Initialize a piezo system
		"""
        self.connected = False
        self.serial_com = None
        self.serial_link = None
        self.com_list = None
        self.read_bytes = None

    def list_serial_hardware(self):
        com_list = serial.tools.list_ports.comports()
        self.com_list = []
        for p in com_list:
            info = {
                "device": p.device,
                "description": p.description,
                "manufacturer": p.manufacturer
            }
            if info['manufacturer'].startswith('STM'):
                self.com_list.append(info)
        return self.com_list

    def set_serial_com(self, value):
        """
        Set the serial port number.
        :param value: number of the communication port - COMxx for windows
        """
        self.serial_com = value

    def connect(self):
        """
        Connect to the hardware interface via a Serial connection
        :return:    True if connection is done, else False.
		"""
        if not self.connected:
            if self.serial_com is not None:
                try:
                    self.serial_link = serial.Serial(self.serial_com, baudrate=115200)
                    self.connected = True
                    return True
                except:
                    print('Cant connect')
                    self.connected = False
                    return False
        return False

    def is_connected(self):
        """
        Return if the hardware is connected.
        :return:    True if connection is done, else False.
        """
        if self.connected:
            try:
                self.serial_link.write(b'_C!')
            except:
                print('Error Sending')
                # Timeout
            for k in range(10):
                if self.serial_link.in_waiting == 4:
                    self.read_bytes = self.serial_link.read(4).decode('utf-8')
                    if self.read_bytes[2] == '1':
                        return True
                    else:
                        return False
                else:
                    time.sleep(0.02)
        return False

    def disconnect(self):
        if self.connected:
            if self.is_connected():
                try:
                    self.serial_link.close()
                    self.connected = False
                    return True
                except:
                    print("Cant disconnect")
                    return False
        return False

    def get_position(self):
        """
        Return the position of the piezo.
        :return:    position of the piezo. pos_um, pos_nm
        """
        if self.connected:
            try:
                self.serial_link.write(b'_G!')
            except:
                print('Error Sending - GetPosition')
                # Detection of acknowledgement value
            for k1 in range(10):
                if self.serial_link.in_waiting < 2:
                    self.read_bytes = self.serial_link.read(2).decode('utf-8')
                    # if position sended
                    if self.read_bytes[1] == 'G':
                        # Detection of acknowledgement value
                        for k2 in range(10):
                            if self.serial_link.in_waiting == 7:
                                self.read_bytes = self.serial_link.read(7).decode('utf-8')
                                pos_um = 0
                                pos_nm = 0
                                if self.read_bytes[0] != ' ':
                                    pos_um += (int(self.read_bytes[0])) * 10
                                if self.read_bytes[1] != ' ':
                                    pos_um += (int(self.read_bytes[1])) * 1

                                if self.read_bytes[3] != ' ':
                                    pos_nm += (int(self.read_bytes[3])) * 100
                                if self.read_bytes[4] != ' ':
                                    pos_nm += (int(self.read_bytes[4])) * 10
                                if self.read_bytes[5] != ' ':
                                    pos_nm += (int(self.read_bytes[5])) * 1

                                return pos_um, pos_nm
                            else:
                                time.sleep(0.1)
                    else:
                        pos_um = -1
                        pos_nm = -1
                        return pos_um, pos_nm
                else:
                    time.sleep(0.1)
        print('Enf of function')
        return -1, -1

    def get_hw_version(self):
        """
        Get hardware version.
        :return:    Hardware version.
        """
        if self.connected:
            try:
                self.serial_link.write(b'_V!')
            except:
                print('Error Sending - HW Version')
                # Timeout / 1 s
            for k in range(10):
                if self.serial_link.in_waiting == 5:
                    self.read_bytes = self.serial_link.read(5).decode('utf-8')
                    return self.read_bytes[2:3]
                else:
                    time.sleep(0.01)
        return -1

    def move_position(self, pos_um, pos_nm):
        """
        Move piezo to a specific position.
        :param pos_um:  Position in um
        :param pos_np:  Position in nm
        """
        if (pos_um < 0) or (pos_um > 10):
            return False
        if (pos_nm < 0) or (pos_nm > 999):
            return False

        data = '_M'
        if pos_um < 10:
            data += ' ' + str(pos_um) + '.'
        else:
            data += str(pos_um) + '.'

        if pos_nm < 10:
            data += '  ' + str(pos_nm) + '!'
        elif pos_nm < 100:
            data += ' ' + str(pos_nm) + '!'
        else:
            data += str(pos_nm) + '!'

        if self.connected:
            try:
                self.serial_link.write(data.encode())
            except:
                print('Error Sending - movePosition')
                # Timeout / 1 s
            for k in range(10):
                if self.serial_link.in_waiting == 4:
                    self.read_bytes = self.serial_link.read(4).decode('utf-8')
                    if self.read_bytes[2] == '1':
                        return True
                    else:
                        return False
                else:
                    time.sleep(0.02)
        return False
