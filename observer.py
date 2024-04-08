from abc import ABC, abstractmethod
import random

class TopicStore:
    def __init__(self, topics):
        self.topics = topics

    def is_topic_available(self, topic):
        return topic in self.topics

    def remove_topic(self, topic):
        self.topics.remove(topic)


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
    def register(self, observable):
        pass

    @abstractmethod
    def update(self, item):
        pass


class Teacher(IObservable):
    def __init__(self, topic_store):
        self.observers = []
        self.weights = []
        self.topic_store = topic_store

    def add(self, observer):
        self.observers.append(observer)
        self.weights.append(1)

    def remove(self, observer):
        observer_index = self.observers.index(observer)
        self.observers.remove(observer_index)
        self.weights.remove(observer_index)

    def notify(self, item):
        for observer in self.observers:
            observer.update(item)

    def remove_topic(self, topic):
        if self.topic_store.is_topic_available(topic):
            self.topic_store.remove_topic(topic)
            self.notify(topic)
            return True
        return False

    def update_probability(self, observer):
        observer_index = self.observers.index(observer)
        self.weights[observer_index] -= self.weights[observer_index] * 0.9
        
class Student(IObserver):
    def __init__(self, name):
        self.name = name
        self.selected_topics = []
        self.observable = None

    def register(self, observable):
        self.observable = observable

    def select_random_topic(self):
        selected_topic = random.choice(list(self.observable.topic_store.topics))
        self.selected_topics.append(selected_topic)
        if self.observable.remove_topic(selected_topic):
            self.observable.update_probability(self)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topics}")

    def update(self, topic):
        print(f"{self.name}: Topic {topic} has been selected.")


def weighted_random_selection(weights):
    total_weight = sum(weights)
    probabilities = [item / total_weight for item in weights]
    cumulative_probability = 0
    rand = random.uniform(0, 1)

    for index, probability in enumerate(probabilities):
        cumulative_probability += probability
        if rand < cumulative_probability:
            return index
    return None

no_of_topics = 5
topics = [i for i in range(1, no_of_topics + 1)]
topic_store = TopicStore(topics)

teacher = Teacher(topic_store)

students = [Student(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    student.register(teacher)

for student in students:
    teacher.add(student)

while teacher.topic_store.topics:
    selected_weight = weighted_random_selection(teacher.weights)
    students[selected_weight].select_random_topic()

for student in students:
    student.get_selected_topic()

print(teacher.weights)
