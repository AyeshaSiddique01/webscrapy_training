from clothing_app.observer_weighted_random_Selection import WeightedObservable, WeightedObserver

class ProxyManager(WeightedObservable):

    MAX_WEIGHT = 100

    def __init__(self):
        super().__init__(self.MAX_WEIGHT)

    def update_weight(self, observer, status):
        observer_index = self.observers.index(observer)
        observer_weight = self.weights[observer_index]

        if status == "blocked":
            self.weights[observer_index] = 0
        elif status == "good":
            observer_weight += observer_weight * (0.1)
            self.weights[observer_index] = min(
                observer_weight, self.MAX_WEIGHT)
        else:
            observer_weight -= observer_weight * (0.1)
            self.weights[observer_index] = max(observer_weight, 0)


class Proxy(WeightedObserver):

    def __init__(self, name):
        self.name = name
        super().__init__()

    def select_proxy(self, status):
        self.observable.update_weight(self, status)


# proxy_manager = ProxyManager()

# with open(proxies_path, "r", encoding="utf-8") as file:
#     proxies = [Proxy(line.strip()) for line in file]

# proxies = [proxy_manager.add( proxy) for proxy in proxies]