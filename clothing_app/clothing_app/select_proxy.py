from clothing_app.observer_weighted_random_Selection import WeightedObservable, WeightedObserver

class ProxyManager(WeightedObservable):

    MAX_WEIGHT = 100

    def __init__(self):
        super().__init__(self.MAX_WEIGHT)

    def set_weight_zero(self, observer):
        observer_index = self.observers.index(observer)
        self.weights[observer_index] = 0

    def increase_weight(self, observer):
        observer_index = self.observers.index(observer)
        observer_weight = self.weights[observer_index]
        observer_weight += observer_weight * (0.1)
        self.weights[observer_index] = min(observer_weight, self.MAX_WEIGHT)

    def reduce_weight(self, observer):
        observer_index = self.observers.index(observer)
        observer_weight = self.weights[observer_index]
        observer_weight -= observer_weight * (0.1)
        self.weights[observer_index] = max(observer_weight, 0)

class Proxy(WeightedObserver):

    def __init__(self, name):
        self.name = name
        super().__init__()

    def reduce_weight(self):
        self.observable.reduce_weight(self)

    def increase_weight(self):
        self.observable.increase_weight(self)

    def set_weight_zero(self):
        self.observable.set_weight_zero(self)
