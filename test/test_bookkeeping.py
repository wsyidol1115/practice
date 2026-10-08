"""使用临时账目验证：python3 -m unittest discover -s test -v。"""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).with_name("bookkeeping.py")


class BookkeepingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.script = Path(self.directory.name) / SOURCE.name
        shutil.copyfile(SOURCE, self.script)
        self.data = self.script.with_name("reimbursements.json")
        spec = importlib.util.spec_from_file_location("bookkeeping_test_target", self.script)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_cli(self, inputs):
        return subprocess.run(
            [sys.executable, "-u", str(self.script)], input=inputs,
            capture_output=True, text=True, timeout=10,
        )

    def test_register_query_reimburse_and_restart(self):
        result = self.run_cli("1\n交通\n12.34\n1\n餐饮\n20\n2\n1\n1\n2\n3\n3\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("32.34 元", result.stdout)
        records = json.loads(self.data.read_text())
        self.assertEqual([r["status"] for r in records], ["已报销", "待报销"])
        restart = self.run_cli("2\n2\n3\n3\n")
        self.assertEqual(restart.returncode, 0)
        self.assertIn("交通 | 12.34 元", restart.stdout)

    def test_invalid_saved_records_are_rejected_without_changes(self):
        valid = {"id": 1, "project": "交通", "amount": "428.00", "status": "待报销"}
        variants = [
            [valid, {**valid, "project": "餐饮"}],
            *[[{**valid, "id": value}] for value in (True, 0, -1)],
            [{**valid, "project": "  "}],
            *[[{**valid, "amount": value}] for value in
              ("-10", "0", "1.234", "1000000001", "NaN", "Infinity", "abc", 12.34, None)],
        ]
        for records in variants:
            with self.subTest(records=records):
                original = json.dumps(records, ensure_ascii=False)
                self.data.write_text(original, encoding="utf-8")
                result = self.run_cli("3\n")
                self.assertEqual(result.returncode, 1)
                self.assertIn("无法读取记账数据", result.stdout)
                self.assertEqual(self.data.read_text(), original)

    def test_invalid_registration_and_failed_save(self):
        records = []
        for value in ("NaN", "-1", "1.234", "1000000001"):
            with patch("builtins.input", side_effect=["交通", value]):
                with patch("builtins.print"):
                    self.module.register(records)
        self.assertEqual(records, [])
        self.assertFalse(self.data.exists())
        with patch("builtins.input", side_effect=["交通", "10"]):
            with patch.object(self.module, "save_records", side_effect=OSError("磁盘满")):
                with self.assertRaises(OSError):
                    self.module.register(records)
        self.assertEqual(records, [])

    def test_second_instance_blocked_and_lock_released(self):
        with self.module.exclusive_session():
            second = self.run_cli("1\n不应保存\n20\n3\n")
            self.assertEqual(second.returncode, 1)
            self.assertFalse(self.data.exists())
        result = self.run_cli("1\n保留项目\n10\n3\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(self.data.read_text())[0]["project"], "保留项目")

    def test_lock_released_after_process_termination(self):
        process = subprocess.Popen(
            [sys.executable, "-u", str(self.script)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            # 看到主菜单说明子进程已取得锁并完成读取。
            for _ in range(3):
                line = process.stdout.readline()
                if "报销记账" in line:
                    break
            blocked = self.run_cli("3\n")
            self.assertEqual(blocked.returncode, 1)
        finally:
            process.kill()
            process.communicate(timeout=10)
        self.assertEqual(self.run_cli("3\n").returncode, 0)


if __name__ == "__main__":
    unittest.main()
