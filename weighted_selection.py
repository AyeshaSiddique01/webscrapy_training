import random

def weighted_random_selection(weights):
    total_weight = sum(weights)
    probabilities = [item / total_weight for item in weights]
    cumulative_probabilities = [sum(probabilities[:i+1]) for i in range(len(probabilities))]
    rand = random.uniform(0, 1)
    for index, cumulative_probability in enumerate(cumulative_probabilities):
        if rand < cumulative_probability:
            return weights[index]
    return None

weights = [1000, 1, 1, 1, 1, 1]
occurrences = [0] * len(weights)

for i in range(200):
    result = weighted_random_selection(weights)
    occurrences[weights.index(result)] += 1

print(occurrences)
