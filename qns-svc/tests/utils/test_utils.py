import os

import pytest

from utils.utils import get_envvar


class TestGetEnvVar:
    @classmethod
    def setup_class(cls):
        cls.exists = "EXISTS"
        cls.exists_return_val = "Valid"
        os.environ[cls.exists] = cls.exists_return_val

        cls.not_exists = "NOT_EXISTS"

    def test_get_envvar_exists(self):
        res = get_envvar(self.exists)
        assert res == self.exists_return_val

    def test_get_envvar_not_exists(self):
        with pytest.raises(ValueError):
            get_envvar(self.not_exists)
