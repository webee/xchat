# coding=utf-8
import os
from pytoolbox.util.pmc_config import register_config, get_project_root

PROJECT_ROOT = get_project_root(target='src')


def load_config(env):
    register_config(__name__, 'settings', env=env)


load_config(os.getenv('ENV', 'default'))

