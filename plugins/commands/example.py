from commands import Command


class Example(Command):

    DESCRIPTION = "Plugin-based example command"

    def run(self):
        print("I turned myself into an example command! Example-Command-Rick!")
