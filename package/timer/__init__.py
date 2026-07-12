from .class_func import timer_tasker_func, timer_categorize_func
from .tasker import timer_tasker
from .method import timer_task_method
from .task import timer_task
package_dict = {"class_func":[timer_tasker_func, timer_categorize_func],
                
                "extra_tasker":[timer_tasker],
                
                "method":[timer_task_method()],
                
                "extra_task":[timer_task]}