import random
import copy
from observer import Observable, Observer


class Teacher(Observable):
    def __init__(self):
        super().__init__()


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

for student in students:
    student.select_random_topic()

for student in students:
    student.get_selected_topic()