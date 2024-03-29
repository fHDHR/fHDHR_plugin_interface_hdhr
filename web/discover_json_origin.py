from flask import Response, request
import json


class Discover_JSON_Origin():
    endpoints = ["/hdhr/<origin>/discover.json"]
    endpoint_name = "hdhr_discover_json_origin"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, origin, *args):
        origin_name = origin
        return self.get(origin_name, *args)

    def get(self, origin_name, *args):

        base_url = request.url_root[:-1]

        origindiscover = {}
        if origin_name in self.fhdhr.origins.list_origins:
            origindiscover = self.interface.get_discover_dict(origin_name, base_url)

        return Response(status=200,
                        response=json.dumps(origindiscover, indent=4),
                        mimetype='application/json')
