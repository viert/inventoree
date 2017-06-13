#
# Puppet ENC proof of concept module
# To be removed from conductor to remain as an API plugin
# in the future
#
#   Adds /api/ext/puppet/enc/<host_id> url which acts as puppet ENC
#   Puppet data is encoded in conductor tags the following way:
#
#   Tag $puppet_class:<class_name> adds specified class
#   Tag $puppet_param:<param_key>=<param_value> adds classifier parameter
#   Tag $puppet_env:<environment_name> adds classifier environment
#
#   All tags are processed sequentally in random order, having several parameters
#   with the same key results in undefined behaviour: you'll never be sure what
#   exact value is used
#

import re
import yaml
from flask import make_response
from library.engine.utils import resolve_id, json_response, paginated_data, json_exception
from app.controllers.auth_controller import AuthController

puppet_ctrl = AuthController("puppet", __name__, require_auth=False)


CLASS_EXPR = re.compile(r"^\$puppet_class:(.+)$")
PARAM_EXPR = re.compile(r"^\$puppet_param:([^=]+)=(.+)$")
ENV_EXPR = re.compile(r"^$puppet_env:(.+)$")


def yaml_response(data):
    yaml_data = yaml.safe_dump(data, default_flow_style=False)
    return make_response(yaml_data, 200, { "Content-Type": "application/yaml" })

@puppet_ctrl.route("/enc/<host_id>", methods=["GET"])
def enc(host_id):
    from app.models import Host
    host_id = resolve_id(host_id)
    host = Host.find_one({"$or": [
        {"_id": host_id},
        {"fqdn": host_id},
        {"short_name": host_id}
    ]})
    if host is None:
        return json_response({ "errors": [ "Host not found" ]}, 404)

    puppet_data = {
        "classes": [],
        "parameters": {}
    }

    for tag in host.all_tags:
        class_match = CLASS_EXPR.match(tag)
        if class_match is not None:
            puppet_data["classes"].append(class_match.groups()[0])
            continue
        param_match = PARAM_EXPR.match(tag)
        if param_match is not None:
            k,v = param_match.groups()
            puppet_data["parameters"][k] = v
            continue
        env_match = ENV_EXPR.match(tag)
        if env_match is not None:
            puppet_data["environment"] = env_match.groups()[0]

    return yaml_response(puppet_data)