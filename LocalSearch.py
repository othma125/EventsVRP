from ListsEdit import motion
from InputDatas import inputs


class local_search_motion:
    """
    this class manage the local search motions that may be applied on a giant tour portion or between two portions
    """

    def __init__(self, i: int, j: int, **portions):
        self.I: int = i
        self.J: int = j
        self.IntraPortion = len(portions) == 1
        self.Border: int = len(portions['portion1'] if self.IntraPortion else portions['portion2'])
        self.GiantTourPortion1 = portions['portion1']
        self.GiantTourPortion2 = portions['portion1'] if self.IntraPortion else portions['portion2']
        self.gain: float = 0


class _2Opt(local_search_motion):
    def __init__(self, i: int, j: int, **portions):
        super().__init__(i, j, **portions)
        self.Name = 'inverse insertion'

    def isFeasible(self, Inputs: inputs, *empty_spaces) -> bool:
        """
        only the motions that gives feasible result regarding the twist constraint are selected
        :rtype: * int
        :param Inputs:
        :return:
        """
        if not self.IntraPortion:
            s1 = sum(1 if Inputs.isPickupEvent[self.GiantTourPortion1[i]] else 0 for i in range(self.I, len(self.GiantTourPortion1)))
            s2 = sum(1 if Inputs.isPickupEvent[self.GiantTourPortion2[i]] else 0 for i in range(self.J+1))
            if s1 != s2:
                return False
        self.setGain(Inputs)
        if self.gain >= 0:
            return False
        self.Execution()
        # twist feasibility
        EmptySpaceInVehicle: int = empty_spaces[0]
        for event in self.GiantTourPortion1:
            if Inputs.isPickupEvent[event]:
                if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                    return False
                break
            else:
                EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        if not self.IntraPortion:
            EmptySpaceInVehicle: int = empty_spaces[1]
            for event in self.GiantTourPortion2:
                if Inputs.isPickupEvent[event]:
                    if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                        return False
                    break
                else:
                    EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        return True

    def Execution(self) -> None:
        """
        this methode execute _2opt motion on two portions
        Example:
            Original portion: (1) -> [--1--][--2--][--3--]    (2) -> [--4--][--5--][--6--][--7--][--8--]
            Moved events:                from [--2--] to [--6--]
            Expected portion: (1) -> [--1--][--6--][--5--][--4--]    (2) -> [--3--][--2--][--7--][--8--]
        """
        if self.IntraPortion:
            motion(self.I, self.J)._2opt(self.GiantTourPortion1)
        else:
            l1 = [self.GiantTourPortion1[i] for i in range(self.I)]
            for i in range(self.J, -1, -1):
                l1.append(self.GiantTourPortion2[i])
            l2 = [self.GiantTourPortion2[i] for i in range(self.J + 1, len(self.GiantTourPortion2))]
            for i in range(len(self.GiantTourPortion1) - 1, self.I - 1, -1):
                l2.insert(0, self.GiantTourPortion1[i])
            self.GiantTourPortion1 = l1
            self.GiantTourPortion2 = l2

    def setGain(self, Inputs: inputs) -> None:
        if self.I == 0:
            self.gain += Inputs.DistanceFromDepot(self.GiantTourPortion2[self.J])
            self.gain -= Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I])
        else:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.I - 1],
                                         self.GiantTourPortion2[self.J])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I - 1],
                                         self.GiantTourPortion1[self.I])
        if self.J + 1 < self.Border:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.I],
                                         self.GiantTourPortion2[self.J + 1])
            self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J],
                                         self.GiantTourPortion2[self.J + 1])
        else:
            self.gain += Inputs.DistanceToDepot(self.GiantTourPortion1[self.I])
            self.gain -= Inputs.DistanceToDepot(self.GiantTourPortion2[self.J])


class Swap(local_search_motion):
    def __init__(self, i: int, j: int, **portions):
        super().__init__(i, j, **portions)
        self.FirstBorder = len(self.GiantTourPortion1)
        self.Name = 'inverse insertion'

    def isFeasible(self, Inputs: inputs, *empty_spaces) -> bool:
        """
        only the motions that gives feasible result regarding the twist constraint are selected
        :rtype: * int
        :param Inputs:
        :return:
        """
        if not self.IntraPortion and Inputs.isPickupEvent[self.GiantTourPortion1[self.I]] != Inputs.isPickupEvent[
            self.GiantTourPortion2[self.J]]:
            return False
        self.setGain(Inputs)
        if self.gain >= 0:
            return False
        self.Execution()
        # twist feasibility
        EmptySpaceInVehicle: int = empty_spaces[0]
        for event in self.GiantTourPortion1:
            if Inputs.isPickupEvent[event]:
                if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                    return False
                break
            else:
                EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        if not self.IntraPortion:
            EmptySpaceInVehicle: int = empty_spaces[1]
            for event in self.GiantTourPortion2:
                if Inputs.isPickupEvent[event]:
                    if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                        return False
                    break
                else:
                    EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        return True

    def Execution(self) -> None:
        """
        this methode execute Swap motion on two portions
        exchange the place of two events, an event from portion1 and the other from the portion2.
        Example:
            Original portion: (1) -> [--1--][--2--][--3--]    (2) -> [--4--][--5--][--6--][--7--][--8--]
            Exchanged events:                [--2--] and [--6--]
            Expected portion: (1) -> [--1--][--6--][--3--]    (2) -> [--4--][--5--][--2--][--7--][--8--]
        """
        if self.IntraPortion:
            motion(self.I, self.J).Swap(self.GiantTourPortion1)
        else:
            aux: int = self.GiantTourPortion1[self.I]
            self.GiantTourPortion1[self.I] = self.GiantTourPortion2[self.J]
            self.GiantTourPortion2[self.J] = aux

    def setGain(self, Inputs: inputs) -> None:
        if self.I == 0:
            self.gain += Inputs.DistanceFromDepot(self.GiantTourPortion2[self.J])
            self.gain -= Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I])
        else:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.I - 1],
                                         self.GiantTourPortion2[self.J])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I - 1],
                                         self.GiantTourPortion1[self.I])
        if self.I + 1 < self.J and self.IntraPortion:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.J - 1],
                                         self.GiantTourPortion1[self.I])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.J - 1],
                                         self.GiantTourPortion1[self.J])
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.J],
                                         self.GiantTourPortion1[self.I + 1])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I],
                                         self.GiantTourPortion1[self.I + 1])
        elif not self.IntraPortion:
            self.gain += Inputs.Distance(self.GiantTourPortion2[self.J - 1],
                                         self.GiantTourPortion1[self.I]) if self.J > 0 else Inputs.DistanceFromDepot(
                self.GiantTourPortion1[self.I])
            self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J - 1],
                                         self.GiantTourPortion2[self.J]) if self.J > 0 else Inputs.DistanceFromDepot(
                self.GiantTourPortion2[self.J])
            self.gain += Inputs.Distance(self.GiantTourPortion2[self.J],
                                         self.GiantTourPortion1[
                                             self.I + 1]) if self.I + 1 < self.FirstBorder else Inputs.DistanceToDepot(
                self.GiantTourPortion2[self.J])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I],
                                         self.GiantTourPortion1[
                                             self.I + 1]) if self.I + 1 < self.FirstBorder else Inputs.DistanceToDepot(
                self.GiantTourPortion1[self.I])
        if self.J + 1 < self.Border:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.I],
                                         self.GiantTourPortion2[self.J + 1])
            self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J],
                                         self.GiantTourPortion2[self.J + 1])
        else:
            self.gain += Inputs.DistanceToDepot(self.GiantTourPortion1[self.I])
            self.gain -= Inputs.DistanceToDepot(self.GiantTourPortion2[self.J])


class Insertion(local_search_motion):
    def __init__(self, with2opt: bool, n: int, i: int, j: int, **portions):
        super().__init__(i, j, **portions)
        self.N: int = n
        self.With2Opt: bool = with2opt
        self.Name: str = 'inverse insertion'

    def isFeasible(self, Inputs: inputs, *empty_spaces) -> bool:
        """
        only the motions that gives feasible result regarding the twist constraint are selected
        :rtype: * int
        :param Inputs:
        :return:
        """
        if not self.IntraPortion:
            for k in range(self.N + 1):
                if Inputs.isPickupEvent[self.GiantTourPortion2[self.J + k]]:
                    return False
        self.setGain(Inputs)
        if self.gain >= 0:
            return False
        self.Execution()
        # twist feasibility
        EmptySpaceInVehicle: int = empty_spaces[0]
        for event in self.GiantTourPortion1:
            if Inputs.isPickupEvent[event]:
                if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                    return False
                break
            else:
                EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        if not self.IntraPortion:
            EmptySpaceInVehicle: int = empty_spaces[1]
            for event in self.GiantTourPortion2:
                if Inputs.isPickupEvent[event]:
                    if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                        return False
                    break
                else:
                    EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        return True

    def Execution(self) -> None:
        """
        this methode execute Insertion motion between two portions
        inserts an event from portion2 into the portion1.
        Example:
            Original portion: (1) -> [--1--][--2--][--3--]    (2) -> [--4--][--5--][--6--][--7--][--8--]
            Inserted events:                [--5--][--6--] in place of [--3--] with a 2opt included
            Expected portion: (1) -> [--1--][--2--][--6--][--5--][--3--]    (2) -> [--4--][--7--][--8--]
            Inserted events:                [--5--][--6--] in place of [--3--] without a 2opt included
            Expected portion: (1) -> [--1--][--2--][--5--][--6--][--3--]    (2) -> [--4--][--7--][--8--]
        """
        if self.IntraPortion:
            for k in range(self.N + 1):
                motion(self.I if self.With2Opt else self.I + k, self.J + k).Insertion(self.GiantTourPortion1)
        else:
            for k in range(self.N + 1):
                self.GiantTourPortion1.insert(self.I if self.With2Opt else self.I + k,
                                              self.GiantTourPortion2[self.J + k])
            for _ in range(self.N + 1):
                self.GiantTourPortion2.pop(self.J)

    def setGain(self, Inputs: inputs):
        self.gain -= Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I]) if self.I == 0 else Inputs.Distance(
            self.GiantTourPortion1[self.I - 1], self.GiantTourPortion1[self.I])
        if self.With2Opt:
            self.gain += Inputs.Distance(self.GiantTourPortion2[self.J],
                                         self.GiantTourPortion1[self.I])
            self.gain += Inputs.DistanceFromDepot(
                self.GiantTourPortion2[self.J + self.N]) if self.I == 0 else Inputs.Distance(
                self.GiantTourPortion1[self.I - 1],
                self.GiantTourPortion2[self.J + self.N])
        else:
            self.gain += Inputs.Distance(self.GiantTourPortion2[self.J + self.N],
                                         self.GiantTourPortion1[self.I])
            self.gain += Inputs.DistanceFromDepot(self.GiantTourPortion2[self.J]) if self.I == 0 else Inputs.Distance(
                self.GiantTourPortion1[self.I - 1],
                self.GiantTourPortion2[self.J])
        self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J - 1],
                                     self.GiantTourPortion2[
                                         self.J]) if self.J > 0 or self.IntraPortion else Inputs.DistanceFromDepot(
            self.GiantTourPortion2[self.J])
        if self.J + self.N + 1 < self.Border:
            self.gain += Inputs.Distance(self.GiantTourPortion2[self.J - 1],
                                         self.GiantTourPortion2[
                                             self.J + self.N + 1]) if self.J > 0 or self.IntraPortion else Inputs.DistanceFromDepot(
                self.GiantTourPortion2[self.J + self.N + 1])
            self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J + self.N],
                                         self.GiantTourPortion2[self.J + self.N + 1])
        else:
            self.gain += Inputs.DistanceToDepot(
                self.GiantTourPortion2[self.J - 1]) if self.J > 0 or self.IntraPortion else 0
            self.gain -= Inputs.DistanceToDepot(self.GiantTourPortion2[self.J + self.N])


class InverseInsertion(local_search_motion):
    def __init__(self, with2opt: bool, n: int, i: int, j: int, **portions):
        super().__init__(i, j, **portions)
        self.N: int = n
        self.With2Opt: bool = with2opt
        self.FirstBorder = len(self.GiantTourPortion1)
        self.Name: str = 'inverse insertion'

    def isFeasible(self, Inputs: inputs, *empty_spaces) -> bool:
        """
        only the motions that gives feasible result regarding the twist constraint are selected
        :rtype: * int
        :param Inputs:
        :return:
        """
        if not self.IntraPortion:
            for k in range(self.N + 1):
                if Inputs.isPickupEvent[self.GiantTourPortion1[self.I - k]]:
                    return False
        self.setGain(Inputs)
        if self.gain >= 0:
            return False
        self.Execution()
        # twist feasibility
        EmptySpaceInVehicle: int = empty_spaces[0]
        for event in self.GiantTourPortion1:
            if Inputs.isPickupEvent[event]:
                if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                    return False
                break
            else:
                EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        if not self.IntraPortion:
            EmptySpaceInVehicle: int = empty_spaces[1]
            for event in self.GiantTourPortion2:
                if Inputs.isPickupEvent[event]:
                    if EmptySpaceInVehicle < Inputs.EventsCapacity[event]:
                        return False
                    break
                else:
                    EmptySpaceInVehicle += Inputs.EventsCapacity[event]
        return True

    def Execution(self) -> None:
        """
        this methode execute Inverse Insertion motion between portions
        inserts an event from portion1 into the portion2.
        Example:
            Original portion: (1) -> [--1--][--2--][--3--]    (2) -> [--4--][--5--][--6--][--7--][--8--]
            Inserted events:                [--1--][--2--] in place of [--6--] with a 2opt included
            Expected portion: (1) -> [--3--]    (2) -> [--4--][--5--][--6--][--2--][--1--][--7--][--8--]
            Inserted events:                [--1--][--2--] in place of [--6--] without a 2opt included
            Expected portion: (1) -> [--3--]    (2) -> [--4--][--5--][--6--][--1--][--2--][--7--][--8--]
        """
        if self.IntraPortion:
            for k in range(self.N + 1):
                motion(self.I - k, self.J if self.With2Opt else self.J - k).InverseInsertion(self.GiantTourPortion1)
        else:
            if len(self.GiantTourPortion2) == 0:
                if self.With2Opt:
                    self.GiantTourPortion2 = self.GiantTourPortion1[self.I: self.I - self.N - 1: -1]
                else:
                    self.GiantTourPortion2 = self.GiantTourPortion1[self.I - self.N: self.I + 1]
            else:
                for k in range(self.N + 1):
                    self.GiantTourPortion2.insert(self.J + 1 + k if self.With2Opt else self.J + 1,
                                                  self.GiantTourPortion1[self.I - k])
            for _ in range(self.N + 1):
                self.GiantTourPortion1.pop(self.I - self.N)

    def setGain(self, Inputs: inputs):
        if self.Border == 0:
            if self.With2Opt:
                self.gain += Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I])
                self.gain += Inputs.DistanceToDepot(self.GiantTourPortion1[self.I - self.N])
            else:
                self.gain += Inputs.DistanceToDepot(self.GiantTourPortion1[self.I])
                self.gain += Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I - self.N])
        else:
            self.gain -= Inputs.Distance(self.GiantTourPortion2[self.J], self.GiantTourPortion2[
                self.J + 1]) if self.J + 1 < self.Border else Inputs.DistanceToDepot(
                self.GiantTourPortion2[self.J])
            if self.With2Opt:
                self.gain += Inputs.Distance(self.GiantTourPortion2[self.J], self.GiantTourPortion1[self.I])
                self.gain += Inputs.Distance(self.GiantTourPortion1[self.I - self.N],
                                             self.GiantTourPortion2[self.J + 1]) \
                    if self.J + 1 < self.Border else Inputs.DistanceToDepot(self.GiantTourPortion1[self.I - self.N])
            else:
                self.gain += Inputs.Distance(self.GiantTourPortion2[self.J], self.GiantTourPortion1[self.I - self.N])
                self.gain += Inputs.Distance(self.GiantTourPortion1[self.I],
                                             self.GiantTourPortion2[self.J + 1]) \
                    if self.J + 1 < self.Border else Inputs.DistanceToDepot(self.GiantTourPortion1[self.I])
        self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I],
                                     self.GiantTourPortion1[self.I + 1]) \
            if self.I + 1 < self.FirstBorder or self.IntraPortion else Inputs.DistanceToDepot(
            self.GiantTourPortion1[self.I])
        if self.I - self.N == 0:
            self.gain += Inputs.DistanceFromDepot(
                self.GiantTourPortion1[self.I + 1]) if self.I + 1 < self.FirstBorder or self.IntraPortion else 0
            self.gain -= Inputs.DistanceFromDepot(self.GiantTourPortion1[self.I - self.N])
        else:
            self.gain += Inputs.Distance(self.GiantTourPortion1[self.I - self.N - 1],
                                         self.GiantTourPortion1[
                                             self.I + 1]) if self.I + 1 < self.FirstBorder or self.IntraPortion else Inputs.DistanceToDepot(
                self.GiantTourPortion1[self.I - self.N - 1])
            self.gain -= Inputs.Distance(self.GiantTourPortion1[self.I - self.N - 1],
                                         self.GiantTourPortion1[self.I - self.N])
