#!/usr/bin/env pybricks-micropython

import imp
from random import randint as rdm
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor, ColorSensor
from pybricks.parameters import Port, Button, Stop, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxClient, TextMailbox, NumericMailbox, LogicMailbox
brick = EV3Brick()

def run():
    client = BluetoothMailboxClient()

    class Sensor:

        timeout = 0
        max_timeout = 5

        def __init__(self, id) -> None:
            self.id = id
            self.mbox = LogicMailbox(id, client)
            self.d = None

        def tick(self):
            if self.is_triggered():
                self.timeout = self.max_timeout
                return False
            else:
                self.timeout = max(0, self.timeout - 1)
                return self.timeout == 0

        def is_blocked(self):
            return self.timeout > 0

        def is_triggered(self):
            return False

        def distance(self):
            return self.d

        def update(self):
            self.tick()
            self.s = self.is_triggered()
            self.mbox.send(self.s)

    class ColorSensorAdapter(Sensor):

        def __init__(self, id, port, distance=0) -> None:
            super().__init__(id)
            self.sensor = ColorSensor(port)
            self.distance = distance

        def is_triggered(self):
            self.d = self.sensor.reflection()
            return self.d > self.distance

    s1 = ColorSensorAdapter("s1", Port.S1)
    s2 = ColorSensorAdapter("s4", Port.S4)
    print("Try connect...")
    client.connect("ev3dev")
    print("Connected")
    brick.light.on(Color.GREEN)
    brick.speaker.play_notes(['C4/4', 'G4/4'])
    threshold = 30

    wait(2000)

    while True:
        s1.update()
        s2.update()
        brick.light.on(Color.GREEN)

        brick.screen.print("S1: %s, S2: %s" % (s1.s, s2.s))


        wait(100)

while True:
    try:
        run()
    except Exception as e:
        print(e)
    brick.light.on(Color.RED)
    brick.speaker.beep()
    brick.screen.print("Lost connection")
    wait(10000)
