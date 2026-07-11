from core.extension_registry import ExtensionRegistry
from .timer_task import TimerTask
from .timer_tasker import TimerTasker

ExtensionRegistry.register_task_type("timer", TimerTask)
ExtensionRegistry.register_tasker_type("timer", TimerTasker)
ExtensionRegistry.register_chart_page("duration", "extensions/timer/charts/duration.html")
ExtensionRegistry.register_chart_page("3d_monthly", "extensions/timer/charts/3d_monthly.html")
