from abc import abstractmethod
from random import choice


class TopicStore:
    def __init__(self, topics):
        self.topics = topics

    def is_topic_available(self, topic):
        return topic in self.topics

    def remove_topic(self, topic):
        self.topics.remove(topic)


class IObservable:
    def __init__(self):
        self.observers = []

    @abstractmethod
    def add(self, observer):
        self.observers.append(observer)

    @abstractmethod
    def remove(self, observer):
        self.observers.remove(observer)

    @abstractmethod
    def notify(self, item):
        for observer in self.observers:
            observer.update(item)


class IObserver:
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def register(self, observable):
        self.observable = observable

    @abstractmethod
    def update(self, item):
        pass


class Teacher(IObservable):
    def __init__(self, topic_store):
        super().__init__()
        self.topic_store = topic_store

    def remove_topic(self, topic):
        if self.topic_store.is_topic_available(topic):
            self.topic_store.remove_topic(topic)
            self.notify(topic)


class Student(IObserver):
    def __init__(self, name):
        super().__init__(name)
        self.selected_topic = None

    def select_random_topic(self):
        selected_topic = choice(list(self.observable.topic_store.topics))
        self.selected_topic = selected_topic
        self.observable.remove_topic(selected_topic)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topic}")

    def update(self, topic):
        print(f"{self.name}: Topic {topic} has been selected.")


no_of_topics = 5
topics = [i for i in range(1, no_of_topics + 1)]
topic_store = TopicStore(topics)

teacher = Teacher(topic_store)

students = [Student(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    student.register(teacher)

for student in students:
    teacher.add(student)

for student in students:
    student.select_random_topic()

for student in students:
    student.get_selected_topic()

print(teacher.topic_store.topics)
