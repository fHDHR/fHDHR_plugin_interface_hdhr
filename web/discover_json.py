from flask import Response, request
import json


class Discover_JSON():
    endpoints = ["/discover.json", "/hdhr/discover.json"]
    endpoint_name = "hdhr_discover_json"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        base_url = request.url_root[:-1]

        origindiscover = {}
        if self.interface.source in self.fhdhr.origins.list_origins:
            origindiscover = self.interface.get_discover_dict(self.interface.source, base_url)

        return Response(status=200,
                        response=json.dumps(origindiscover, indent=4),
                        mimetype='application/json')
