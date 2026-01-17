
import moomoo
import logging
from moomoo.common import SysConfig

print("Moomoo version:", moomoo.__version__)
print("SysConfig attributes:")
for attr in dir(SysConfig):
    if not attr.startswith("_"):
        print(attr)

print("\nLogging info:")
try:
    from moomoo.common import ft_logger
    print("Default logger:", ft_logger.logger)
    print("Console logger:", ft_logger.logger.console_logger)
except ImportError:
    print("Could not import ft_logger")
