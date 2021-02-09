from flask import Response, request
import json


class Discover_JSON():
    endpoints = ["/discover.json", "/hdhr/discover.json"]
    endpoint_name = "hdhr_discover_json"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.get(*args)

    @property
    def source(self):
        if self.fhdhr.config.dict["hdhr"]["source"]:
            return self.fhdhr.config.dict["hdhr"]["source"]
        elif len(self.fhdhr.origins.valid_origins):
            return self.fhdhr.origins.valid_origins[0]
        else:
            return None

    def get(self, *args):

        base_url = request.url_root[:-1]

        if self.source in self.fhdhr.origins.valid_origins:

            origindiscover = {
                                "FriendlyName": "%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], self.source),
                                "Manufacturer": self.fhdhr.config.dict["hdhr"]["reporting_manufacturer"],
                                "ModelNumber": self.fhdhr.config.dict["hdhr"]["reporting_model"],
                                "FirmwareName": self.fhdhr.config.dict["hdhr"]["reporting_firmware_name"],
                                "TunerCount": self.fhdhr.origins.origins_dict[self.source].tuners,
                                "FirmwareVersion": self.fhdhr.config.dict["hdhr"]["reporting_firmware_ver"],
                                "DeviceID": "%s%s" % (self.fhdhr.config.dict["main"]["uuid"], self.source),
                                "DeviceAuth": self.fhdhr.config.dict["fhdhr"]["device_auth"],
                                "BaseURL": "%s/hdhr/%s" % (base_url, self.source),
                                "LineupURL": "%s/hdhr/%s/lineup.json" % (base_url, self.source)
                            }
        else:
            origindiscover = {}

        discover_json = json.dumps(origindiscover, indent=4)

        return Response(status=200,
                        response=discover_json,
                        mimetype='application/json')
