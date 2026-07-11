from core.extension_registry import ExtensionRegistry
from .label_task import LabelTask
from .label_tasker import LabelTasker

ExtensionRegistry.register_task_type("label", LabelTask)
ExtensionRegistry.register_tasker_type("label", LabelTasker)
