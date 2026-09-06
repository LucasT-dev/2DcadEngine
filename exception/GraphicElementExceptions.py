

class GraphicElementError(Exception):
    """Exception de base pour toutes les erreurs liées à GraphicElementManager."""
    pass


class ElementNotRegisteredError(GraphicElementError):
    """Levée quand un nom d'élément demandé n'existe pas dans le registre."""

    def __init__(self, name: str, known_names: list[str] = None):
        self.name = name
        self.known_names = known_names or []
        message = f"Aucun élément enregistré sous le nom '{name}'."
        if self.known_names:
            message += f" Noms disponibles : {', '.join(self.known_names)}"
        super().__init__(message)


class ElementAlreadyRegisteredError(GraphicElementError):
    """Levée en cas de tentative d'écraser un élément déjà enregistré sans le vouloir explicitement."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Un élément est déjà enregistré sous le nom '{name}'. "
                         f"Utilisez overwrite=True pour le remplacer volontairement.")


class ElementCreationError(GraphicElementError):
    """Levée quand l'instanciation d'un élément échoue (mauvais arguments, erreur interne...)."""

    def __init__(self, name: str, original_exception: Exception):
        self.name = name
        self.original_exception = original_exception
        super().__init__(f"Échec de création de l'élément '{name}' : {original_exception}")