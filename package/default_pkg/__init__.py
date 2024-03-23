from .class_func import default_tasker_func
from .tasker import default_tasker
from .io import command_input, normal_input, strict_input, block_input
from .message import system_msg, error_msg, tips_msg, table_msg, head_msg, body_msg, normal_msg
from .method import default_method, default_txt_operation, default_sys_method, default_tasker_sort
from .task import default_task
package_dict = {"class_func":[default_tasker_func],
                "default_tasker":[default_tasker],
                "io":[{"io_label":"default_io",
                       "command_input":command_input,
                       "normal_input":normal_input,
                       "strict_input":strict_input,
                       "block_input":block_input}],
                "message":[ # message:1
                            {"message_label":"default_message",
                            "system_msg":system_msg,
                            "error_msg":error_msg,
                            "tips_msg":tips_msg,
                            "table_msg":table_msg,
                            "head_msg":head_msg,
                            "body_msg":body_msg,
                            "normal_msg":normal_msg}
                            # message:2 （可拓展）
                            ],
                "method":[default_method(), default_txt_operation(), default_sys_method(), default_tasker_sort()],
                "default_task":[default_task]}