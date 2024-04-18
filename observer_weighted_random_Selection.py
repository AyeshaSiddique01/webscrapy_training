import random
from observer import Observable, Observer

class WeightedObservable(Observable):
    def __init__(self, max_weight):
        super().__init__()
        self.weights = []
        self.max_weight = max_weight

    def add(self, observer):
        super().add(observer)
        self.weights.append(self.max_weight)

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

class Teacher(WeightedObservable):

    MAX_WEIGHT = 1
    def __init__(self):
        super().__init__(self.MAX_WEIGHT)
    
    def reduce_weight(self, observer):
        observer_index = self.observers.index(observer)
        self.weights[observer_index] = 0

class Student(Observer):

    def __init__(self, name, topics):
        self.name = name
        self.topics = topics
        self.selected_topics = []
        super().__init__()

    def select_random_topic(self):
        selected_topic = random.choice(self.topics)
        self.selected_topics.append(selected_topic)
        self.observable.notify(selected_topic)
        self.observable.reduce_weight(self)

    def get_selected_topic(self):
        print(f"{self.name} selected topic {self.selected_topics}")


no_of_topics = 5
topics = [f"Topic_{i}" for i in range(1, no_of_topics + 1)]

teacher = Teacher()

students = [Student(f"Student{i}", topics) for i in range(1, no_of_topics + 1)]

for student in students:
    teacher.add(student)

while any(teacher.weights):
    selected_student = teacher.weighted_random_selection()
    selected_student.select_random_topic()

print("Students selected topic")
for student in students:
    student.get_selected_topic()

all_selected_topic = []
for student in students:
    all_selected_topic += student.selected_topics

unique_topic = set(all_selected_topic)
if len(unique_topic) < len(students[0].topics):
    print("Some students haven't selected topic")
else:
    print("All students selected unique topic")

print(teacher.weights)
