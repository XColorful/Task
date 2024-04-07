from .class_func import df_class_func_template, ex_class_func_template
from .tasker import df_tasker_template, ex_tasker_template
from .io import command_input, normal_input, strict_input, block_input
from .message import system_msg, error_msg, tips_msg, table_msg, head_msg, body_msg, normal_msg
from .method import method_template
from .task import df_task_template, ex_task_template
package_dict = {"class_func":[df_class_func_template,
                              ex_class_func_template],
                
                "default_tasker":[df_tasker_template],
                "extra_tasker":[ex_tasker_template],
                
                "io":[{"io_label":"io_template",
                       "command_input":command_input,
                       "normal_input":normal_input,
                       "strict_input":strict_input,
                       "block_input":block_input}],
                "message":[ # message:1
                            {"message_label":"message_template",
                            "system_msg":system_msg,
                            "error_msg":error_msg,
                            "tips_msg":tips_msg,
                            "table_msg":table_msg,
                            "head_msg":head_msg,
                            "body_msg":body_msg,
                            "normal_msg":normal_msg}
                            # message:2 （可拓展）
                            ],
                "method":[method_template()],
                
                "default_task":[df_task_template],
                "extra_task":[ex_task_template]}