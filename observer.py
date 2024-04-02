from abc import abstractmethod


# Topic Store class
class TopicStore:
    def __init__(self, topics):
        self.topics = topics

    def is_topic_available(self, topic):
        return topic in self.topics

    def remove_topic(self, topic):
        self.topics.remove(topic)

# Observable interface
class Teacher:
    @abstractmethod
    def add(self, observer):
        pass

    @abstractmethod
    def remove(self, observer):
        pass

    @abstractmethod
    def notify(self, topic):
        pass

# Concrete Observable class
class ConcreteTeacher(Teacher):
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

    def select_topic(self, topic):
        if self.topic_store.is_topic_available(topic):
            self.topic_store.remove_topic(topic)
            self.notify(topic)

# Observer interface
class Student:
    @abstractmethod
    def update(self, topic):
        pass

# Concrete observer class
class ConcreteStudent(Student):
    def __init__(self, name):
        self.name = name

    def update(self, topic):
        print(f"{self.name}: Topic {topic} has been selected.")


no_of_topics = 20
topics = [i for i in range(1, no_of_topics + 1)]
topic_store = TopicStore(topics)

teacher = ConcreteTeacher(topic_store)

students = [ConcreteStudent(f"Student{i}") for i in range(1, no_of_topics + 1)]

for student in students:
    teacher.add(student)

teacher.select_topic(4)
print(topic_store.topics)
