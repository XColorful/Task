# Task txt 备份文件格式说明

> 本文档说明 Task 项目生成的 txt 备份文件的数据结构，便于编写解析器或数据迁移工具。

## 一、备份文件类型概览

Task 项目生成以下几种 txt 文件：

| 文件类型 | 生成指令 | 典型路径 | 用途 |
|----------|----------|----------|------|
| 全局备份 | `backup`(main) | `./backup_all/backup_YYYY_MM_DD - HH-MM-SS.txt` | 完整数据备份，可 reimport |
| 单体备份 | `backup`(Tasker内) | `./backup_single/{label}_YYYY_MM_DD - HH-MM-SS.txt` | 单个 Tasker 备份 |
| 可读 txt | `txt`(main) | `./Task_txt.txt` | 人类可读的汇总文件 |
| 早期备份 | `backup1`(school_task) | `./backup1.txt` | 早期格式（兼容用） |

## 二、全局/单体备份格式（主格式）

这是 `backup` 和 `reload` 指令使用的格式，也是最重要的数据格式。

### 2.1 整体结构

```
{Tasker行1}
\t{Task行1.1}
\t{Task行1.2}
{Tasker行2}
\t{Task行2.1}
\t{Task行2.2}
...
/end
{备份元信息行1}
{备份元信息行2}
...
```

- Tasker 行**不以 `\t` 开头**，Task 行**以 `\t` 开头**
- 每条记录内部字段用 `||||`（四个竖线）分隔
- 文件以 `/end` 标记数据结束，之后为元信息

### 2.2 Tasker 行格式

```
{type}||||{version}||||{tasker_label}||||{create_date}||||{function_list}||||{task_template_list}||||{description}
```

| 位置 | 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|------|
| 0 | type | str | Tasker 类型 | `Default` 或 `Extra` 或自定义 |
| 1 | version | str | Tasker 版本 | Default 类用数字如 `1.0`，Extra 类用字符串如 `account` |
| 2 | tasker_label | str | Tasker 标签名 | `班级`、`计时器` |
| 3 | create_date | str | 创建日期 | `2023_09_03` |
| 4 | function_list | str | 功能类列表（空格分隔三元组） | `default_tasker_func 1.0 Default categorize_task 1.0 Default` |
| 5 | task_template_list | str | Task 模板列表（空格分隔二元组） | `Default 1.0` |
| 6 | description | str | Tasker 描述文本 | `从Task导入` |

**function_list 结构：** `{label1} {version1} {type1} {label2} {version2} {type2} ...`
- 每 3 个空格分隔的字段描述一个 class_func
- 如果 Tasker 没有任何 function，此字段为空字符串

**task_template_list 结构：** `{type1} {version1} {type2} {version2} ...`
- 每 2 个空格分隔的字段描述一个 Task 模板
- 如果备份时无可用的 task_template，此字段可能为空

### 2.3 Task 行格式

#### Default 类型 Task

```
\tDefault||||{version}||||{create_date}||||{date}||||{attribute}||||{content}||||{comment}
```

| 位置 | 字段 | 说明 | 示例 |
|------|------|------|------|
| 0 | type | 固定为 `Default` | `Default` |
| 1 | version | Task 版本 | `1.0` |
| 2 | create_date | 记录创建日期 | `2023_09_01` |
| 3 | date | 事件日期 | `2023_09_01` |
| 4 | attribute | 属性/分类 | `回执`、`购买`、`高考` |
| 5 | content | 内容文本（可包含 `"; "` 分隔的多段信息） | `填写特殊体质登记备案表` |
| 6 | comment | 注释 | `包含家庭住址,家长姓名,工作单位,联系电话` |

**完整示例：**
```
Default||||1.0||||2023_09_01||||2023_09_01||||回执||||填写特殊体质登记备案表||||包含家庭住址,家长姓名,工作单位,联系电话
```

在文件中 Task 行以 `\t` 开头：
```
\tDefault||||1.0||||2023_09_01||||2023_09_01||||回执||||填写特殊体质登记备案表||||包含家庭住址,家长姓名,工作单位,联系电话
```

#### Extra 类型 Task

Extra 类型 Task 的格式由各模块自定义，基本结构为：

```
\t{type}||||{version}||||{自定义字段...}
```

**timer_task 示例：**
```
\tExtra||||timer||||2024_05_07||||2024_05_07-14:30||||2024_05_07-16:00||||编程||||写Task重构方案||||计划阶段
```

字段序列：`type, version, create_date, start_time, end_time, attribute, content, comment`

**account_task 示例（变长字段）：**
```
\tExtra||||account||||2024_05_08||||2024_05_08||||GitHub||||my-account||||password123||||description|||我的GitHub账号|||主账号||||login_name|||xcolorful
```

account_task 的前 7 个固定字段：`type, version, create_date, last_date, account_type, label, password`

之后为变长字段，每个 "段" 格式：`{key}|||{value1}|||{value2}|||...`

支持的 key：`description`, `login_name`, `verified_phone`, `verified_email`, `linked_account`, `secure_question`, `other_info`, `password_history`

## 三、可读 txt 格式 (Task_txt.txt)

由 `txt` 指令生成，支持三种排序模式：

### 3.1 按日期排序模式

```
date：2023_09_01
|  |--班级
|  |  |-<回执>|填写特殊体质登记备案表
|  |  | |-包含家庭住址,家长姓名,工作单位,联系电话
|  |  |-<购买>|订阅高招周刊
|  |--其他Tasker
|  |  |-<记录>|其他内容
date：2023_09_04
|  |--班级
|  |  |-<回执>|填写少儿住院互助基金告家长书回执
```

### 3.2 按 Tasker 类别模式

```
班级
|--创建于2023_09_03；共150项Task
|--描述：班级事务记录
|--|Task列表：
   |--[  1]-2023_09_01|<回执>|填写特殊体质登记备案表
   |   |-包含家庭住址,家长姓名,工作单位,联系电话
   |--[  2]-2023_09_04|<回执>|填写少儿住院互助基金告家长书回执
```

### 3.3 按创建日期排序模式

```
create_date：2023_09_03
|  |--班级
|  |  |-2023_09_01|<回执>|填写特殊体质登记备案表
|  |  | |-包含家庭住址,家长姓名,工作单位,联系电话
```

## 四、早期备份格式 (backup1.txt)

由 `school_task` 模块的 `backup1` 指令生成，是早期版本的兼容格式。

### 4.1 Tasker 行
```
Task_object|{tasker_label}|{create_date}|{description}
```

### 4.2 Task 行
```
Task|{date}|{attribute}|{content}|{comment}|{create_date}
```

**示例：**
```
Task_object|班级|2023_09_03|班级事务记录
Task|2023_09_01|回执|填写特殊体质登记备案表|包含家庭住址,家长姓名,工作单位,联系电话|2023_09_01
```

**注意：** 此格式不支持 Extra 类型数据，fields 用单个 `|` 分隔。

## 五、today.txt 格式

由 `school_task` 模块的 `today` 指令生成，仅包含指定日期的 Task：

```
班级:
	2025_06_19|<作业>|数学练习册P45-P47|明天交
	2025_06_19|<通知>|家长会改为线上
计时器:
	2025_06_19|<编程>|重构Task项目
```

- 格式：`Tasker名:\n\t{date}|<{attribute}>|{content}|{comment}`
- comment 为空时不显示 `|{comment}`

## 六、分隔符汇总

| 分隔符 | 用途 | 说明 |
|--------|------|------|
| `||||` | 主字段分隔 | 用于 backup 格式的所有字段间 |
| `\|\|\|` | account 内部字段分隔 | 仅用于 account_task 的 dict key-value |
| `\|`（单竖线） | 早期格式字段分隔 | 仅用于 backup1.txt |
| `\t` | Task 行前缀 | 用于区分 Tasker 行和 Task 行 |
| `"; "`（分号+空格） | content 内多段信息分隔 | 人为约定，非程序强制 |
| `：`（中文冒号） | content 内键值对分隔 | 人为约定，如 `卡号:A02084` |
| `/end` | 备份数据结束标记 | 之后为人类可读的元信息 |

## 七、解析注意事项

1. **编码：** 所有 txt 文件使用 UTF-8 编码
2. **空行：** backup 文件中可存在空行（`reload` 时会跳过）
3. **变长字段：** account_task 的字段数不固定，需按 key-value 模式解析
4. **特殊字符冲突：** `strict_input` 和 `block_input` 函数会阻止用户输入含 `||||` 或 `\t` 的内容，但 content/comment 字段理论上可包含任意内容
5. **版本兼容：** Default 类型使用 float 版本比较（≤为兼容），Extra 类型使用字符串精确匹配
6. **function_list 解析：** 每 3 个字段一组（label, version, type），无法被 3 整除则说明数据异常
7. **task_template 解析：** 每 2 个字段一组（type, version）
