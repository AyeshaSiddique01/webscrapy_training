from abc import ABC, abstractmethod
import random
import copy

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
        self.weights = []

    def add(self, observer):
        self.observers.append(observer)
        observer.observable = self
        self.weights.append(1)

    def remove(self, observer):
        observer_index = self.observers.index(observer)
        self.observers.remove(observer)
        observer.observable = None
        self.weights.remove(self.weights[observer_index])


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
    
    def reduce_weight(self, observer):
        observer_index = self.observers.index(observer)
        self.weights[observer_index] -= self.weights[observer_index] * 0.9

class Teacher(Observable):
    def __init__(self):
        super().__init__()


class Observer(IObserver):
    def __init__(self):
        self.observable = None

    def on_update(self, item):
        print(f"{item} has been selected.")


class Student(Observer):
    def __init__(self, name, topics):
        self.name = name
        self.topics = copy.deepcopy(topics)
        self.selected_topics = []
        super().__init__()

    def select_random_topic(self):
        selected_topic = random.choice(self.topics)
        self.selected_topics.append(selected_topic)
        self.observable.notify(selected_topic)
        self.observable.reduce_weight(self)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topics}")

    def on_update(self, item):
        super().on_update(item)
        self.topics.remove(item)

no_of_topics = 5
topics = [f"Topic_{i}" for i in range(1, no_of_topics + 1)]

teacher = Teacher()

students = [Student(f"Student{i}", topics) for i in range(1, no_of_topics + 1)]

for student in students:
    teacher.add(student)

while students[0].topics:
    selected_weight = teacher.weighted_random_selection()
    students[selected_weight].select_random_topic()

for student in students:
    student.get_selected_topic()

print(teacher.weights)