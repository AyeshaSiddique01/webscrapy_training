import random
from clothing_app.observer import Observable, Observer

class WeightedObservable(Observable):
    MAX_WEIGHT = 1
    def __init__(self):
        super().__init__()
        self.weights = []

    def add(self, observer):
        super().add(observer)
        self.weights.append(self.MAX_WEIGHT)

    def remove(self, observer):
        super().remove(observer)
        observer_index = self.observers.index(observer)
        self.weights.pop(observer_index)

    def weighted_random_selection(self):
        total_weight = sum(self.weights)
        probabilities = [item / total_weight for item in self.weights]
        cumulative_probability = 0
        rand = random.uniform(0, 1)

        for index, probability in enumerate(probabilities):
            cumulative_probability += probability
            if rand < cumulative_probability:
                return self.observers[index]
        return None

class WeightedObserver(Observer):
    def __init__(self):
        super().__init__()
