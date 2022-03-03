from flask import Response
import json


class Lineup_Status_JSON():
    endpoints = ["/lineup_status.json", "/hdhr/lineup_status.json"]
    endpoint_name = "hdhr_lineup_status_json"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        jsonlineup = {}
        if self.interface.source in self.fhdhr.origins.list_origins:
            jsonlineup = self.interface.lineup_status(self.interface.source)

        return Response(status=200,
                        response=json.dumps(jsonlineup, indent=4),
                        mimetype='application/json')
