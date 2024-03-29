from flask import Response, request
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import sub_el


class HDHR_Device_XML():
    endpoints = ["/hdhr/<origin>/device.xml"]
    endpoint_name = "hdhr_device_xml_origin"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

        self.schema = "urn:schemas-upnp-org:device:MediaServer:1"

    def __call__(self, origin, *args):
        origin_name = origin
        return self.get(origin_name, *args)

    def get(self, origin_name, *args):
        """Device.xml referenced from SSDP"""

        base_url = request.url_root[:-1]

        out = xml.etree.ElementTree.Element('root')
        out.set('xmlns', "urn:schemas-upnp-org:device-1-0")

        if origin_name in self.fhdhr.origins.list_origins:
            origin_obj = self.fhdhr.origins.get_origin_obj(origin_name)

            origin_plugin_name = origin_obj.plugin_utils.plugin_name
            origin_plugin_version = origin_obj.plugin_utils.plugin_manifest["version"]

            sub_el(out, 'URLBase', "%s/hdhr/%s" % (base_url, origin_name))

            specVersion_out = sub_el(out, 'specVersion')
            sub_el(specVersion_out, 'major', "1")
            sub_el(specVersion_out, 'minor', "0")

            device_out = sub_el(out, 'device')

            sub_el(device_out, 'deviceType', self.schema)

            sub_el(device_out, 'friendlyName', "%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], origin_name))
            sub_el(device_out, 'manufacturer', self.fhdhr.config.dict["hdhr"]["reporting_manufacturer"])
            sub_el(device_out, 'manufacturerURL', "https://github.com/fHDHR/%s" % origin_plugin_name)
            sub_el(device_out, 'modelName', self.fhdhr.config.dict["hdhr"]["reporting_model"])
            sub_el(device_out, 'modelNumber', origin_plugin_version)

            sub_el(device_out, 'serialNumber')

            sub_el(device_out, 'UDN', "uuid:%s%s" % (self.fhdhr.config.dict["main"]["uuid"], origin_name))

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        device_xml = fakefile.getvalue()

        return Response(status=200,
                        response=device_xml,
                        mimetype='application/xml')
