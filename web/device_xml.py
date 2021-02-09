from flask import Response, request
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import sub_el


class HDHR_Device_XML():
    endpoints = ["/hdhr/<origin>/device.xml"]
    endpoint_name = "hdhr_device_xml_origin"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.schema = "urn:schemas-upnp-org:device:MediaServer:1"

    def __call__(self, origin, *args):
        return self.get(origin, *args)

    def get(self, origin, *args):
        """Device.xml referenced from SSDP"""

        base_url = request.url_root[:-1]

        out = xml.etree.ElementTree.Element('root')
        out.set('xmlns', "urn:schemas-upnp-org:device-1-0")

        if origin in self.fhdhr.origins.valid_origins:

            origin_plugin_name = self.fhdhr.origins.origins_dict[origin].plugin_utils.plugin_name
            origin_plugin_version = self.fhdhr.origins.origins_dict[origin].plugin_utils.plugin_manifest["version"]

            sub_el(out, 'URLBase', "%s/hdhr/%s" % (base_url, origin))

            specVersion_out = sub_el(out, 'specVersion')
            sub_el(specVersion_out, 'major', "1")
            sub_el(specVersion_out, 'minor', "0")

            device_out = sub_el(out, 'device')

            sub_el(device_out, 'deviceType', self.schema)

            sub_el(device_out, 'friendlyName', "%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], origin))
            sub_el(device_out, 'manufacturer', self.fhdhr.config.dict["hdhr"]["reporting_manufacturer"])
            sub_el(device_out, 'manufacturerURL', "https://github.com/fHDHR/%s" % origin_plugin_name)
            sub_el(device_out, 'modelName', self.fhdhr.config.dict["hdhr"]["reporting_model"])
            sub_el(device_out, 'modelNumber', origin_plugin_version)

            sub_el(device_out, 'serialNumber')

            sub_el(device_out, 'UDN', "uuid:%s%s" % (self.fhdhr.config.dict["main"]["uuid"], origin))

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        device_xml = fakefile.getvalue()

        return Response(status=200,
                        response=device_xml,
                        mimetype='application/xml')
