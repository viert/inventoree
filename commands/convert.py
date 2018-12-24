from commands import Command
import re

DELIMITER = re.compile("[:\.]+")


def convert_cf(cf, obj):
    key_tokens = DELIMITER.split(cf["key"])
    node = obj
    while len(key_tokens) > 1:
        token = key_tokens.pop(0)
        if token not in node:
            node[token] = {}
        node = node[token]
    token = key_tokens.pop(0)
    node[token] = cf["value"]


class Convert(Command):

    NAME = "convert"

    def init_argument_parser(self, parser):
        parser.add_argument('action', type=str, choices=['custom', 'host-responsibles'])

    @staticmethod
    def convert_custom():
        from app.models import Group, Host
        from app import app

        for group in Group.find():
            cnt = 0
            app.logger.info("Converting group %s" % group.name)
            for cf in group.custom_fields:
                cnt += 1
                convert_cf(cf, group.local_custom_data)
            group.save()
            if cnt > 0:
                app.logger.info("%d custom fields converted in group %s" % (cnt, group.name))

        for host in Host.find():
            cnt = 0
            app.logger.info("Converting host %s" % host.fqdn)
            for cf in host.custom_fields:
                cnt += 1
                convert_cf(cf, host.local_custom_data)
            host.save()
            if cnt > 0:
                app.logger.info("%d custom fields converted in host %s" % (cnt, host.fqdn))

    @staticmethod
    def convert_host_responsibles():
        from app import app
        from app.models import Host

        for h in Host.find():
            app.logger.debug("Setting host responsibles for host %s" % h.fqdn)
            h.reset_responsibles_cache()
            h.save(skip_callback=True)

    def run(self):
        if self.args.action == 'custom':
            return self.convert_custom()
        elif self.args.action == 'host-responsibles':
            return self.convert_host_responsibles()
