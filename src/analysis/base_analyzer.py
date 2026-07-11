"""BaseAnalyzer -- abstract base class for all analyzers."""

from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """所有分析器的抽象基类。"""

    analyzer_name: str = ""

    @abstractmethod
    def analyze(self, params: dict) -> dict:
        """Execute analysis and return structured results.

        Args:
            params: dict with keys like tasker_id, year, month, attr_filter, top_n

        Returns:
            dict ready for ECharts consumption. Structure varies by analyzer.
        """
        ...
