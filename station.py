#!/usr/bin/env pybricks-micropython


import imp
from random import randint as rdm
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor, ColorSensor
from pybricks.parameters import Port, Button, Stop, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxClient, TextMailbox, LogicMailbox

brick = EV3Brick()
def run():
    # https://pybricks.com/ev3-micropython/messaging.html
    client = BluetoothMailboxClient()
    color_map = {"#1": Color.ORANGE, "#2": Color.WHITE, "#3": Color.YELLOW, "#4": Color.GREEN}
    tunes_map = {"#1": 400, "#2": 350, "#3": 300, "#4": 200}
    config = {}

    class Sensor:

        timeout = 0
        max_timeout = 30

        def __init__(self, id) -> None:
            self.id = id
            self.mbox = LogicMailbox(id, client)
            self.d = None
            self.last = False

        def tick(self):
            if self.is_triggered():
                if not self.last:
                    brick.light.on(color_map[self.id])
                    brick.speaker.beep(tunes_map[self.id], 500)

                self.last = True

                self.timeout = self.max_timeout
                return False
            else:
                self.timeout = max(0, self.timeout - 1)
                self.last = False
                return self.timeout == 0

        def is_blocked(self):
            return self.timeout > 0

        def is_triggered(self, read=False):
            return False

        def get_d(self):
            return self.d

        def update(self):
            self.tick()
            self.mbox.send(self.is_triggered(False))

    class ColorSensorAdapter(Sensor):

        def __init__(self, id, port, distance=0) -> None:
            super().__init__(id)
            self.sensor = ColorSensor(port)
            self.distance = distance

        def is_triggered(self, read=True):
            if read:
                self.d = self.sensor.reflection()
            return self.d > self.distance

    class IRSensorAdapter(Sensor):

        def __init__(self, id, port, distance=40) -> None:
            super().__init__(id)
            self.sensor = InfraredSensor(port)
            self.distance = distance

        def is_triggered(self, read=True):
            if read:
                self.d = self.sensor.distance()
            return self.d < self.distance


    sensor1 = IRSensorAdapter('#1', Port.S1, 15)
    sensor2 = IRSensorAdapter('#2', Port.S2, 15)
    sensor3 = IRSensorAdapter('#3', Port.S3, 15)
    sensor4 = IRSensorAdapter('#4', Port.S4, 15)

    print("Try connecting...")
    client.connect("ev3dev")
    print("Connected")
    brick.light.on(Color.GREEN)
    brick.speaker.play_notes(['C4/4', 'G4/4'])
    sensor1.mbox.send(True)

    sensors = [sensor1, sensor2, sensor3, sensor4]

    while True:

        for sensor in sensors:
            sensor.update()
        config = {s.id: (s.is_triggered(False), s.get_d()) for s in sensors}
        print(config)

#        brick.screen.print(", ".join([s.get_d() for s in sorted(sensors)]))

        brick.screen.print("".join(["x " if s.is_triggered(False) else "  " for s in sorted(sensors, key=lambda s: s.id)]))

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

