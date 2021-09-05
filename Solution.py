import random
import threading
import time
from typing import List
from ListsEdit import motion
from InputDatas import inputs
from SplitAlgorithm import auxiliary_graph


class heuristic_solution:

    def __init__(self, Inputs: inputs, giant_tour: List[int] = None):
        """
        the constructor methode
        if giant_tour is None it generate the self.GiantTour randomly the it launch the split algorithm
        :param Inputs:
        :param giant_tour:
        """
        self.GiantTour = RandomGiantTour(Inputs.EventsCounter) if giant_tour is None else giant_tour
        self.TraveledDistance = float('inf')
        self.Split(Inputs, giant_tour is not None)

    def isFeasible(self) -> bool:
        return self.AuxiliaryGraph.isFeasible()

    def Split(self, Inputs: inputs, withLSM: bool = True) -> None:
        """
        Split algorithm that clusters the giant tour into feasible routes
        :type bound: float
        :param bound:
        :type withLSM: bool
        :param Inputs:
        :return:
        """
        self.setGraph(Inputs, withLSM)
        self.setRoutes(Inputs)

    def setGraph(self, Inputs: inputs, withLSM):
        self.AuxiliaryGraph = auxiliary_graph(self.GiantTour, withLSM)
        self.AuxiliaryGraph.setArcs(Inputs)

    def setRoutes(self, Inputs: inputs):
        if self.isFeasible():
            if self.AuxiliaryGraph.isImprovedByLSM() and self.TraveledDistance > self.AuxiliaryGraph.getTraveledDistance():
                self.TraveledDistance = self.AuxiliaryGraph.getTraveledDistance()
                self.GiantTour = [gene for r in self.AuxiliaryGraph.getRoutes() for gene in r.GiantTourPortion]
                self.Split(Inputs, random.random() < 0.1)
            else:
                self.TraveledDistance = self.AuxiliaryGraph.getTraveledDistance()
                self.RoutesCounter = self.AuxiliaryGraph.getRoutesCounter()
                self.Routes = [0 for _ in range(Inputs.EventsCounter)]
                self.GiantTour = []
                for route_index, r in enumerate(self.AuxiliaryGraph.getRoutes()):
                    for event in r.GiantTourPortion:
                        self.GiantTour.append(event)
                        self.Routes[event] = route_index

    def Crossover(self, Inputs: inputs, mother, cut_point1: int, cut_point2: int):
        """
        crossover operation generate a new solution by taking portions form the mother and father solutions (self) according to the cut points
        :param Inputs:
        :param mother:
        :param cut_point1:
        :param cut_point2:
        :return:
        """
        new_giant_tour = [self.GiantTour[i] for i in range(0 if cut_point1 == cut_point2 else cut_point1, cut_point2)]
        k = 0
        for i in range(cut_point2, len(self.GiantTour)):
            if mother.GiantTour[i] not in new_giant_tour:
                if len(new_giant_tour) < len(self.GiantTour) - cut_point1:
                    new_giant_tour.append(mother.GiantTour[i])
                else:
                    new_giant_tour.insert(k, mother.GiantTour[i])
                    k += 1
        for i in range(cut_point2):
            if mother.GiantTour[i] not in new_giant_tour:
                if len(new_giant_tour) < len(self.GiantTour) - cut_point1:
                    new_giant_tour.append(mother.GiantTour[i])
                else:
                    new_giant_tour.insert(k, mother.GiantTour[i])
                    k += 1
        Mutation(new_giant_tour)
        return heuristic_solution(Inputs, new_giant_tour)

    def toString(self, Inputs: inputs) -> str:
        """
        solution's description
        :return:
        """
        txt = f'The solution contains {self.RoutesCounter} routes\n'
        r: int = 0
        txt += f'The route number {1 + r} contains:\n'
        for event in self.GiantTour:
            if self.Routes[event] != r:
                r += 1
                txt += f'The route number {1 + r} contains:\n'
            txt += f'\tthe event {1 + event} (pickup event)\n' if Inputs.isPickupEvent[event] else f'\tthe event {1 + event}\n'
        txt += f'Solution\'s cost = {self.TraveledDistance}\n'
        return txt


class crossover_operation:
    """
    This class make the selection of the parents and the cut points then it generate two child
    """

    def __init__(self, Inputs: inputs, population: list, start_time):
        self.Inputs = Inputs
        self.start_time = start_time
        self.population = population
        Length = len(self.population) - 1
        Half = len(self.population) // 2
        index_father = random.randint(0, Half)
        self.Father = self.population[index_father]
        if random.random() < 0.7:
            while True:
                index_mother = random.randint(0, Half)
                if index_mother == index_father:
                    continue
                break
        else:
            index_mother = random.randint(Half + 1, Length)
        self.Mother = self.population[index_mother]
        self.CrossoverType = random.random() < 0.3

    def run(self):
        UpdatePopulation(self.population, self.start_time, self.Mother.Crossover(self.Inputs, self.Father, self.CutPoint1,
                                                 self.CutPoint2 if self.CrossoverType else self.CutPoint1))

    def setChilds(self):
        if self.CrossoverType:
            self.CutPoint1 = random.randint(0, len(self.Father.GiantTour) - 1)
            self.CutPoint2 = random.randint(self.CutPoint1, len(self.Father.GiantTour) - 1)
        else:
            self.CutPoint1 = random.randint(0, len(self.Father.GiantTour) - 1)
        t = threading.Thread(target=self.run())
        t.start()
        self.Child = self.Father.Crossover(self.Inputs, self.Mother, self.CutPoint1,
                                                self.CutPoint2 if self.CrossoverType else self.CutPoint1)
        t.join()
        UpdatePopulation(self.population, self.start_time, self.Child)


def GeneticAlgorithm(Inputs: inputs, RunningTime: float):
    """
    Genetic algorithm launched for a selected running time in second then it returns the best solution of the population
    :param Inputs:
    :param RunningTime:
    :return:
    """
    population_length = 20
    start_time = time.time() * 1000
    population = InitialPopulation(Inputs, population_length)
    QuickSort(population, 0, len(population) - 1)
    print(f'\t{population[0].TraveledDistance} after {int(time.time() * 1000 - start_time)} ms')
    while time.time() * 1000 - start_time < RunningTime * 1000:
        if random.random() < 0.8:
            CrossoverOperation = crossover_operation(Inputs, population, start_time)
            CrossoverOperation.setChilds()
        else:
            while True:
                new_solution = heuristic_solution(Inputs)
                if new_solution.isFeasible():
                    UpdatePopulation(population, start_time, new_solution)
                    break
    return population[0]


def InitialPopulation(Inputs: inputs, PopulationSize: int):
    """
    Randomly generated population
    :param Inputs:
    :param PopulationSize:
    :return:
    """
    population = []
    print('Initial population:')
    for _ in range(PopulationSize):
        while True:
            solution = heuristic_solution(Inputs)
            if solution.isFeasible():
                print(solution.TraveledDistance)
                population.append(solution)
                break
    return population


def UpdatePopulation(population: List[heuristic_solution], StartTime: float, solution: heuristic_solution) -> None:
    """
    this methode randomly adds a solution to the population then resorts it
    :param population:
    :param StartTime:
    :param solution:
    :return:
    """
    x = len(population) - 1
    if solution.isFeasible() and solution.TraveledDistance < population[x].TraveledDistance:
        if solution.TraveledDistance < population[0].TraveledDistance:
            print(f'\t{solution.TraveledDistance} after {int(time.time() * 1000 - StartTime)} ms')
        population[random.randint(len(population) // 2, x)] = solution
        QuickSort(population, 0, x)


def RandomGiantTour(n: int):
    """
    This methode randomly generate a giant tour
    :param n:
    :return:
    """
    new_giant_tour = list(range(n))
    for i in range(n):
        motion(i, random.randint(0, len(new_giant_tour) - 1)).Swap(new_giant_tour)
    return new_giant_tour


def Mutation(giant_tour: List[int]):
    """
    Application of a random _2opt movement on the giant tour
    :param giant_tour:
    :return:
    """
    if random.random() < 0.1:
        i = random.randint(0, len(giant_tour) - 1)
        j = random.randint(0, len(giant_tour) - 1)
        motion(min(i, j), max(i, j))._2opt(giant_tour)


def QuickSort(population: List[heuristic_solution], x: int, y: int):
    """
    Population's sorting according to the objective function
    :param population:
    :param x:
    :param y:
    :return:
    """
    if x < y:
        p = Partition(population, x, y)
        QuickSort(population, x, p - 1)
        QuickSort(population, p + 1, y)


def Partition(population: List[heuristic_solution], x: int, y: int):
    pivot = population[y].TraveledDistance
    i = x
    for j in range(x, y):
        if population[j].TraveledDistance < pivot:
            motion(i, j).Swap(population)
            i += 1
    motion(i, y).Swap(population)
    return i
