from threading import Condition, Thread
import RPi.GPIO as GPIO
from queue import Queue
TILT_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class ServoController(Thread):
    ZERO = 4
    ONE_EIGHTY = 11
    def __init__(self, pin):
        super().__init__()
        self.daemon=True
        self.NINETY = (self.ZERO + self.ONE_EIGHTY)/2.
        self.pin = pin
        self.duty_cycle = self.NINETY
        GPIO.setup(self.pin,GPIO.OUT)
        self.tQ = Queue()
        self._found_something = False
        self._direction = None

    def setCycle(self,duty_cycle):
        if duty_cycle < self.ZERO:
            duty_cycle = self.ZERO
        if duty_cycle > self.ONE_EIGHTY:
            duty_cycle = self.ONE_EIGHTY

        tilt = GPIO.PWM(self.pin,50.0)
        tilt.start(8)
        tilt.ChangeDutyCycle(duty_cycle)
        time.sleep(.01)
        tilt.stop()


    def move_towards(self,point):
        """ Point should be normalized """
        if isinstance(point, tuple):
            self._found_something = True
            x, y = point
            if x < 1/6:
                self._direction = 'Left'
                self.duty_cycle += .2
                self.setCycle(self.duty_cycle)
            elif x < 1/3:
                self._direction = 'Left'
                self.duty_cycle += .1
                self.setCycle(self.duty_cycle)
            elif x > 2/3:
                self._direction = 'Right'
                self.duty_cycle -= .1
                self.setCycle(self.duty_cycle)
            elif x > 5/6:
                self._direction = 'Right'
                self.duty_cycle -= .2
                self.setCycle(self.duty_cycle)
        elif self._found_something and self._direction:
            if self._direction == 'Left':
                self.duty_cycle += .4
                self.setCycle(self.duty_cycle)
                if self.duty_cycle > self.ONE_EIGHTY:
                    self._direction = 'Right'
            elif self._direction == 'Right':
                self.duty_cycle -= .4
                self.setCycle(self.duty_cycle)
                if self.duty_cycle < self.ZERO:
                    self._direction = 'Left'

    def run(self):
        while 1:
            point = self.tQ.get()
            self.move_towards(point)

Servos = ServoController(TILT_PIN)
