from flask import Response, request
import json

from fHDHR.tools import channel_sort


class Lineup_JSON():
    endpoints = ["/lineup.json", "/hdhr/lineup.json"]
    endpoint_name = "hdhr_lineup_json"

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

        show = request.args.get('show', default="all", type=str)

        chan_guide = []

        if self.source in self.fhdhr.origins.valid_origins:

            channelslist = {}
            for fhdhr_id in [x["id"] for x in self.fhdhr.device.channels.get_channels(self.source)]:
                channel_obj = self.fhdhr.device.channels.get_channel_obj("id", fhdhr_id, self.source)
                if channel_obj:
                    if channel_obj.enabled:
                        channelslist[channel_obj.number] = channel_obj

            # Sort the channels
            sorted_channel_list = channel_sort(list(channelslist.keys()))
            for channel in sorted_channel_list:

                channel_obj = channelslist[channel]
                lineup_dict = {
                                 'GuideNumber': channel_obj.number,
                                 'GuideName': channel_obj.dict['name'],
                                 'Tags': ",".join(channel_obj.dict['tags']),
                                 'URL': '/hdhr/auto/v%s' % channel_obj.number,
                                 'HD': channel_obj.dict["HD"],
                                 "Favorite": channel_obj.dict["favorite"],
                                }
                lineup_dict["URL"] = "%s%s" % (base_url, lineup_dict["URL"])
                if show == "found" and channel_obj.enabled:
                    lineup_dict["Enabled"] = 1
                elif show == "found" and not channel_obj.enabled:
                    lineup_dict["Enabled"] = 0

                chan_guide.append(lineup_dict)

        lineup_json = json.dumps(chan_guide, indent=4)

        return Response(status=200,
                        response=lineup_json,
                        mimetype='application/json')
