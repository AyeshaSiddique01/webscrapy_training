import random
from abc import ABC, abstractmethod


class IObservable(ABC):

    @abstractmethod
    def add(self, observer):
        pass

    @abstractmethod
    def remove(self, observer):
        pass

    @abstractmethod
    def notify(self, item):
        pass


class IObserver(ABC):

    @abstractmethod
    def on_update(self, item):
        pass


class Observable(IObservable):
    __max_weight = 100

    def __init__(self):
        self.observers = []
        self.weights = []

    def add(self, observer):
        self.observers.append(observer)
        observer.observable = self
        self.weights.append(self.__max_weight)

    def remove(self, observer):
        observer_index = self.observers.index(observer)
        self.observers.remove(observer)
        self.weights.remove(self.weights[observer_index])
        observer.observable = None

    def notify(self, item):
        for observer in self.observers:
            observer.on_update(item)

    def weighted_random_selection(self):
        total_weight = sum(self.weights)
        probabilities = [item / total_weight for item in self.weights]
        cumulative_probability = 0
        rand = random.uniform(0, 1)

        for index, probability in enumerate(probabilities):
            cumulative_probability += probability
            if rand < cumulative_probability:
                return index
        return None

    def update_weight(self, observer, status):
        observer_index = self.observers.index(observer)
        observer_weight = self.weights[observer_index]

        if status == "blocked":
            self.weights[observer_index] = 0
        elif status == "good":
            observer_weight += observer_weight * (0.1)
            self.weights[observer_index] = min(observer_weight, self.__max_weight)
        else:
            observer_weight -= observer_weight * (0.1)
            self.weights[observer_index] = max(observer_weight, 0)

class ProxyManager(Observable):
    def __init__(self):
        super().__init__()


class Observer(IObserver):
    def __init__(self):
        self.observable = None

    def on_update(self, item):
        print(f"{item} has been selected.")


class Proxy(Observer):

    def __init__(self, name):
        self.name = name
        super().__init__()

    def select_proxy(self, status):
        self.observable.update_weight(self, status)
