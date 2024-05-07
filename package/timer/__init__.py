from .class_func import timer_tasker_func
from .tasker import timer_tasker
from .method import method_template
from .task import timer_task
package_dict = {"class_func":[timer_tasker_func],
                
                "extra_tasker":[timer_tasker],
                
                "method":[method_template()],
                
                "extra_task":[timer_task]}