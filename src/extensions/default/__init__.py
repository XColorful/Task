from core.extension_registry import ExtensionRegistry
from core.input_processor import InputPreprocessor, step_plus_to_search
from .default_task import DefaultTask
from .default_tasker import DefaultTasker

ExtensionRegistry.register_task_type("default", DefaultTask)
ExtensionRegistry.register_tasker_type("default", DefaultTasker)
ExtensionRegistry.register_chart_page("attr_count", "extensions/default/charts/attr_count.html")
ExtensionRegistry.register_chart_page("monthly_count", "extensions/default/charts/monthly_count.html")
InputPreprocessor.register_step(step_plus_to_search)
