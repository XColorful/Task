from core.extension_registry import ExtensionRegistry
from .account_task import AccountTask
from .account_tasker import AccountTasker

ExtensionRegistry.register_task_type("account", AccountTask)
ExtensionRegistry.register_tasker_type("account", AccountTasker)
ExtensionRegistry.register_chart_page("account_type_count", "extensions/account/charts/account_type_count.html")
ExtensionRegistry.register_chart_page("password_age", "extensions/account/charts/password_age.html")
