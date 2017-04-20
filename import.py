#!/usr/bin/env python

import json
from app.models import User, Project, Group, Datacenter, Host

project_cache = {}

with open('projects.json') as f:
    data = json.load(f)

User.destroy_all()
supervisor = User(username='viert', password_raw='miupass')
supervisor.save()

Project.destroy_all()

print "Processing projects"
for item in data:
    p = Project(name=item["name"],
                description=item["description"],
                email=item["mailto"],
                root_email=item["root_email"],
                owner_id=supervisor._id)
    p.save()
    project_cache[item["name"]] = p

with open("executer_data.json") as f:
    data = json.load(f)

Group.destroy_all()

group_cache = {}
i = 0
print "Processing groups"
for group_name, group_desc in data["Groups"].items():
    project = project_cache[group_desc["project"]]
    g = Group(name=group_name, description=group_desc["description"], project_id=project._id)
    g.save()
    group_cache[group_name] = g
    i += 1
    if i % 1000 == 0:
        print i
print i

i = 0
print "Setting children"
for group_name, group_desc in data["Groups"].items():
    child_ids = []
    for child in group_desc["children"]:
        child_ids.append(group_cache[child]._id)
    if len(child_ids) > 0:
        g = group_cache[group_name]
        for cid in child_ids:
            g.add_child(cid)
    i += 1
    if i % 100 == 0:
        print i
print i

print "Processing datacenters"
Datacenter.destroy_all()
datacenter_cache = {}
for datacenter_name, datacenter_desc in data["Datacenters"].items():
    dc = Datacenter(name=datacenter_name, human_readable=datacenter_desc["golem_name"])
    dc.save()
    datacenter_cache[datacenter_name] = dc

print "Setting parents"
for datacenter_name, datacenter_desc in data["Datacenters"].items():
    if datacenter_desc["parent"] is not None:
        dc = datacenter_cache[datacenter_name]
        parent = datacenter_cache[datacenter_desc["parent"]]
        dc.set_parent(parent)

print "Processing hosts"
Host.destroy_all()
i = 0
for fqdn, host_desc in data["Hosts"].items():
    if host_desc["datacenter"] is not None:
        dc_id = datacenter_cache[host_desc["datacenter"]]._id
    else:
        dc_id = None
    h = Host(fqdn=fqdn,
             datacenter_id=dc_id,
             group_id=group_cache[host_desc["group"]]._id,
             short_name=host_desc["short_name"])
    h.save()
    i += 1
    if i % 1000 == 0:
        print i

print i
print "Done"