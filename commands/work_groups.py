from commands import Command
from copy import deepcopy


class WorkGroups(Command):

    NAME = "wg"

    def run(self):
        from app.models import WorkGroup
        from library.db import db

        wgmap = {}
        projects = db.conn.project.find({})
        for p in projects:
            project_id = p["_id"]
            attrs = deepcopy(p)
            del(attrs["_id"])
            wg = WorkGroup.find_one({"name": p["name"]})
            if wg is None:
                print "Creating workgroup %s" % p["name"]
                wg = WorkGroup(**attrs)
                wg.save()
            wgmap[str(project_id)] = wg._id

        groups = db.conn.groups.find({})
        for g in groups:
            if "project_id" not in g:
                print "Group %s doesn't have project_id, thus already converted" % g["name"]
                continue
            print "Converting group %s" % g["name"]
            g_project_id = g["project_id"]
            wg_id = wgmap[str(g_project_id)]
            db.conn.groups.update(
                {"_id": g["_id"]},
                {
                    "$set": {"work_group_id": wg_id},
                    "$unset": {"project_id": ""}
                }
            )

