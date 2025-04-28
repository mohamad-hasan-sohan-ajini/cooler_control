import json

import RPi.GPIO as GPIO

from temp import get_temperature

GPIO.setmode(GPIO.BCM)


class Cooler:
    def __init__(self, pump_pin, slow_pin, speed_pin, inverse_logic, config_file):
        super(Cooler, self).__init__()
        self.pump = False
        self.pump_pin = pump_pin
        self.slow = False
        self.slow_pin = slow_pin
        self.speed = False
        self.speed_pin = speed_pin
        self.inverse_logic = inverse_logic
        self.config_file = config_file
        with open(config_file) as f:
            config = json.load(f)
        self.min_threshold = config.get("min_threshold", 26.6)
        self.max_threshold = config.get("max_threshold", 27.5)
        GPIO.setup(pump_pin, GPIO.OUT)
        GPIO.output(pump_pin, GPIO.LOW)
        GPIO.setup(slow_pin, GPIO.OUT)
        GPIO.output(slow_pin, GPIO.LOW)
        GPIO.setup(speed_pin, GPIO.OUT)
        GPIO.output(speed_pin, GPIO.LOW)
        self.control_mode = "automatic"
        self.smoothed_temperature = get_temperature()

    def set_pump(self, status):
        self.pump = status
        try:
            if self.inverse_logic ^ status:
                GPIO.output(self.pump_pin, GPIO.HIGH)
            else:
                GPIO.output(self.pump_pin, GPIO.LOW)
        except Exception as E:
            print("set pump: {}".format(status))

    def set_slow(self, status):
        self.slow = status
        try:
            if self.inverse_logic ^ status:
                GPIO.output(self.slow_pin, GPIO.HIGH)
            else:
                GPIO.output(self.slow_pin, GPIO.LOW)
        except Exception as E:
            print("set slow: {}".format(status))

    def set_speed(self, status):
        self.speed = status
        try:
            if self.inverse_logic ^ status:
                GPIO.output(self.speed_pin, GPIO.HIGH)
            else:
                GPIO.output(self.speed_pin, GPIO.LOW)
        except Exception as E:
            print("set speed: {}".format(status))

    def update_temperature(self):
        self.smoothed_temperature = (
            0.7 * self.smoothed_temperature + 0.3 * get_temperature()
        )
        self.smoothed_temperature = round(self.smoothed_temperature, 2)

    def update(self):
        self.update_temperature()
        # automatic
        if self.control_mode == "automatic":
            # low threshold
            if self.smoothed_temperature < self.min_threshold:
                self.set_pump(False)
                self.set_slow(False)
            # high threshold
            if self.smoothed_temperature > self.max_threshold:
                self.set_pump(True)
                self.set_slow(True)
