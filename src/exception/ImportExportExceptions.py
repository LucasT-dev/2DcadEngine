class ImportExportError(Exception):
    """Exception de base pour les erreurs d'import/export de scène."""
    pass


class ExportError(ImportExportError):
    def __init__(self, path: str, original_exception: Exception):
        self.path = path
        self.original_exception = original_exception
        super().__init__(f"Échec de l'export vers '{path}' : {original_exception}")


class ImportError_(ImportExportError):
    """Suffixe '_' pour éviter le conflit avec le ImportError natif de Python."""
    def __init__(self, path: str, original_exception: Exception):
        self.path = path
        self.original_exception = original_exception
        super().__init__(f"Échec de l'import depuis '{path}' : {original_exception}")


