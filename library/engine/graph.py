
def _group_parents_recursive(group, fields, host_fields):
    result = group.to_dict(fields)
    result["hosts"] = [x.to_dict(host_fields) for x in group.hosts]
    result["parents"] = []
    for parent in group.parents:
        result["parents"].append(_group_parents_recursive(parent, fields, host_fields))
    return result


def _group_children_recursive(group, fields, host_fields):
    result = group.to_dict(fields)
    result["hosts"] = [x.to_dict(host_fields) for x in group.hosts]
    result["children"] = []
    for child in group.children:
        result["children"].append(_group_children_recursive(child, fields, host_fields))
    return result


def group_structure(group, fields, host_fields):
    result = group.to_dict(fields)
    result["hosts"] = [x.to_dict(host_fields) for x in group.hosts]
    result["parents"] = _group_parents_recursive(group, fields, host_fields)["parents"]
    result["children"] = _group_children_recursive(group, fields, host_fields)["children"]
    return result