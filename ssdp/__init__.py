

class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr

        self.device_xml_path = '/hdhr/device.xml'

        # self.schema = "urn:schemas-upnp-org:device:MediaServer:1"
        self.schema = "upnp:rootdevice"

    @property
    def max_age(self):
        return self.fhdhr.config.dict["hdhr"]["ssdp_max_age"]

    @property
    def interface(self):
        return self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def create_ssdp_content(self, origin_name):
        data = ''
        data_command = "NOTIFY * HTTP/1.1"

        device_xml_path = "/hdhr/%s/device.xml" % origin_name

        data_dict = {
                    "HOST": "%s:%s" % ("239.255.255.250", 1900),
                    "NT": self.schema,
                    "ST": self.schema,
                    "NTS": "ssdp:alive",
                    "USN": 'uuid:%s::%s' % (self.interface.get_DeviceID(origin_name), self.schema),
                    "SERVER": 'fHDHR/%s UPnP/1.0' % self.fhdhr.version,
                    "LOCATION": "%s%s" % (self.fhdhr.api.base, device_xml_path),
                    "AL": "%s%s" % (self.fhdhr.api.base, device_xml_path),
                    "Cache-Control:max-age=": self.max_age
                    }

        data += "%s\r\n" % data_command
        for data_key in list(data_dict.keys()):
            data += "%s:%s\r\n" % (data_key, data_dict[data_key])
        data += "\r\n"

        return data

    @property
    def notify(self):
        ssdp_content = []
        for origin_name in self.fhdhr.origins.list_origins:
            data = self.create_ssdp_content(origin_name)
            ssdp_content.append(data)
        return ssdp_content
