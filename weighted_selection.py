import random

def weighted_random_selection(weights):
    total_weight = sum(weights)
    probabilities = [item / total_weight for item in weights]
    cumulative_probability = 0
    rand = random.uniform(0, 1)

    for index, probability in enumerate(probabilities):
        cumulative_probability += probability
        if rand < cumulative_probability:
            return weights[index]
    return None

weights = [1000, 1, 1, 1, 1, 1]
occurrences = [0] * len(weights)

for i in range(200):
    result = weighted_random_selection(weights)
    occurrences[weights.index(result)] += 1

print(occurrences)
