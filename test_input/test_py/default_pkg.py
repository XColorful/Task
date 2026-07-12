from sys import argv
from sys import exit
from os import mkdir, remove

from os.path import exists, dirname

def make_pkl():
    pkl_dir = get_pkl_dir()
    main_tasker_list = [] # 用于测试的空列表
    if not exists(dirname(pkl_dir)):
        mkdir(dirname(pkl_dir))
    import pickle
    pkl_file = open(pkl_dir, "wb")
    pickle.dump(main_tasker_list, pkl_file, 5)
    pkl_file.close()

def get_pkl_dir() -> str:
    try:
        with open(f".\\pkl_dir.txt", "r", encoding = "utf-8") as f:
            main_pkl_dir = f.readline()
            if exists(main_pkl_dir):
                print(f"Directory:\"{main_pkl_dir}\" already exists, to prevent data lost, this test will stop")
                input("Press any button to exit")
                exit(1)
            main_pkl_dir = ".\\Tasker_list.pkl"
    except FileNotFoundError: main_pkl_dir = ".\\Tasker_list.pkl"
    return main_pkl_dir


def prepare_environment():
    # 检查pkl_dir，创建Tasker_list.pkl
    main_pkl_dir = get_pkl_dir()
    if exists(main_pkl_dir):
        print(f"Directory:\"{main_pkl_dir}\" already exists, to prevent data lost, this test will stop.")
        input("Press any bottom to exit")
        exit(1)
    make_pkl()
    # 检查settings.txt
    if exists(f".\\settings.txt"):
        print(f"Directory:\".\\settings.txt\" already exists, to make sure this test will not be proceeded to prevent doing something wrong")
        input("Press any button to exit")
        exit(1)
    # load_package.txt检查
    # 由于main.py默认导入default_pkg，此处无需检查

def clear_environment():
    print("pkl file for test:\".\\Tasker_list.pkl\"")
    if input("Save test pkl file(y/n)") != "y":
        try:
            remove(".\\Tasker_list.pkl")
        except FileNotFoundError:
            pass

for arg in argv:
    if arg == "prepare":
        prepare_environment()
    elif arg == "clear":
        clear_environment()