from commands import Command
from unittest import main

class Test(Command):

    NO_ARGPARSE = True

    def run(self):
        import os
        if os.environ.get("CONDUCTOR_ENV") is None:
            os.environ["CONDUCTOR_ENV"] = "testing"
        from app import tests
        argv = ['micro.py test'] + self.raw_args
        test_program = main(argv=argv, module=tests, exit=False)
        if test_program.result.wasSuccessful():
            return 0
        else:
            return 1
