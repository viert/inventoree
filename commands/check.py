from commands import Command


class Check(Command):

    def init_argument_parser(self, parser):
        parser.add_argument("-f", "--fix", action="store_true", dest="fix", default=False, help="Fix faulty relations")

    def run(self):
        from app.models import Group
        from app.models.group import GroupNotFound
        from app import app
        groups = Group.find({})
        for group in groups:
            cids = []
            pids = []
            for child_id in group.child_ids:
                try:
                    Group._resolve_group(child_id)
                except GroupNotFound:
                    cids.append(child_id)
                    app.logger.error("Group %s has faulty child_id %s" % (group.name, child_id))
            for parent_id in group.parent_ids:
                try:
                    Group._resolve_group(parent_id)
                except GroupNotFound:
                    pids.append(parent_id)
                    app.logger.error("Group %s has faulty parent_id %s" % (group.name, parent_id))

            if self.args.fix:
                for _id in cids:
                    group.child_ids.remove(_id)
                for _id in pids:
                    group.parent_ids.remove(_id)
                if len(cids) + len(pids) > 0:
                    group.save()
                    app.logger.info("Group %s has been fixed. Children removed %d, parents removed %d" %
                                    (group.name, len(cids), len(pids)))