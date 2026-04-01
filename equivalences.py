# equivalences.py
# CSCI 331
# S Imply Z
# by The Proof is Trivial
# author: Thomas Cosh
# date: Feb 26, 2026
# brief: defines Equivelence Class class which stores equivalences for
#        given variables ie 
#               if a|b => b = ac for some integer c
#               then the equivalance class of b = B = {b, ac}
# THIS FILE IS COMPLETELY UNUSED AT THIS POINT
# IT IS ONLY BEING LEFT BEHIND FOR REFERENCE
from collections import UserList, UserDict
from copy import deepcopy

class EquivalenceClass(UserDict):

    def __init__(self, data: dict = None) -> None:
        super().__init__()

        if data:
            for key, value in data.items():
                self[key] = value

    def __or__(self, other: EquivalenceClass) -> EquivalenceClass:

        result = EquivalenceClass(deepcopy(self.data))

        for key, value in other.data.items():

            if key not in result.data.keys():
                result[key] = value
            else:
                result[key].update(value)

        return result
    
    def __setitem__(self, key: str, value) -> None:

        if isinstance(value, set):
            super().__setitem__(key, value)
        elif isinstance(value, (list, tuple)):
            super().__setitem__(key, set(value))
        else:
            super().__setitem__(key, {value})

class World(UserList):

    def __init__(self, elements: list = None):

        super().__init__()

        if elements:
            for element in elements:
                if isinstance(element, EquivalenceClass):
                    self.data.append(element)
                else:
                    self.data.append(EquivalenceClass(element))

    def __setitem__(self, index: int, value) -> None:

        if isinstance(value, EquivalenceClass):
            self.data[index] = value
        else:
            self.data[index] = EquivalenceClass(value)

    def append(self, value) -> None:

        if isinstance(value, EquivalenceClass):
            self.data.append(value)
        else:
            self.data.append(EquivalenceClass(value))

    def __add__(self, other: World) -> World:

        result = World(deepcopy(self.data))
        for eq in other.data:
            if eq not in result.data:
                result.append(eq)

        return result

    def __mul__(self, other: World) -> World:

        result = World()
        for case in self.data:
            for c in other.data:
                result.append(deepcopy(case | c))

        return result





if __name__ == '__main__':


    w1 = World(
        [
            {'a': 'xe', 'e': set(), 'x': set()},
            {'b': 'xf', 'f': set(), 'x': set()}
        ])
    print('w1: ', w1)

    w2 = World(
        [
            {'c': 'yg', 'y': set(), 'g': set()},
            {'d': 'yh', 'y': set(), 'h': set()}
        ])
    print('w2: ', w2)

    print('w1 + w2:', w1 + w2)
    for i, case in enumerate(w1 + w2):
        print('Case ', i, ': ', case)

    print('w1 x w2', w1*w2)
    for i, case in enumerate(w1*w2):
        print('Case ', i, ': ', case)
