import time

import RPi.GPIO as GPIO

from temp import get_temperature

GPIO.setmode(GPIO.BCM)


class Cooler():
    def __init__(self, pump_pin, slow_pin, speed_pin):
        super(Cooler, self).__init__()
        self.pump = False
        self.pump_pin = pump_pin
        self.slow = False
        self.slow_pin = slow_pin
        self.speed = False
        self.speed_pin = speed_pin
        GPIO.setup(pump_pin, GPIO.OUT)
        GPIO.output(pump_pin, GPIO.LOW)
        GPIO.setup(slow_pin, GPIO.OUT)
        GPIO.output(slow_pin, GPIO.LOW)
        GPIO.setup(speed_pin, GPIO.OUT)
        GPIO.output(speed_pin, GPIO.LOW)
        self.control_mode = 'automatic'
        self.min_threshold =  26.6
        self.max_threshold = 27.5
        self.smoothed_temperature = get_temperature()

    def set_pump(self, status):
        self.pump = status
        try:
            if status:
                GPIO.output(self.pump_pin, GPIO.HIGH)
            else:
                GPIO.output(self.pump_pin, GPIO.LOW)
        except Exception as E:
            print('set pump: {}'.format(status))

    def set_slow(self, status):
        self.slow = status
        try:
            if status:
                GPIO.output(self.slow_pin, GPIO.HIGH)
            else:
                GPIO.output(self.slow_pin, GPIO.LOW)
        except Exception as E:
            print('set slow: {}'.format(status))

    def set_speed(self, status):
        self.speed = status
        try:
            if status:
                GPIO.output(self.speed_pin, GPIO.HIGH)
            else:
                GPIO.output(self.speed_pin, GPIO.LOW)
        except Exception as E:
            print('set speed: {}'.format(status))

    def update_temperature(self):
        self.smoothed_temperature = (
            .7 * self.smoothed_temperature
            + .3 * get_temperature()
        )
        self.smoothed_temperature = round(self.smoothed_temperature, 2)

    def update(self):
        self.update_temperature()
        # automatic
        if self.control_mode == 'automatic':
            # low threshold
            if self.smoothed_temperature < self.min_threshold:
                self.set_pump(False)
                self.set_slow(False)
            # high threshold
            if self.smoothed_temperature > self.max_threshold:
                self.set_pump(True)
                self.set_slow(True)
