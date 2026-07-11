"""AnalysisEngine -- facade that loads analyzers by name and delegates queries."""

from core.extension_registry import ExtensionRegistry
from .base_analyzer import BaseAnalyzer


class AnalysisEngine:
    """Facade that loads analyzers by registered name."""

    def __init__(self, storage):
        self._storage = storage
        self._cache = {}

    def _get_analyzer(self, name):
        if name not in self._cache:
            cls = ExtensionRegistry._analyzers.get(name)
            if cls is None:
                raise KeyError(f"Analyzer '{name}' not registered")
            self._cache[name] = cls()
        return self._cache[name]

    def analyze(self, name, params=None):
        """Run a named analyzer.

        Args:
            name: analyzer registration name (e.g. 'attr_count')
            params: dict passed to analyzer.analyze()

        Returns:
            dict: analysis result
        """
        params = params or {}
        params['_storage'] = self._storage
        return self._get_analyzer(name).analyze(params)
