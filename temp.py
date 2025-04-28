from datetime import datetime
import time

import smbus

bus = smbus.SMBus(1)
address = 0x77
BASE_PATH = "/home/pi/"


def read_byte(adr):
    return bus.read_byte_data(address, adr)


def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if val >= 0x8000:
        return -((0xFFFF - val) + 1)
    else:
        return val


def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)


def twos_compliment(val):
    if val >= 0x8000:
        return -((0xFFFF - val) + 1)
    else:
        return val


def get_word(array, index, twos):
    val = (array[index] << 8) + array[index + 1]
    if twos:
        return twos_compliment(val)
    else:
        return val


def calculate():
    x1 = ((temp_raw - ac6) * ac5) / 32768
    x2 = (mc * 2048) / (x1 + md)
    b5 = int(x1 + x2)
    t = (b5 + 8) / 16
    return round(t / 10, 3)


def get_temperature():
    global temp_raw
    write_byte(0xF4, 0x2E)
    time.sleep(temp_wait_period)
    temp_raw = read_word_2c(0xF6)
    temperature = calculate()
    file_path = BASE_PATH + datetime.today().strftime("%Y-%m-%d") + ".txt"
    with open(file_path, "a") as f:
        f.write(f"{datetime.now()} {temperature:.3f}\n")
    return temperature


calibration = bus.read_i2c_block_data(address, 0xAA, 22)

oss = 3
temp_wait_period = 0.004
pressure_wait_period = 0.0255

# The sensor has a block of factory set calibration values we need to
#  read these are then used in a length calculation to get the
# temperature and pressure
ac1 = get_word(calibration, 0, True)
ac2 = get_word(calibration, 2, True)
ac3 = get_word(calibration, 4, True)
ac4 = get_word(calibration, 6, False)
ac5 = get_word(calibration, 8, False)
ac6 = get_word(calibration, 10, False)
b1 = get_word(calibration, 12, True)
b2 = get_word(calibration, 14, True)
mb = get_word(calibration, 16, True)
mc = get_word(calibration, 18, True)
md = get_word(calibration, 20, True)

if __name__ == "__main__":
    for i in range(10):
        temperature = get_temperature()
        print(time.time(), temperature)
        time.sleep(1)
