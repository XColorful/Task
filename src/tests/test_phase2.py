"""阶段 2 验证测试——工具层 + 配置层"""

import sys
import os
import tempfile

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, _src)

# ============================================================
# Test 1: JsonUtils
# ============================================================
from util.json_utils import JsonUtils
from collections import OrderedDict

d = tempfile.mkdtemp()

# 写入 + 读取
data = OrderedDict([("b", 2), ("a", 1)])
p1 = os.path.join(d, "test.json")
JsonUtils.save_json(p1, data, atomic=True)
loaded = JsonUtils.load_json(p1)
assert list(loaded.keys()) == ["b", "a"], f"Order not preserved: {list(loaded.keys())}"
assert loaded["b"] == 2
print("Test 1.1 PASS: JsonUtils save/load with order")

# 验证原子写入：tmp 文件应已被 rename
assert not os.path.exists(p1 + ".tmp"), "tmp file not cleaned up"
print("Test 1.2 PASS: JsonUtils atomic write (no tmp residue)")

# 非原子写入
p2 = os.path.join(d, "test2.json")
JsonUtils.save_json(p2, data, atomic=False)
assert os.path.exists(p2) and not os.path.exists(p2 + ".tmp")
print("Test 1.3 PASS: JsonUtils non-atomic write")

# ============================================================
# Test 2: FileUtils
# ============================================================
from util.file_utils import atomic_write, safe_join, ensure_dir

d2 = os.path.join(d, "subdir")
ensure_dir(d2)
assert os.path.isdir(d2)
print("Test 2.1 PASS: ensure_dir")

p3 = os.path.join(d2, "f.txt")
atomic_write(p3, "hello")
with open(p3) as f:
    assert f.read() == "hello"
assert not os.path.exists(p3 + ".tmp")
print("Test 2.2 PASS: atomic_write")

sp = safe_join(d, "subdir", "f.txt")
assert sp == os.path.abspath(p3)
print("Test 2.3 PASS: safe_join")

try:
    safe_join(d, "..")
    assert False, "should have raised"
except ValueError:
    print("Test 2.4 PASS: safe_join blocks traversal")

# ============================================================
# Test 3: StringUtils
# ============================================================
from util.string_utils import parse_semicolon_content, extract_key_value, extract_jpg_references

parts = parse_semicolon_content("a; b;  c ")
assert parts == ["a", "b", "c"], parts
print("Test 3.1 PASS: parse_semicolon_content")

kv = extract_key_value("卡号:A02084; 密码:255612", "卡号")
assert kv == "A02084"
print("Test 3.2 PASS: extract_key_value")

kv2 = extract_key_value("key：value", "key")
assert kv2 == "value", repr(kv2)
print("Test 3.3 PASS: extract_key_value chinese colon")

jpgs = extract_jpg_references("jpg:photo1; png:screenshot; doc:readme")
assert jpgs == ["photo1", "screenshot"]
print("Test 3.4 PASS: extract_jpg_references")

# ============================================================
# Test 4: ConfigStore
# ============================================================
from config.config_store import ConfigStore
from config.app_config import AppConfig

defaults = ConfigStore.load_defaults()
assert defaults["max_segment_size"] == 500
assert defaults["http_port"] == 19527
print("Test 4.1 PASS: ConfigStore defaults")

cfg_path = os.path.join(d, "config.json")
JsonUtils.save_json(cfg_path, {"max_segment_size": 300, "data_dir": "/custom"}, atomic=True)
loaded_cfg = ConfigStore.load(cfg_path)
assert loaded_cfg["max_segment_size"] == 300
assert loaded_cfg["http_port"] == 19527  # default
print("Test 4.2 PASS: ConfigStore merge with defaults")

# ============================================================
# Test 5: AppConfig
# ============================================================
AppConfig._instance = None
cfg2 = AppConfig.initialize(cfg_path)
assert cfg2.max_segment_size == 300
assert cfg2.http_port == 19527
assert cfg2.data_dir == "/custom"
print("Test 5.1 PASS: AppConfig.initialize from file")

d2_cfg = AppConfig()
d2_cfg.update_from_dict({"http_port": 8888, "max_segment_size": 999})
assert d2_cfg.http_port == 8888
assert d2_cfg.max_segment_size == 999
print("Test 5.2 PASS: AppConfig.update_from_dict")

# ============================================================
# Test 6: ConfigStore save
# ============================================================
cfg_path2 = os.path.join(d, "config2.json")
ConfigStore.save(cfg_path2, defaults)
assert os.path.exists(cfg_path2)
loaded2 = JsonUtils.load_json(cfg_path2)
assert loaded2["http_port"] == 19527
print("Test 6.1 PASS: ConfigStore.save")

# ============================================================
# Test 7: DateUtils re-verify (already tested in phase 1)
# ============================================================
from util.date_utils import today_str, now_str, format_duration, is_valid_date
assert is_valid_date(today_str())
assert len(now_str()) == 16
assert format_duration(0) == " 0m"
print("Test 7 PASS: date_utils regressions")

# cleanup
import shutil
shutil.rmtree(d)

print()
print("=== ALL 7 TESTS PASSED ===")
