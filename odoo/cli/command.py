from __future__ import print_function
import logging
import sys
import os
from os.path import join as joinpath, isdir

import odoo
from odoo.modules import get_modules, get_module_path

commands = {}


# 自定义一个元类 CommandType
class CommandType(type):
    """
    自定义元类CommandType
    """

    def __init__(cls, name, bases, attrs):
        # 继承type元类的基本功能
        super(CommandType, cls).__init__(name, bases, attrs)
        # 扩展元类额外功能 -增加了一个name属性（来自class的lower字符串）、并将类加入全局commands参数中
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls


# 调用自定义元类CommandType 并返回一个Command类
# 默认一个run的抽象方法 接收self, args两个参数，后面继承类可以重写
# 用元类定义的run方法
Command = CommandType('Command', (object,), {'run': lambda self, args: None})
# 功能同下：
# class Command(object, metaclass=CommandType):
#     def run(self, args):
#         return None


class Help(Command):
    """Display the list of available commands"""
    def run(self, args):
        print("Available commands:\n")
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').strip()
            print("    %s%s" % (name, doc))
        print("\nUse '%s <command> --help' for individual command help." % sys.argv[0].split(os.path.sep)[-1])

def main():
    args = sys.argv[1:]

    # The only shared option is '--addons-path=' needed to discover additional
    # commands from modules
    if len(args) > 1 and args[0].startswith('--addons-path=') and not args[1].startswith("-"):
        # parse only the addons-path, do not setup the logger...
        odoo.tools.config._parse_config([args[0]])
        args = args[1:]

    # Default legacy command
    command = "server"

    # TODO: find a way to properly discover addons subcommands without importing the world
    # Subcommand discovery
    if len(args) and not args[0].startswith("-"):
        logging.disable(logging.CRITICAL)
        for module in get_modules():
            if isdir(joinpath(get_module_path(module), 'cli')):
                __import__('odoo.addons.' + module)
        logging.disable(logging.NOTSET)
        command = args[0]
        args = args[1:]

    if command in commands:
        o = commands[command]()
        o.run(args)
    else:
        sys.exit('Unknow command %r' % (command,))
