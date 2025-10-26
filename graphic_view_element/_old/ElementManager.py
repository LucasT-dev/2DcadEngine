class ElementManager:

    def __init__(self):

        self.registry = {}

    def register(self, name: str, cls):
        self.registry[name] = cls

    def create_element(self, name: str, start, end, style):

        if not self.contains_element(name):
            raise ValueError(f"Aucun élément enregistré sous le nom '{name}'")

        cls = self.registry.get(name)

        return cls(start, end, style)

    def contains_element(self, name: str) -> bool:
        return self.registry.__contains__(name)