import subprocess
import time

from os import listdir, chdir
from os.path import dirname, abspath, join, basename, exists
from unittest.mock import patch

working_dir = dirname(abspath(__file__))
chdir(working_dir) # 切换工作路径至当前文件目录


def get_test_input_list() -> list[str]:
    directory = ".\\test_input"
    test_input_list = []
    if not exists(directory):
        print("Test code directory \".\\test_input\\\" doesn't exists")
        input("Press any button to exit")
        exit()
    for filename in listdir(directory):
        if filename.endswith(".txt"):
            test_input_list.append(join(directory, filename))
    return test_input_list

def select_test_input(test_input_list) -> str:
    if test_input_list == []:
        print("There's no test_input available in \".\\test_input\"")
        input("Press any button to exit.")
        exit()
    print("Select test_input")
    for index, filedir in enumerate(test_input_list):
        print(f"\t[{index}]|{filedir}")
    if len(test_input_list) == 1:
        if input("Press <Enter> to select the only test code") != "":
            exit()
        else:
            return test_input_list[0]
    else:
        user_input = input("Choose one test_input")
        if user_input == "exit":
            exit()
        try:
            index = int(user_input)
            return test_input_list[index]
        except ValueError:
            pass
        except IndexError:
            pass
        for filedir in test_input_list:
            if user_input in filedir:
                return filedir
    print(f"Didn't found \"{user_input}\"")
    input(f"Press any button to exit")
    exit()

def run_test_py(basename, run_mode):
    check_py = f".\\test_input\\test_py\\{basename}.py"
    if not exists(check_py):
        return None
    
    # test.py本身已经和main.py同工作目录
    result = subprocess.run(["python", check_py, run_mode])
    if result.returncode == 1: # cwd=dirname(abspath(__file__))
        exit()
    return None

def prepare_environment(basename):
    run_test_py(basename, "prepare")

def clear_environment(basename):
    run_test_py(basename, "clear")

def show_used_time(elapsed_time):
    seconds = round(elapsed_time, 1)
    milliseconds = int(elapsed_time * 1000)
    minutes = "" if seconds < 60 else f" (about {round(seconds/60, 1)}minutes)"
    print("Runtime:")
    print(f"\t{seconds} seconds{minutes}")
    print(f"\tor {round(milliseconds)} ms")

def run_test():
    test_input_list = get_test_input_list()
    file_dir = select_test_input(test_input_list)
    
    with open(file_dir, 'r') as test_input:
        test_inputs = test_input.read().splitlines()

    
    with patch('builtins.input', side_effect=test_inputs):
        try:
            # 配置环境
            test_basename = basename(file_dir).rstrip(".txt")
            prepare_environment(test_basename)
            
            # 开始测试
            start_time = time.time()
            import main
            # subprocess.run(["python", "main.py"] + parameter_list) # 不太行，新开进程就没mock了
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("--------Test End--------")
            show_used_time(elapsed_time)
            print(f"Run Time:{elapsed_time}")
            
            # 清除环境
            clear_environment(test_basename)
        except StopIteration:
            pass  # 当所有的输入都被使用完时，会抛出StopIteration异常


if __name__ == '__main__':
    run_test()