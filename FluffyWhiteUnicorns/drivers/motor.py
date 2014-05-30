#!/usr/bin/env python
#-------------------------------------------------------------------------------
# motor.py
# 
# DMA based PWM motor control for the Raspberry Pi.
# This requires the RPIO library and the Pi needs to be in BCM mode.
#-------------------------------------------------------------------------------
# Written by Salvatore Arpino
# Copyright 2014, Fluffy White Unicorns
#-------------------------------------------------------------------------------

# this module requires root privilege (% sudo python)
from RPIO import PWM
import math

class MotorDriver:
    MAX_SPEED = 99
    SUBCYCLE_TIME = 6000 #us

    def __init__(self, min_speed=50.0, flipLeft=False, flipRight=False):
        PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
        # each motor will use seperate dma channel (not sure if completely necessary)
        self.left_servo  = PWM.Servo(dma_channel=0,
                                     subcycle_time_us=self.SUBCYCLE_TIME)
        self.right_servo = PWM.Servo(dma_channel=1,
                                     subcycle_time_us=self.SUBCYCLE_TIME)

        # RPIO.PWM module uses BCM GPIO numbering
        self._gpio_lf = 24 # left forward
        self._gpio_lr = 23 # left rear
        self._gpio_rf = 22 # right forward
        self._gpio_rr = 27 # right rear

        # Holder for last commanded speed per motor
        self.left_speed  = 0
        self.right_speed = 0

        self.slope = math.floor(self.SUBCYCLE_TIME * (1 - min_speed/100.0) / 100.0)
        self.offset = math.floor(self.SUBCYCLE_TIME * min_speed / 100.0)

        if flipLeft:
            self.flipLeftMotor()
        if flipRight:
            self.flipRightMotor()

    @staticmethod
    def clipSpeed(speed):
        if speed > MotorDriver.MAX_SPEED:
            speed = MotorDriver.MAX_SPEED
        elif speed < -MotorDriver.MAX_SPEED:
            speed = -MotorDriver.MAX_SPEED
        return speed

    def flipLeftMotor(self):
        '''flip orientation of left motor gpio pins'''
        (self._gpio_lf, self._gpio_lr) = (self._gpio_lr, self._gpio_lf)

    def flipRightMotor(self):
        '''flip orientation of right motor gpio pins'''
        (self._gpio_rf, self._gpio_rr) = (self._gpio_rr, self._gpio_rf)

    def stopMotors(self):
        '''Ensure right and left motor are stopped'''
        # Ran into issue when motor was still running because servo failed to cleanup properly
        # so we need to explicitly stopMotors at end of program
        try:
            self.left_servo.stop_servo(self._gpio_lf)
        except:
            pass

        try:
            self.left_servo.stop_servo(self._gpio_lr)
        except:
            pass
            
        try:
            self.right_servo.stop_servo(self._gpio_rf)
        except:
            pass
            
        try:
            self.right_servo.stop_servo(self._gpio_rr)
        except:
            pass

        self.left_speed = 0
        self.right_speed = 0

    def setSpeed(self, left_speed, right_speed):
        '''set left and right motor speeds (Speed: -99 to 99)'''
        
        prev_left_speed  = self.left_speed
        prev_right_speed = self.right_speed

        left_speed = self.clipSpeed(left_speed)
        right_speed = self.clipSpeed(right_speed)

        self._setMotorSpeed(left_speed,
                            prev_left_speed,
                            self.left_servo,
                            self._gpio_lf,
                            self._gpio_lr)

        self._setMotorSpeed(right_speed,
                            prev_right_speed,
                            self.right_servo,
                            self._gpio_rf,
                            self._gpio_rr)
        
        self.left_speed = left_speed
        self.right_speed = right_speed

    def _setMotorSpeed(self,
                       speed,
                       prev_speed,
                       servo,
                       gpio_forward,
                       gpio_backward):

        if speed != prev_speed:
            if prev_speed != 0:
                if prev_speed > 0:
                    servo.stop_servo(gpio_forward)
                else:
                    servo.stop_servo(gpio_backward)
            if speed == 0:
                pass
            elif speed > 0:
                servo.set_servo(gpio_forward, int((self.slope * speed + self.offset)/10) * 10)
            else:
                servo.set_servo(gpio_backward, int((self.slope * -speed + self.offset)/10) * 10)

if __name__ == '__main__':
    # this test case requires batteries in Zumo Chassis
    import time
    try:
        m = MotorDriver()
        for i in range(-99, 100, 40):
            m.setSpeed(i, 0)
            time.sleep(1)
        for i in range(-99, 100, 40):
            m.setSpeed(0, i)
            time.sleep(1)
        m.setSpeed(99, 99)
        time.sleep(2)
        m.setSpeed(-99, -99)
        time.sleep(2)
        m.setSpeed(99, 99)
        time.sleep(2)
        m.setSpeed(0, 99)
        time.sleep(2)
        m.setSpeed(0, 0)
        time.sleep(2)
    finally:
        m.stopMotors()
