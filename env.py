import optparse
import gym
from gym.spaces import Discrete, Box
import os
import sys
import optparse

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME")

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                        default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

from sumolib import checkBinary
import traci


class SumoEnv(gym.Env):
    def __init__(self):
        options = get_options()
        if options.nogui:
            self._sumoBinary = checkBinary('sumo')
        else:
            self._sumoBinary = checkBinary('sumo-gui')

        self.sumoCmd = [self._sumoBinary, "-c", "demo.sumocfg", "--tripinfo-output", "tripinfo.xml", "--no-internal-links", "false"]

        self.gymStep = 0
        self.busStops = ["stop1", "stop2"]
        self.stoppedBuses = [None, None]
        self.decisionBus = "bus.0"

        traci.start(self.sumoCmd)


    def step(self, action):

        self.gymStep += 1
        print("new gym step ", self.gymStep)

        

        #####################
        #   APPLY ACTION    #
        #####################
        if traci.simulation.getTime() > 1: #the first bus leaves after the first simulation step
            if action == 0: # hold the bus
                stopData = traci.vehicle.getStops(self.decisionBus, 1)
                traci.vehicle.setBusStop(self.decisionBus, stopData[0].stoppingPlaceID, duration=70)
                print("holding {} at {}".format(self.decisionBus, stopData[0].stoppingPlaceID))
            elif action == 1: # skip the stop
                stopData = traci.vehicle.getStops(self.decisionBus, 1)
                traci.vehicle.setBusStop(self.decisionBus, stopData[0].stoppingPlaceID, duration=0)
            #else action == 2, no action taken and bus behaves normally


        ########################################
        #   FAST FORWARD TO NEXT DECISION STEP #
        ########################################
        # self.sumoStep()
        # while len(self.stoppedBuses()) < 1:
        #     self.sumoStep()


        # self.sumoStep() # CHECK ############
        reachedStopBuses = self.reachedStop()
        while len(reachedStopBuses) < 1:
            self.sumoStep()
            reachedStopBuses = self.reachedStop()

        ###### UPDATE DECISION BUS #######
        self.decisionBus = str(list(reachedStopBuses.keys())[0])


        ###############################################
        #   GET NEW OBSERVATION AND CALCULATE REWARD  #
        ###############################################

        state = {}

        reward = 0

        if self.gymStep > 10:
            print(self.gymStep)
            done = True
            
        else:
            done = False

        info = {}

        return state, reward, done, info


    def reset(self):
        traci.close()
        traci.start(self.sumoCmd)
        self.gymStep = 0
        self.stoppedBuses = [None, None]
        self.decisionBus = "bus.0"

    def close(self):
        traci.close()

    def stoppedBuses(self):
        stopped = dict()
        for stop in ["stop1", "stop2"]:
            buses = traci.busstop.getVehicleIDs(stop)
            for bus in buses:
                stopped[bus] = stop
        return stopped

    def newStoppedBus(self):   
        stopped = dict() 
        for vehicle in traci.vehicle.getIDList():
            if vehicle[0:3] == "bus":
                if traci.vehicle.isAtBusStop(vehicle):
                    if self.stoppedBuses[int(vehicle[-1])] == None:
                        print(vehicle)
                        #get stop id and update stoppedBuses list
                        for stop in self.busStops:
                            buses = traci.busstop.getVehicleIDs(stop)
                            if vehicle in buses:
                                self.stoppedBuses[int(vehicle[-1])] = stop
                                stopped[vehicle] = stop

                else:
                    if self.stoppedBuses[int(vehicle[-1])] != None:
                        self.stoppedBuses[int(vehicle[-1])] = None

        # for vehicle in traci.simulation.getStopStartingVehiclesIDList():
        #     if vehicle[0:3] == "bus":
        #         for stop in self.busStops:
        #             buses = traci.busstop.getVehicleIDs(stop)
        #             if vehicle in buses:
        #                 self.stoppedBuses[int(vehicle[-1])] = stop
        #                 stopped[vehicle] = stop
        # for vehicle in traci.simulation.getStopEndingVehiclesIDList():
        #     if vehicle[0:3] == "bus":
        #         self.stoppedBuses[int(vehicle[-1])] = None
        return stopped

    def reachedStop(self):
        reached = dict()
        for vehicle in traci.vehicle.getIDList():
            if vehicle[0:3] == "bus":
                for stop in self.busStops:
                    if traci.busstop.getLaneID(stop) == traci.vehicle.getLaneID(vehicle):
                        if (traci.vehicle.getLanePosition(vehicle) >= (traci.busstop.getStartPos(stop) - 5)) and (traci.vehicle.getLanePosition(vehicle) <= (traci.busstop.getEndPos(stop) + 1)):
                            if self.stoppedBuses[int(vehicle[-1])] == None:
                                # get stop id and update stopped bused list
                                self.stoppedBuses[int(vehicle[-1])] = stop
                                reached[vehicle] = stop
                        else:
                            if self.stoppedBuses[int(vehicle[-1])] != None:
                                self.stoppedBuses[int(vehicle[-1])] = None
        
        return reached


    def sumoStep(self):
        traci.simulationStep()



env = SumoEnv()
episodes = 3
for episode in range(1, episodes + 1):

    state = env.reset()

    done = False
    score = 0

    while not done:
        state, reward, done, info = env.step(10)
        score += reward

    print("Episode: {} Score: {}".format(episode, score))

env.close()


    