import itertools
import threading
from typing import List
from InputDatas import inputs
from LocalSearch import Swap, _2Opt, Insertion, InverseInsertion


class route:
    def __init__(self, Inputs: inputs, portion, LSM: bool = True, cost: float = 0, empty_space: int = 0):
        self.GiantTourPortion = portion
        self.isImprovedByLSM = LSM
        self.RouteCost: float = cost if cost >= 0 else self.getRouteCost(Inputs)
        self.EmptySpaceInVehicle: int = empty_space if empty_space >= 0 else self.getEmptySpace(Inputs)

    def getEmptySpace(self, Inputs: inputs) -> int:
        return Inputs.VehicleCapacity - sum(Inputs.getEventCapacity(event) for event in self.GiantTourPortion)

    def getRouteCost(self, Inputs: inputs) -> float:
        return Inputs.DistanceFromDepot(self.GiantTourPortion[0]) + sum(
            Inputs.Distance(event, self.GiantTourPortion[index + 1]) if index + 1 < len(
                self.GiantTourPortion) else Inputs.DistanceToDepot(event) for index, event
            in enumerate(self.GiantTourPortion))

    def TwistFeasibility(self, Inputs: inputs, EmptySpaceInVehicle: int) -> bool:
        empty_space: int = EmptySpaceInVehicle
        for event in self.GiantTourPortion:
            if Inputs.isPickupEvent[event]:
                return empty_space >= Inputs.EventsCapacity[event]
            else:
                empty_space += Inputs.EventsCapacity[event]
        return True

    def getLocalSearchMotion(self, Inputs: inputs, r):
        """
        this methode seeks to improve the current and r route by testing different inter-route motions.
        if the improvements are successful it returns the improving motion otherwise None is returned.
        :param Inputs:
        :param r:
        :return:
        """
        s1: int = sum(Inputs.getEventCapacity(event) for event in self.GiantTourPortion)
        for i in range(len(self.GiantTourPortion)):
            s2: int = 0
            for j in range(len(r.GiantTourPortion)):
                s2 += Inputs.getEventCapacity(r.GiantTourPortion[j])
                if r.EmptySpaceInVehicle + s2 >= s1 and self.EmptySpaceInVehicle + s1 >= s2:
                    _2opt = _2Opt(i, j, portion1=self.GiantTourPortion.copy(), portion2=r.GiantTourPortion.copy())
                    if _2opt.isFeasible(Inputs, self.EmptySpaceInVehicle + s1 - s2, r.EmptySpaceInVehicle + s2 - s1):
                        return _2opt
                s: int = 0
                for n in itertools.count(start=0):
                    if j + n < len(r.GiantTourPortion):
                        s += Inputs.getEventCapacity(r.GiantTourPortion[j + n])
                        if self.EmptySpaceInVehicle >= s:
                            ins1 = Insertion(False, n, i, j, portion1=self.GiantTourPortion.copy(),
                                             portion2=r.GiantTourPortion.copy())
                            if ins1.isFeasible(Inputs, self.EmptySpaceInVehicle - s, r.EmptySpaceInVehicle + s):
                                return ins1
                            if n > 0:
                                ins2 = Insertion(True, n, i, j, portion1=self.GiantTourPortion.copy(),
                                                 portion2=r.GiantTourPortion.copy())
                                if ins2.isFeasible(Inputs, self.EmptySpaceInVehicle - s, r.EmptySpaceInVehicle + s):
                                    return ins2
                        else:
                            break
                    else:
                        break
                s: int = 0
                for n in itertools.count(start=0):
                    if i - n >= 0:
                        s += Inputs.getEventCapacity(self.GiantTourPortion[i - n])
                        if r.EmptySpaceInVehicle >= s:
                            inv_ins1 = InverseInsertion(False, n, i, j, portion1=self.GiantTourPortion.copy(),
                                                        portion2=r.GiantTourPortion.copy())
                            if inv_ins1.isFeasible(Inputs, self.EmptySpaceInVehicle + s, r.EmptySpaceInVehicle - s):
                                return inv_ins1
                            if n > 0:
                                inv_ins2 = InverseInsertion(True, n, i, j, portion1=self.GiantTourPortion.copy(),
                                                            portion2=r.GiantTourPortion.copy())
                                if inv_ins2.isFeasible(Inputs, self.EmptySpaceInVehicle + s, r.EmptySpaceInVehicle - s):
                                    return inv_ins2
                        else:
                            break
                    else:
                        break
                if r.EmptySpaceInVehicle >= Inputs.getEventCapacity(self.GiantTourPortion[i]) - \
                        Inputs.getEventCapacity(r.GiantTourPortion[j]):
                    if self.EmptySpaceInVehicle >= Inputs.getEventCapacity(r.GiantTourPortion[j]) - \
                            Inputs.getEventCapacity(self.GiantTourPortion[i]):
                        swp = Swap(i, j, portion1=self.GiantTourPortion.copy(), portion2=r.GiantTourPortion.copy())
                        if swp.isFeasible(Inputs,
                                          self.EmptySpaceInVehicle - Inputs.getEventCapacity(r.GiantTourPortion[j]) +
                                          Inputs.getEventCapacity(self.GiantTourPortion[i]),
                                          r.EmptySpaceInVehicle - Inputs.getEventCapacity(self.GiantTourPortion[i]) +
                                          Inputs.getEventCapacity(r.GiantTourPortion[j])):
                            return swp
            s1 -= Inputs.getEventCapacity(self.GiantTourPortion[i])
        return None

    def getImprovedRoute(self, Inputs: inputs, targeted_cost):
        """
        this methode seeks to improve the current route cost by testing different intra-route motions.
        if the improvements are successful it returns the improved route otherwise None is returned.
        :param Inputs:
        :param targeted_cost:
        :return:
        """
        cost = self.RouteCost
        portion = self.GiantTourPortion
        for i in range(len(portion) - 1):
            for j in range(len(portion) - 1, i, -1):
                lsm = _2Opt(i, j, portion1=portion.copy())
                if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                    cost += lsm.gain
                    portion = lsm.GiantTourPortion1
                    if cost < targeted_cost:
                        return route(Inputs,
                                     portion, True, cost, self.EmptySpaceInVehicle)
                if j == i + 1:
                    continue
                for n in itertools.count(start=0):
                    if j + n < len(portion):
                        lsm = Insertion(False, n, i, j, portion1=portion.copy())
                        if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                            cost += lsm.gain
                            portion = lsm.GiantTourPortion1
                            if cost < targeted_cost:
                                return route(Inputs,
                                             portion, True, cost, self.EmptySpaceInVehicle)
                        if n > 0:
                            lsm = Insertion(True, n, i, j, portion1=portion.copy())
                            if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                                cost += lsm.gain
                                portion = lsm.GiantTourPortion1
                                if cost < targeted_cost:
                                    return route(Inputs,
                                                 portion, True, cost, self.EmptySpaceInVehicle)
                    else:
                        break
                for n in itertools.count(start=0):
                    if i - n >= 0:
                        lsm = InverseInsertion(False, n, i, j, portion1=portion.copy())
                        if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                            cost += lsm.gain
                            portion = lsm.GiantTourPortion1
                            if cost < targeted_cost:
                                return route(Inputs,
                                             portion, True, cost, self.EmptySpaceInVehicle)
                        if n > 0:
                            lsm = InverseInsertion(True, n, i, j, portion1=portion.copy())
                            if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                                cost += lsm.gain
                                portion = lsm.GiantTourPortion1
                                if cost < targeted_cost:
                                    return route(Inputs,
                                                 portion, True, cost, self.EmptySpaceInVehicle)
                    else:
                        break
                lsm = Swap(i, j, portion1=portion.copy())
                if lsm.isFeasible(Inputs, self.EmptySpaceInVehicle):
                    cost += lsm.gain
                    portion = lsm.GiantTourPortion1
                    if cost < targeted_cost:
                        return route(Inputs,
                                     portion, True, cost, self.EmptySpaceInVehicle)
        return None


class node:
    def __init__(self, i: int):
        """
        graph's node with index i
        :param i:
        """
        self.NodeIndex: int = i
        self.NodeIdInConnectionWith: int = self.NodeIndex
        self.Posterior = None
        self.Label: float = 0 if self.NodeIndex == 0 else float('inf')
        self.Routes = []
        self.Lock = threading.Lock()

    def getLabel(self):
        self.Lock.acquire()
        label = self.Label
        self.Lock.release()
        return label

    def Update(self, Id: int, Posterior=None, *new_routes):
        new_label: float = Posterior.Label + sum(r.RouteCost for r in new_routes)
        if Id >= 0:
            new_label -= Posterior.Routes[Id].RouteCost
        self.Lock.acquire()
        if new_label < self.Label:
            self.Label = new_label
            self.Posterior = Posterior
            self.Routes = [new_routes[0] if i == Id else r for i, r in enumerate(self.Posterior.Routes)]
            for j in range(0 if Id < 0 else 1, len(new_routes)):
                self.Routes.append(new_routes[j])
        self.Lock.release()

    def isFeasible(self) -> bool:
        return self.Posterior is not None


class auxiliary_graph:
    def __init__(self, giant_tour: List[int], lsm: bool):
        self.GiantTour = giant_tour
        self.withLSM = lsm
        self.Length: int = len(self.GiantTour)
        self.Nodes = [node(i) for i in range(1 + self.Length)]

    def run(self, Inputs: inputs, i: int) -> None:
        """
        run creating arcs starting from the node with index i
        :param Inputs:
        :param i:
        :return:
        """
        StartingNode: node = self.Nodes[i]
        Skip: bool = True
        FirstEvent: int = self.GiantTour[StartingNode.NodeIndex]
        EmptySpaceInVehicle: int = Inputs.VehicleCapacity
        TraveledDistance: float = Inputs.DistanceFromDepot(FirstEvent)
        CurrentPortion = []
        threads_list = []
        for j in range(StartingNode.NodeIndex, self.Length):
            event: int = self.GiantTour[j]
            EndingNode: node = self.Nodes[j + 1]
            CurrentPortion.append(event)
            EmptySpaceInVehicle -= Inputs.getEventCapacity(event)
            if EmptySpaceInVehicle < 0:
                StartingNode.NodeIdInConnectionWith = self.Length
                break
            if Inputs.isPickupEvent[event]:
                if Skip:
                    Skip = False
                else:
                    StartingNode.NodeIdInConnectionWith = self.Length
                    break
            if (Skip and not Inputs.isPickupEvent[event]) or StartingNode.Label >= EndingNode.Label:
                TraveledDistance += Inputs.Distance(event, self.GiantTour[
                    EndingNode.NodeIndex]) if EndingNode.NodeIndex < self.Length else 0
                StartingNode.NodeIdInConnectionWith += 1
                if EndingNode.NodeIndex < self.Length:
                    self.setNewThread(Inputs, EndingNode, threads_list)
                continue
            TraveledDistance += Inputs.DistanceToDepot(event)
            current_route = route(Inputs, CurrentPortion.copy(), False, TraveledDistance, EmptySpaceInVehicle)
            TwistFeasibility = current_route.TwistFeasibility(Inputs, EmptySpaceInVehicle)
            if TwistFeasibility:
                EndingNode.Update(-1, StartingNode, current_route)
            if self.withLSM:
                ImprovedRoute = None
                if j - StartingNode.NodeIndex > 1:
                    ImprovedRoute = current_route.getImprovedRoute(Inputs, EndingNode.getLabel() - StartingNode.Label)
                    if ImprovedRoute is not None:
                        EndingNode.Update(-1, StartingNode, ImprovedRoute)
                for index, r in enumerate(StartingNode.Routes):
                    lsm = r.getLocalSearchMotion(Inputs, current_route if ImprovedRoute is None else ImprovedRoute)
                    if lsm is not None:
                        new_route1 = route(Inputs, lsm.GiantTourPortion1.copy(), True, -1, -1)
                        new_route2 = route(Inputs, lsm.GiantTourPortion2.copy(), True, -1, -1)
                        EndingNode.Update(index, StartingNode, new_route1, new_route2)
                        break
            TraveledDistance += Inputs.Distance(event, self.GiantTour[
                EndingNode.NodeIndex]) if EndingNode.NodeIndex < self.Length else 0
            TraveledDistance -= Inputs.DistanceToDepot(event)
            StartingNode.NodeIdInConnectionWith += 1
            if EndingNode.NodeIndex == self.Length:
                break
            else:
                self.setNewThread(Inputs, EndingNode, threads_list)
        for t in threads_list:
            t.join()

    def setArcs(self, Inputs: inputs) -> None:
        """
        starting the splitting procedure to cluster the giant tour into feasible routes
        :param Inputs:
        :return:
        """
        self.Nodes[0].Routes = []
        t = threading.Thread(target=self.run, args=(Inputs, 0,))
        t.start()
        t.join()

    def setNewThread(self, Inputs: inputs, EndingNode: node, threads_list: node) -> None:
        """
        this methode spawn new thread that operate the method run(self, Inputs: inputs, i: int) when its time comes.
        the created thread is added to threads_list
        :param Inputs:
        :param EndingNode:
        :param threads_list:
        :return:
        """
        if not EndingNode.Lock.locked() and EndingNode.isFeasible():
            for k in range(EndingNode.NodeIndex - 1, EndingNode.Posterior.NodeIndex, -1):
                if self.Nodes[k].NodeIdInConnectionWith < EndingNode.NodeIndex:
                    return
            if EndingNode.Label < float('inf'):
                t = threading.Thread(target=self.run, args=(Inputs, EndingNode.NodeIndex,))
                threads_list.append(t)
                t.start()
            else:
                EndingNode.NodeIdInConnectionWith = self.Length

    def getLastNode(self) -> node:
        return self.Nodes[self.Length]

    def getTraveledDistance(self) -> float:
        return self.getLastNode().Label

    def getRoutesCounter(self) -> int:
        return len(self.getRoutes())

    def getRoutes(self) -> route:
        return self.getLastNode().Routes

    def getRoute(self, index: int) -> route:
        self.getRoutes()[index]

    def isFeasible(self) -> bool:
        return self.getLastNode().isFeasible()

    def isImprovedByLSM(self) -> bool:
        c = False
        for r in self.getLastNode().Routes:
            c = c or r.isImprovedByLSM
            if c:
                return True
        return False
