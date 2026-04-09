"""test_utils.py — utils.py 单元测试"""
import os
import pytest
from utils import load_dotenv


class TestLoadDotenv:
    def test_loads_variables(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR_MCTTK=hello\n", encoding="utf-8")
        os.environ.pop("TEST_VAR_MCTTK", None)
        load_dotenv(str(tmp_path))
        assert os.environ.get("TEST_VAR_MCTTK") == "hello"
        del os.environ["TEST_VAR_MCTTK"]

    def test_does_not_overwrite_existing(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR_MCTTK2=from_file\n", encoding="utf-8")
        os.environ["TEST_VAR_MCTTK2"] = "original"
        load_dotenv(str(tmp_path))
        assert os.environ["TEST_VAR_MCTTK2"] == "original"
        del os.environ["TEST_VAR_MCTTK2"]

    def test_skips_comments(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("# this is a comment\nTEST_VAR_MCTTK3=value\n", encoding="utf-8")
        os.environ.pop("TEST_VAR_MCTTK3", None)
        load_dotenv(str(tmp_path))
        assert os.environ.get("TEST_VAR_MCTTK3") == "value"
        del os.environ["TEST_VAR_MCTTK3"]

    def test_no_env_file(self, tmp_path):
        # 不存在 .env 文件时不报错
        load_dotenv(str(tmp_path))

    def test_value_with_equals(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR_MCTTK4=jiubook=玖书=1501743\n", encoding="utf-8")
        os.environ.pop("TEST_VAR_MCTTK4", None)
        load_dotenv(str(tmp_path))
        assert os.environ.get("TEST_VAR_MCTTK4") == "jiubook=玖书=1501743"
        del os.environ["TEST_VAR_MCTTK4"]

    def test_empty_lines_skipped(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("\n\nTEST_VAR_MCTTK5=ok\n\n", encoding="utf-8")
        os.environ.pop("TEST_VAR_MCTTK5", None)
        load_dotenv(str(tmp_path))
        assert os.environ.get("TEST_VAR_MCTTK5") == "ok"
        del os.environ["TEST_VAR_MCTTK5"]
