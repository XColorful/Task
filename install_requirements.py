from subprocess import check_call
from os import walk
from os.path import dirname, abspath, join
working_dir = dirname(abspath(__file__))

def install_requirements(directory):
    for root, dirs, files in walk(directory):
        if 'requirements.txt' in files:
            req_path = join(root, 'requirements.txt')
            try:
                print(f"Installing requirements from {req_path}")
                check_call(f"pip install -r {req_path}", shell=True)
            except Exception as e:
                print(f"Failed to install requirements from {req_path}. Error: {str(e)}")

install_requirements(working_dir)
input("--------安装完成，按任意键退出--------")
exit()