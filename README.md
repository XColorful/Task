# Task

使用Task将各种类型的记录存放在在Tasker中，如任务，事件，账号，备忘录等。

## 安装

1. 安装[Python](https://www.python.org/)（目前使用[3.12.2](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)）[_https://www.python.org/_](https://www.python.org/)
2. 点击"[**<>Code**](https://github.com/XColorful/Task/archive/refs/heads/main.zip)"，下载压缩包后解压
3. 双击"**安装.cmd**"，完成后即可双击"**运行.cmd**"，运行程序

    > _可对"运行.cmd"添加快捷方式至桌面或任意目录下，便于启动程序_

## 简易教程

_注：在任意界面均可输入"**exit**"退出当前操作_

## 1. 创建一个Tasker

- 主界面输入"_**add**_"，输入"_**回车**_"创建默认类型的Tasker
- 输入"_**y**_"立即补充该标签，描述；输入"_**回车**_"添加默认Task类型模板

## 2. 进入Tasker界面

- 主界面输入"_**get**_"，选中索引或标签即可进入Tasker界面

## 3. 默认Tasker界面

- 输入任意内容，程序将尝试用空格分隔前的部分作为指令

    > _可以尝试输入"_**/info**_"获取更多帮助_

## 4. 记录一项Task

- 默认Tasker界面内输入"_**new**_"，依次填入"**日期**"，"**属性**"，"**内容**"，"**注释**"

    > _除"**内容**"外，输入"**回车**"即可填入默认内容_

##  其他功能

## 备份与读取

- 主界面输入"_**backup**_"，创建备份文件至代码目录下"**_.\\\\backup_all\\\\backup_YYYY_MM_DD - HH-MM-SS.txt_**"
- 主界面输入"_**reload**_"，选择代码目录下"**_.\\\\backup_all\\\\_**"中的"**_backup\_\*.txt_**"文件进行读取

## 添加导入模块

- 在代码目录下创建"_**load_module.txt**_"
- 选择输入"_**代码目录/package/**_"下的文件夹名称即可在程序启动时导入模块

## 为Tasker添加功能

- 导入"**_tasker_manager_**"模块后，在主界面输入"_**add_func**_"，选中需要添加功能的Tasker
- 选中索引，标签或任意Tasker功能列表
- 添加后即可在Tasker界面内使用

## 额外设置

## 更改数据文件存放目录

- 在代码目录下创建"_**pkl_dir.txt**_"
- 将代码目录下"_**Tasker_list.pkl**_"移至任意目录
- 在"_**pkl_dir.txt**_"第一行输入移动后的**文件**路径，如"_**D:\\\\文件夹\\\\Tasker_list.pkl**_"

## 更改默认设置

- 在主界面输入"**sys_info**"，输入"**settings_dict**"查看已有设置

- 在代码目录下创建"**settings.txt**"，以{"设置名"|"值"}的格式进行设置，每项换行输入

    > 示例：

    > SHOW_TIPS|True

    > BACKUP_INTERVAL|3

    > AUTO_BACKUP|True