

class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils, broadcast_ip, max_age):
        self.fhdhr = fhdhr

        self.broadcast_ip = broadcast_ip
        self.device_xml_path = '/hdhr/device.xml'

        self.schema = "urn:schemas-upnp-org:device:MediaServer:1"

        self.max_age = max_age

    @property
    def enabled(self):
        return self.fhdhr.config.dict["hdhr"]["enabled"]

    def create_ssdp_content(self, origin):
        data = ''
        data_command = "NOTIFY * HTTP/1.1"

        device_xml_path = "/hdhr/%s/device.xml" % origin

        data_dict = {
                    "HOST": "%s:%s" % ("239.255.255.250", 1900),
                    "NT": self.schema,
                    "NTS": "ssdp:alive",
                    "USN": 'uuid:%s%s::%s' % (self.fhdhr.config.dict["main"]["uuid"], origin, self.schema),
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
        for origin in self.fhdhr.origins.valid_origins:
            data = self.create_ssdp_content(origin)
            ssdp_content.append(data)
        return ssdp_content
