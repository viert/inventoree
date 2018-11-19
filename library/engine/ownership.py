from flask import g
from app.models import WorkGroup, Group, Host


def user_work_groups(user_id=None):
    if user_id is None:
        if g.user is None:
            return []
        user_id = g.user._id
    return WorkGroup.find({"$or":[
        {"owner_id": user_id},
        {"member_ids": user_id},
    ]})


def user_groups(user_id=None):
    wgs = user_work_groups(user_id)
    if wgs.count() == 0:
        return []
    return Group.find({"work_group_id": {
        "$in": [x._id for x in wgs]
    }})


def user_hosts(user_id=None, include_not_assigned=True):
    grps = user_groups(user_id)
    query = {"group_id": {"$in": [x._id for x in grps]}}
    if include_not_assigned:
        query = {"$or": [
            {"group_id": None},
            query
        ]}
    return Host.find(query)
