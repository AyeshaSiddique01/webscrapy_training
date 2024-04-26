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
    def __init__(self):
        self.observers = []

    def add(self, observer):
        self.observers.append(observer)
        observer.observable = self

    def remove(self, observer):
        self.observers.remove(observer)
        observer.observable = None

    def notify(self, item):
        for observer in self.observers:
            observer.on_update(item)


class Observer(IObserver):
    def __init__(self):
        self.observable = None

    def on_update(self, item):
        print(f"{item} has been selected.")

