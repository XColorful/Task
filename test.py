import subprocess
import time

from os import listdir, chdir, mkdir
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

def make_pkl(pkl_dir):
    main_tasker_list = []
    if not exists(dirname(pkl_dir)):
        mkdir(dirname(pkl_dir))
    import pickle
    pkl_file = open(pkl_dir, "wb")
    pickle.dump(main_tasker_list, pkl_file, 5)
    pkl_file.close()

def temp_main_pkl_dir() -> str:
    from function import YYYY_MM_DD_HH_MM_SS
    return f".\\test_input\\temp_pkl\\{YYYY_MM_DD_HH_MM_SS()}.pkl"

def try_check_result(basename, test_inputs):
    check_py = f".\\test_input\\test_py\\{basename}.py"
    if not exists(check_py):
        return None
    subprocess.run(["python", check_py, test_inputs])
    return None

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

    main_pkl_dir = temp_main_pkl_dir()
    make_pkl(main_pkl_dir)
    
    with patch('builtins.input', side_effect=test_inputs):
        try:
            parameter_list = [f"main_pkl_dir {main_pkl_dir}"]
            start_time = time.time()
            import main
            # subprocess.run(["python", "main.py"] + parameter_list) # 不太行，新开进程就没mock了
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("--------Test End--------")
            show_used_time(elapsed_time)
            print(f"Run Time:{elapsed_time}")
        except StopIteration:
            pass  # 当所有的输入都被使用完时，会抛出StopIteration异常
    
    test_basename = basename(file_dir)
    try_check_result(test_basename, test_inputs)
    print(f"Test pkl file:\"{main_pkl_dir}\"")
    if input("Save temporary used Tasker_list.pkl(y/n)") == "y":
        exit()
    from os import remove
    try:
        remove(main_pkl_dir)
    except FileNotFoundError:
        pass
    exit()

if __name__ == '__main__':
    run_test()