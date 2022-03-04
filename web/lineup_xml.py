from flask import Response, request
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import sub_el


class Lineup_XML():
    endpoints = ["/lineup.xml", "/hdhr/lineup.xml"]
    endpoint_name = "hdhr_lineup_xml"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        base_url = request.url_root[:-1]

        show = request.args.get('show', default="all", type=str)

        chan_guide = []
        if self.interface.source in self.fhdhr.origins.list_origins:
            chan_guide = self.interface.get_channel_lineup(self.interface.source, base_url, show)

        out = xml.etree.ElementTree.Element('Lineup')
        for lineup_dict in chan_guide:
            program_out = sub_el(out, 'Program')
            for key in list(lineup_dict.keys()):
                sub_el(program_out, str(key), str(lineup_dict[key]))

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        lineup_xml = fakefile.getvalue()

        return Response(status=200,
                        response=lineup_xml,
                        mimetype='application/xml')
