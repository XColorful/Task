from .class_func import account_tasker_func, account_manage_func
from .tasker import account_tasker
from .task import account_task
package_dict = {"class_func":[account_tasker_func, account_manage_func],
                "extra_tasker":[account_tasker],
                "extra_task":[account_task]}