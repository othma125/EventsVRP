

class motion:
    def __init__(self, Id1: int, Id2: int):
        """
        Local search movement between two indexes
        :param Id1:
        :param Id2:
        """
        self.Index1 = Id1
        self.Index2 = Id2

    def Swap(self, li: list) -> None:
        if self.Index1 != self.Index2:
            aux = li[self.Index1]
            li[self.Index1] = li[self.Index2]
            li[self.Index2] = aux

    def _2opt(self, li: list) -> None:
        if self.Index1 < self.Index2:
            k = self.Index1
            l = self.Index2
            while k < l:
                motion(k, l).Swap(li)
                k += 1
                l -= 1
        elif self.Index1 > self.Index2:
            print('_2opt error')
            quit(0)

    def Insertion(self, li: list) -> None:
        if self.Index1 < self.Index2:
            aux = li[self.Index2]
            k = self.Index2
            while k > self.Index1:
                li[k] = li[k - 1]
                k -= 1
            li[self.Index1] = aux
        else:
            print('insertion error')
            quit(0)

    def InverseInsertion(self, li: list) -> None:
        if self.Index1 < self.Index2:
            aux = li[self.Index1]
            k = self.Index1
            while k < self.Index2:
                li[k] = li[k + 1]
                k += 1
            li[self.Index2] = aux
        else:
            print('inverse insertion error')
            quit(0)