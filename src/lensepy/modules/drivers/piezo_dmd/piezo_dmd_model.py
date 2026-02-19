import serial
from serial.tools import list_ports
import time


class DMDWrapper:
    """
    Wrapper class for a DMD xxx.
    """

    def __init__(self, parent=None):
        self.image = [None]*3


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
        self.com_list = serial.tools.list_ports.comports()
        return self.com_list

    def set_serial_com(self, value):
        """
        Set the serial port number

        Parameters
        ----------
        value : STR
            number of the communication port - COMxx for windows

        Returns
        -------
        None
        """
        self.serial_com = value
        print(self.serial_com)

    def connect(self):
        """
        Connect to the hardware interface
		via a Serial connection

        Returns
        -------
            True if connection is done
            False if not
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
        Return if the hardware is connected

        Returns
        -------
            True if hardware is connected
            False if not
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
        Return the position of the piezo

        Returns
        -------
        pos_um : INT
            position in um (integer part)
        pos_nm : INT
            position in nm (integer part)
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

        Returns
        -------
        None.

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

        Parameters
        ----------
        pos_um : INT
            um value of the piezo motion

        pos_nm : INT
            nm value of the piezo motion

        Returns
        -------
        None.

        """
        if (pos_um < 0) or (pos_um) > 10:
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
