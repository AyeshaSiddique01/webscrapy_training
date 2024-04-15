from abc import ABC, abstractmethod
import random


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


class Teacher(Observable):
    def __init__(self, topics):
        super().__init__()
        self.topics = topics

    def remove_topic(self, topic):
        if topic in self.topics:
            self.topics.remove(topic)
            super().notify(topic)
            return True
        return False


class Observer(IObserver):
    def __init__(self):
        self.observable = None

    def on_update(self, item):
        print(f"{item} has been selected.")


class Student(Observer):
    def __init__(self, name):
        self.name = name
        self.selected_topics = []
        super().__init__()

    def select_random_topic(self):
        selected_topic = random.choice(list(self.observable.topics))
        self.selected_topics.append(selected_topic)
        self.observable.remove_topic(selected_topic)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topics}")


no_of_topics = 5
topics = [f"Topic_{i}" for i in range(1, no_of_topics + 1)]

teacher = Teacher(topics)

students = [Student(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    teacher.add(student)

for student in students:
    student.select_random_topic()

for student in students:
    student.get_selected_topic()
