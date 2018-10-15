from commands import Command
from unittest import main
import logging


class Test(Command):

    NO_ARGPARSE = True

    def run(self, *args, **kwargs):
        from app.models import WorkGroup, Group, Host, Datacenter, User, ApiAction, Token, ServerGroup
        from app import app
        from app import tests
        app.logger.level = logging.ERROR

        WorkGroup._collection = 'test_work_groups'
        Group._collection = 'test_groups'
        Host._collection = 'test_hosts'
        Datacenter._collection = 'test_datacenters'
        User._collection = 'test_users'
        ApiAction._collection = 'test_api_actions'
        Token._collection = 'test_tokens'
        ServerGroup._collection = 'test_server_groups'

        argv = ['micro.py test'] + self.raw_args
        test_program = main(argv=argv, module=tests, exit=False)
        if test_program.result.wasSuccessful():
            return 0
        else:
            return 1
