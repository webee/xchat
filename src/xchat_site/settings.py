from xchat_site import config
from xchat_site.config.settings import *
CONFIG = config

try:
    from .local_settings import *
except:
    pass
