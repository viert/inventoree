from commands import Command
from unittest import main
from coverage import coverage
from app import tests

class Test(Command):

    NO_ARGPARSE = True

    def run(self):
        argv = ['micro.py test'] + self.raw_args
        test_program = main(argv=argv, module=tests, exit=False)
        if test_program.result.wasSuccessful():
            return 0
        else:
            return 1
