from abc import abstractmethod
from random import choice

class IObservable:
    @abstractmethod
    def add(self, observer):
        pass

    @abstractmethod
    def remove(self, observer):
        pass

    @abstractmethod
    def notify(self, topic):
        pass

class IObserver:
    @abstractmethod
    def update(self, topic):
        pass

class TopicStore:
    def __init__(self, topics):
        self.topics = topics

    def is_topic_available(self, topic):
        return topic in self.topics

    def remove_topic(self, topic):
        self.topics.remove(topic)

class ConcreteTeacher(IObservable):
    def __init__(self, topic_store):
        self.topic_store = topic_store
        self.observers = []

    def add(self, observer):
        self.observers.append(observer)

    def remove(self, observer):
        self.observers.remove(observer)

    def notify(self, topic):
        for observer in self.observers:
            observer.update(topic)

    def remove_topic(self, topic):
        if self.topic_store.is_topic_available(topic):
            self.topic_store.remove_topic(topic)
            self.notify(topic)

class ConcreteStudent(IObserver):
    def __init__(self, name):
        self.name = name
        self.selected_topic = None

    def select_random_topic(self, teacher):
        selected_topic = choice(list(teacher.topic_store.topics))
        self.selected_topic = selected_topic
        teacher.remove_topic(selected_topic)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topic}")

    def update(self, topic):
        print(f"{self.name}: Topic {topic} has been selected.")


no_of_topics = 5
topics = [i for i in range(1, no_of_topics + 1)]
topic_store = TopicStore(topics)

teacher = ConcreteTeacher(topic_store)

students = [ConcreteStudent(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    teacher.add(student)

for student in students:
    student.select_random_topic(teacher)

for student in students:
    student.get_selected_topic()
