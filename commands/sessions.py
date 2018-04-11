from commands import Command


class Sessions(Command):

    def init_argument_parser(self, parser):
        parser.add_argument("action", type=str, nargs=1, choices=["cleanup", "count"])

    def run(self):
        from library.db import db
        from datetime import datetime
        action = self.args.action[0]
        if action == "count":
            total = db.ro_conn["sessions"].find().count()
            expired = db.ro_conn["sessions"].find({"expiration": {"$lt": datetime.now()}}).count()
            print "Total number of sessions: %d, expired: %d" % (total, expired)
            if expired > 0:
                print "Use <micro.py sessions cleanup> to remove old sessions manually"

        elif action == "cleanup":
            print "Starting sessions clean up process..."
            count = db.cleanup_sessions()
            if count == 0:
                print "There's no expired sessions to clean up"
            else:
                print "%d expired sessions have been cleaned up" % count
