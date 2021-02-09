from flask import Response, request
import json


class Discover_JSON_Origin():
    endpoints = ["/hdhr/<origin>/discover.json"]
    endpoint_name = "hdhr_discover_json_origin"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, origin, *args):
        return self.get(origin, *args)

    def get(self, origin, *args):

        base_url = request.url_root[:-1]

        if origin in self.fhdhr.origins.valid_origins:

            origindiscover = {
                                "FriendlyName": "%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], origin),
                                "Manufacturer": self.fhdhr.config.dict["hdhr"]["reporting_manufacturer"],
                                "ModelNumber": self.fhdhr.config.dict["hdhr"]["reporting_model"],
                                "FirmwareName": self.fhdhr.config.dict["hdhr"]["reporting_firmware_name"],
                                "TunerCount": self.fhdhr.origins.origins_dict[origin].tuners,
                                "FirmwareVersion": self.fhdhr.config.dict["hdhr"]["reporting_firmware_ver"],
                                "DeviceID": "%s%s" % (self.fhdhr.config.dict["main"]["uuid"], origin),
                                "DeviceAuth": self.fhdhr.config.dict["fhdhr"]["device_auth"],
                                "BaseURL": "%s/hdhr/%s" % (base_url, origin),
                                "LineupURL": "%s/hdhr/%s/lineup.json" % (base_url, origin)
                            }
        else:
            origindiscover = {}

        discover_json = json.dumps(origindiscover, indent=4)

        return Response(status=200,
                        response=discover_json,
                        mimetype='application/json')
