from flask import Response, request
import json


class Lineup_JSON_Origin():
    endpoints = ["/hdhr/<origin>/lineup.json"]
    endpoint_name = "hdhr_lineup_json_origin"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, origin, *args):
        return self.get(origin, *args)

    def get(self, origin, *args):

        base_url = request.url_root[:-1]

        show = request.args.get('show', default="all", type=str)

        chan_guide = []
        if origin in self.fhdhr.origins.list_origins:
            chan_guide = self.interface.get_channel_lineup(origin, base_url, show)

        lineup_json = json.dumps(chan_guide, indent=4)

        return Response(status=200,
                        response=lineup_json,
                        mimetype='application/json')
