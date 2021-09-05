import math
import random


class inputs:
    def __init__(self, file_name: str):
        """
        input file reading
        :param file_name:
        """
        with open("instances\\" + file_name, "r") as file:
            line = file.readline()
            word = line.split()
            self.EventsCounter: int = int(word[0])
            self.VehicleCapacity: int = int(word[1])
            self.EventsCapacity = []
            self.Coordinates = []
            c = False
            for _ in range(self.EventsCounter + 1):
                line = file.readline()
                word = line.split()
                self.Coordinates.append([float(word[0]), float(word[1])])
                if c:
                    self.EventsCapacity.append(int(word[2]))
                else:
                    c = True
        self.DistanceMatrix = [[0 for _ in range(self.EventsCounter + 1)] for _ in range(self.EventsCounter + 1)]
        # 30% of stops are selected randomly to be pickup events
        self.isPickupEvent = [random.random() < 0.3 for _ in range(self.EventsCounter)]

    def Distance(self, i, j) -> float:
        """
        euclidean distance between two stops
        :param i:
        :param j:
        :return:
        """
        if self.DistanceMatrix[i + 1][j + 1] == 0 and i != j:
            self.DistanceMatrix[i + 1][j + 1] = math.sqrt(
                (self.Coordinates[j + 1][0] - self.Coordinates[i + 1][0]) ** 2 + (
                        self.Coordinates[j + 1][1] - self.Coordinates[i + 1][1]) ** 2)
        return self.DistanceMatrix[i + 1][j + 1]

    def DistanceToDepot(self, i) -> float:
        """
        euclidean distance from the stop i to the depot with index 0
        :param i:
        :return:
        """
        if self.DistanceMatrix[i + 1][0] == 0:
            self.DistanceMatrix[i + 1][0] = math.sqrt((self.Coordinates[i + 1][0] - self.Coordinates[0][0]) ** 2 + (
                    self.Coordinates[i + 1][1] - self.Coordinates[0][1]) ** 2)
        return self.DistanceMatrix[i + 1][0]

    def DistanceFromDepot(self, i) -> float:
        """
        euclidean distance from the depot to the stop i
        :param i:
        :return:
        """
        if self.DistanceMatrix[0][i + 1] == 0:
            self.DistanceMatrix[0][i + 1] = math.sqrt((self.Coordinates[0][0] - self.Coordinates[i + 1][0]) ** 2 + (
                    self.Coordinates[0][1] - self.Coordinates[i + 1][1]) ** 2)
        return self.DistanceMatrix[0][i + 1]

    def getEventCapacity(self, event: int):
        return 0 if self.isPickupEvent[event] else self.EventsCapacity[event]
