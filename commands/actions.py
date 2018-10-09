from commands import Command
from datetime import datetime, timedelta

DEFAULT_ACTION_LOG_TTL = 86400 * 31 * 6 # approximately half a year


class Actions(Command):

    def init_argument_parser(self, parser):
        parser.add_argument('action_name', nargs=1, choices=['count', 'cleanup'])

    def run(self):
        from app import app
        from app.models import ApiAction
        ttl = app.config.app.get("ACTION_LOG_TTL", DEFAULT_ACTION_LOG_TTL)
        delta = timedelta(seconds=ttl)
        min_date = datetime.utcnow() - delta

        action_name = self.args.action_name[0]
        ttl_query = {"created_at": {"$lt": min_date}}

        expired = ApiAction.find(ttl_query).count()

        if action_name == 'count':
            total = ApiAction.find().count()
            print "ApiActions count, total = %d, expired = %d" % (total, expired)
            return

        if action_name == 'cleanup':
            if expired == 0:
                print "There's no expired actions to cleanup"
            ApiAction.destroy_many(ttl_query)
            print "%d expired ApiActions removed" % expired
