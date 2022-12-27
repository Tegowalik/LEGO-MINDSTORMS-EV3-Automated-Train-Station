#!/usr/bin/env pybricks-micropython

# https://pybricks.com/ev3-micropython/messaging.html#pybricks.messaging.BluetoothMailboxClient
from random import randint as rdm
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor, ColorSensor
from pybricks.parameters import Port, Button, Stop, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, LogicMailbox

NAME = 'ev3dev'
ev3 = EV3Brick()
station_status = {}
def run():
    server = BluetoothMailboxServer()

    distance1_box = LogicMailbox('s1', server)
    distance2_box = LogicMailbox('s4', server)
    station1_box = LogicMailbox('#1', server)
    station2_box = LogicMailbox('#2', server)
    station3_box = LogicMailbox('#3', server)
    station4_box = LogicMailbox('#4', server)
    station_boxes = [station1_box, station2_box, station3_box, station4_box]
    print('waiting for connection...')
    server.wait_for_connection(count=2)
    print('connected!')
    ev3.speaker.play_notes(['C4/4', 'G4/4'])

    wait(2000)
    print(distance1_box.read())
    m1 = Motor(Port.C)
    m2 = Motor(Port.B)
    m3 = Motor(Port.A)
    m4 = Motor(Port.D)

    sensor = ColorSensor(Port.S4)

    def sensor_active():
        r = sensor.reflection()
        return r > 0

    stations = {}
    def add_station(id, stud_len, path):
        stations[id] = {'len': stud_len, 'path': path}

    # True means straight
    add_station('#1', 16*8, [(m1, False), (m2, False), (m3, False)])
    add_station('#2', 16*12, [(m1, False), (m2, False), (m3, True)])
    add_station('#3', 16*14, [(m1, False), (m2, True)])
    add_station('#4', 16*16, [(m1, True), (m4, True)])

    backup_path = [(m1, True), (m4, False)]

    XL_turn = 50 # from True to False
    motor_config = {m1: {"position": True, "turn": XL_turn}, m2: {"position": True, "turn": XL_turn}, m3: {"position": True, "turn": XL_turn}, m4: {"position": True, "turn": XL_turn}}

    station_status = {key: True for key in stations}
    def update(box):
        s = box.read()
        if s != None:
            return s

        print("Got None")
        return True

    def update_station_status(station_status):
        station_status["#1"] = update(station1_box)
        station_status["#2"] = update(station2_box)
        station_status["#3"] = update(station3_box)
        station_status["#4"] = update(station4_box)
        #print(station_status)

    update_station_status(station_status)

    class State:

        states = {0: "ready", 1: "train passing", 2: "train not arrived at station"}

        def __init__(self):
            self.state = 0
            self.active_station = None

        def next(self):
            self.state = (self.state + 1) % len(self.states)
            
            self.set(self.state)
            return self.state
        
        def get_state(self):
            return self.state

        def set(self, value):
            self.state = value
            if self.state == 0:
                self.active_station = None
            print("New state: %s" % self.states[self.state])

        def get_state_name(self):
            return self.states[self.state]

    state = State()
    train_not_station = 0

    print("Ready")
    while True:

        if Button.CENTER in ev3.buttons.pressed():
            ev3.light.on(Color.RED)
            print("EXIT")
            # reset
            for motor in motor_config:
                config = motor_config[motor]
                if not config["position"]:
                    motor.run_angle(300, config["turn"])

            exit

        d1 = distance1_box.read()
        d2 = distance2_box.read() 

        state_name = state.get_state_name()
        sensor_is_active = sensor_active()
        if train_not_station > 15 and sensor_is_active:
            print("Another train arrives while a train is still on his way to the station, direct him to the backup path")
            train_not_station = 0
            state.set(0)
            # force backup path
            for s in station_status:
                station_status[s] = True  
            state_name = state.get_state_name()

        elif train_not_station > 100:
            print("Timeout for train to arrive the station...")
            state.set(0)
            train_not_station = 0
            state_name = state.get_state_name()

        if state_name == "ready":
            ev3.light.on(Color.GREEN)
            train_not_station = 0


            if sensor_is_active:
                available_stations = [id for id in stations if not station_status[id]]
                print("Available stations %s" % available_stations)
                if len(available_stations) > 0:
                    
                    if d1 is not None and d1:
                        available_stations = [id for id in available_stations if id not in ["#1", "#2"]]
                        print("Available stations %s" % available_stations)
                        
                        if d2 is not None and d2:
                            available_stations = [id for id in available_stations if id not in ["#3", "#4"]]
                            print("Available stations %s" % available_stations)

                # choose best train station depending on train size and availability
                
                if len(available_stations) > 0:
                    # lead the train to the best station
                    best = min(available_stations)
                    print("Best %s" % best)
                    path = stations[best]["path"]
                    state.active_station = best
                else:
                    # use backup path
                    print("Use backup path")
                    path = backup_path

                for p in path:
                    
                    motor = p[0]
                    current_position = motor_config[motor]["position"]
                    if current_position != p[1]:
                        turn = motor_config[motor]["turn"]
                        directed_turn = turn if p[1] else -turn
                        motor_config[motor]["position"] = p[1]
                        motor.run_angle(300, directed_turn)
                        print("Turn %s" % p[1])
                
                state.next()
       

        elif state_name == "train passing":
            ev3.light.on(Color.ORANGE)
            if not sensor_is_active:
                if state.active_station is not None:
                    state.next()
                else:
                    state.next()
                    state.next() 
            
        elif state_name == "train not arrived at station":
            train_not_station += 1
            ev3.light.on(Color.WHITE)
            if station_status[state.active_station]:
                if not sensor_is_active:
                    state.next() # train arrived at station -> again ready
                else:
                    print("Warning: train arrived but still a train is in front of the sensor")

        
        #print(station_status)

        ev3.screen.print("det " + ("x " if d1 else "| ") + ("x " if d2 else "| ") + ", st " + "".join(["x " if station_status[s] else "| " for s in station_status]))
        update_station_status(station_status)
        wait(100)

while True:
    try:
        run()
    except ValueError as e:
        print(e)
    ev3.light.on(Color.RED)
    ev3.speaker.beep()
    wait(10000)