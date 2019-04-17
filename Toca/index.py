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
    ls                 列出所有 API
    run                运行所有 API
    run api1 api2      运行指定 API
    help, -h, --help   打印帮助

optional arguments:
    -c toca.toml  指定配置文件, 默认为当前路径下的 toca.toml
    -show         显示 API 返回结果。默认只显示 HTTP 状态码，不显示结果
"""


def main():
    args = sys.argv[1:]
    action = args[0] if args else "help"
    if action not in ("ls", "run", "help", "-h", "--help"):
        print("Invalid arguments.\nSee 'toca help' for help")
        return
    if action in ("help", "-h", "--help"):
        print(cmd_help)
        return
    api_list = []
    show = False
    config_file = "./toca.toml"
    if len(args) > 1:
        for i in range(len(args)):
            if i == 0: continue;
            if args[i] in ["-c", "-show"]: 
                break
            api_list.append(args[i])
        for i in range(len(args)):
            if args[i] == "-c":
                config_file = args[i+1]
            elif args[i] == "-show":
                show = True
    if not os.path.isfile(config_file):
        raise FileNotFoundError("Toca config file not found, path = {}".format(config_file))
    toca = Toca(config_file)
    func = getattr(toca, action)
    if action == "run":
        func(api_list=api_list, show=show)
    else:
        func()


if __name__ == "__main__":
    main()
