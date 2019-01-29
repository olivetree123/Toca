import os
import sys
import argparse
from winney import Winney
from jinja2 import Template

from toca.entity.root import Toca
from toca.utils.errors import ArgumentError


cmd_help = """
usage: toca ACTION [-c toca.toml]

ACTION should be:
    ls           列出所有 API
    run          运行所有 API
    help, -h, --help    打印帮助

optional arguments:
    -c toca.toml  指定配置文件, 默认为当前路径下的 toca.toml
"""


def main():
    args = sys.argv[1:]
    action = args[0] if args else "help"
    if action not in ("ls", "run", "help", "-h", "--help") or len(args) == 2 or (len(args) > 1 and args[1] != "-c"):
        print("Invalid arguments.\nSee 'toca help' for help")
        return
    if action in ("help", "-h", "--help"):
        print(cmd_help)
        return
    config_file = args[2] if len(args) >= 3 else "./toca.toml"
    if not os.path.isfile(config_file):
        raise FileNotFoundError("Toca config file not found, path = {}".format(config_file))
    toca = Toca(config_file)
    func = getattr(toca, action)
    func()


if __name__ == "__main__":
    main()
