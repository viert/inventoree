import sys
import pkgutil
import inspect
from argparse import ArgumentParser, REMAINDER


class Command(object):
    """Base class for CLI commands
    You should override at least run() method
        run() - method is being called to do the main job
        init_argument_parser(parser) - override this method if you want to accept arguments
        NAME - if this property is not None it is used as command name.
               Otherwise command name is generated from class name
        DESCRIPTION - description that is used in help messages. Consider setting it to something meaningful.
    """
    NAME = None
    DESCRIPTION = None
    NO_ARGPARSE = False

    def __init__(self):
        if self.NAME is None:
            self.NAME = self.__class__.__name__.lower()
        if self.DESCRIPTION is None:
            self.DESCRIPTION = '"%s" has no DESCRIPTION' % (self.NAME,)
        self.args = None
        self.raw_args = None

    def init_argument_parser(self, parser):
        """
        This method is called to configure argument subparser for command
        Override it if you need to accept arguments
          - parser: argparse.ArgumentParser to fill with arguments
        """
        pass

    def run(self):
        """
        This is a main method of command. Override it and do all the job here
        Command arguments can be read from self.args
        The return value from this method will be used as CLI exit code
        """
        raise NotImplementedError()


def is_a_command_class(obj):
    return inspect.isclass(obj) and Command in inspect.getmro(obj) and obj != Command


def load_commands_from_module(module):
    return [obj for _, obj in inspect.getmembers(module) if is_a_command_class(obj)]


def load_commands_from_package(package):
    commands = []

    for modloader, modname, ispkg in pkgutil.iter_modules(package.__path__):
        module = modloader.find_module(modname).load_module(modname)
        commands.extend(load_commands_from_module(module))

        if ispkg:
            commands.extend(load_commands_from_package(module))
    return commands


def load_commands():
    commands = []
    this_module = sys.modules[__name__]

    if this_module.__package__:
        commands = load_commands_from_package(sys.modules[this_module.__package__])

    try:
        import plugins.commands
        commands.extend(load_commands_from_package(plugins.commands))
    except ImportError:
        pass

    commands.extend(load_commands_from_module(this_module))
    return commands


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(
        title='Commands',
        help="One of the following commands",
        description='use <command> --help to get help on particular command',
        metavar="<command>",
    )
    for command_class in load_commands():
        command = command_class()
        if command.NO_ARGPARSE:
            command_parser = subparsers.add_parser(
                command.NAME,
                help=command.DESCRIPTION,
                add_help=False,
                prefix_chars=chr(0),  # Ugly hack to prevent arguments from being parsed as options
            )
            command_parser.add_argument('raw_args', nargs=REMAINDER)
        else:
            command_parser = subparsers.add_parser(command.NAME, help=command.DESCRIPTION)
        command_parser.set_defaults(command=command)
        command.init_argument_parser(command_parser)

    args = parser.parse_args()
    args.command.args = args
    if 'raw_args' in args:
        args.command.raw_args = args.raw_args
    return args.command.run()