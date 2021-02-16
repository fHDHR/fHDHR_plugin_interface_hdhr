from flask import Response
import json


class Lineup_Status_JSON_Origin():
    endpoints = ["/hdhr/<origin>/lineup_status.json"]
    endpoint_name = "hdhr_lineup_status_json_origin"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, origin, *args):
        return self.get(origin, *args)

    def get(self, origin, *args):

        jsonlineup = {}
        if origin in self.fhdhr.origins.valid_origins:
            jsonlineup = self.interface.lineup_status(self.interface.source)

        return Response(status=200,
                        response=json.dumps(jsonlineup, indent=4),
                        mimetype='application/json')
