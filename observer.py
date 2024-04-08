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
    def update(self, item):
        pass


class Observable(IObservable):
    def __init__(self):
        self.observers = []

    def add(self, observer):
        self.observers.append(observer)

    def remove(self, observer):
        self.observers.remove(observer)

    def notify(self, item):
        for observer in self.observers:
            observer.update(item)


class Teacher(Observable):
    def __init__(self, topic_store):
        self.topic_store = topic_store
        super().__init__()

    def remove_topic(self, topic):
        if self.topic_store.is_topic_available(topic):
            self.topic_store.remove_topic(topic)
            super().notify(topic)
            return True
        return False


class Observer(IObserver):
    def __init__(self, name):
        self.name = name

    def update(self, item):
        print(f"{self.name}: {item} has been selected.")


class Student(Observer):
    def __init__(self, name):
        self.selected_topics = []
        self.teacher = None
        super().__init__(name)

    def select_random_topic(self):
        selected_topic = random.choice(
            list(self.teacher.topic_store.topics))
        self.selected_topics.append(selected_topic)
        self.teacher.remove_topic(selected_topic)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topics}")


no_of_topics = 5
topics = [f"Topic_{i}" for i in range(1, no_of_topics + 1)]
topic_store = TopicStore(topics)

teacher = Teacher(topic_store)

students = [Student(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    student.teacher = teacher
    teacher.add(student)

for student in students:
    student.select_random_topic()

for student in students:
    student.get_selected_topic()
