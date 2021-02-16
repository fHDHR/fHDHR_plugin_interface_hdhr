import os
import uuid

from .discovery_udp import HDHR_Discovery_Service_UDP
from .discovery_tcp import HDHR_Discovery_Service_TCP


from fHDHR.tools import isint, isfloat, channel_sort
from fHDHR.exceptions import TunerError


class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.generate_or_load_uid()

        self.discover_udp = HDHR_Discovery_Service_UDP(fhdhr, plugin_utils, self)
        self.discover_tcp = HDHR_Discovery_Service_TCP(fhdhr, plugin_utils, self)

    def run_thread(self):
        if "hdhr_udp_discovery" in list(self.fhdhr.threads.keys()):
            self.fhdhr.threads["hdhr_udp_discovery"].start()
        if "hdhr_tcp_discovery" in list(self.fhdhr.threads.keys()):
            self.fhdhr.threads["hdhr_tcp_discovery"].start()

    def generate_or_load_uid(self):
        uid_file = os.path.join(self.plugin_utils.config.internal["paths"]["cache_dir"], 'hdhr_uid')
        if os.path.exists(uid_file):
            with open(uid_file, "r") as f:
                self.base_uid = f.readline().rstrip()
            self.fhdhr.logger.info("Loaded HDHR Base UID: %s" % self.base_uid)
        else:
            self.base_uid = str(uuid.uuid1())
            with open(uid_file, "w") as f:
                f.write(str(self.base_uid))
                self.fhdhr.logger.info("Generated HDHR Base UID: %s" % self.base_uid)

    def get_origin_uid(self, origin):
        return str(uuid.uuid5(uuid.UUID(self.base_uid), str(origin)))

    @property
    def source(self):
        if self.plugin_utils.config.dict["hdhr"]["source"]:
            return self.plugin_utils.config.dict["hdhr"]["source"]
        elif len(self.plugin_utils.origins.valid_origins):
            return self.plugin_utils.origins.valid_origins[0]
        else:
            return None

    def get_DeviceID(self, origin):
        uid = self.get_origin_uid(origin)
        device_id = int(uid[:8], 16)  # Hex string to int
        valid_id = device_id + self.device_id_checksum(device_id)
        return hex(valid_id)[2:]

    def device_id_checksum(self, device_id):
        """Generate a HDHomerun checksum for a device ID.
        HDHomerun considers a device to be valid if the checksum
        is 0. Adding the checksum to the device ID will
        provide a valid checksum though.
        Args:
            device_id (int): Device ID
        Returns:
            int: Checksum of the device id.
        """
        lookup_table = [0xA, 0x5, 0xF, 0x6, 0x7, 0xC, 0x1,
                        0xB, 0x9, 0x2, 0x8, 0xD, 0x4, 0x3, 0xE, 0x0]
        checksum = 0
        checksum ^= lookup_table[(device_id >> 28) & 0x0F]
        checksum ^= (device_id >> 24) & 0x0F
        checksum ^= lookup_table[(device_id >> 20) & 0x0F]
        checksum ^= (device_id >> 16) & 0x0F
        checksum ^= lookup_table[(device_id >> 12) & 0x0F]
        checksum ^= (device_id >> 8) & 0x0F
        checksum ^= lookup_table[(device_id >> 4) & 0x0F]
        checksum ^= (device_id >> 0) & 0x0F

        return checksum

    def channel_number_convert(self, channel):

        if channel.startswith("v"):
            channel_number = channel.replace('v', '')
            if not isint(channel_number) and not isfloat(channel_number):
                return None, ("Invalid Channel %s" % channel)
            return channel_number, None

        elif channel.startswith("ch"):
            channel_freq = channel.replace('ch', '').split("-")[0]
            subchannel = None
            if "-" in channel:
                subchannel = channel.replace('ch', '').split("-")[1]
            return None, ("Not Implemented %s-%s" % (channel_freq, subchannel))

        else:
            return None, ("Invalid Channel %s" % channel)

    def get_tuner_api_url(self, channel_number, origin, duration, transcode_quality, accessed_url, tuner_number=None):

        redirect_url = "/api/tuners?method=stream"

        if tuner_number:
            redirect_url += "&tuner=%s" % (tuner_number)

        redirect_url += "&channel=%s" % channel_number
        redirect_url += "&origin=%s" % origin
        redirect_url += "&stream_method=%s" % self.plugin_utils.origins.origins_dict[origin].stream_method

        if duration:
            redirect_url += "&duration=%s" % duration

        if transcode_quality:
            redirect_url += "&transcode=%s" % transcode_quality

        redirect_url += "&accessed=%s" % accessed_url

        return redirect_url

    def get_channel_lineup(self, origin, base_url, show):
        chan_guide = []

        channelslist = {}
        for fhdhr_id in [x["id"] for x in self.plugin_utils.channels.get_channels(origin)]:
            channel_obj = self.plugin_utils.channels.get_channel_obj("id", fhdhr_id, origin)
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
                             'URL': '/hdhr/%s/auto/v%s' % (origin, channel_obj.number),
                             'HD': channel_obj.dict["HD"],
                             "Favorite": channel_obj.dict["favorite"],
                            }
            lineup_dict["URL"] = "%s%s" % (base_url, lineup_dict["URL"])
            if show == "found" and channel_obj.enabled:
                lineup_dict["Enabled"] = 1
            elif show == "found" and not channel_obj.enabled:
                lineup_dict["Enabled"] = 0

            chan_guide.append(lineup_dict)

        return chan_guide

    def get_discover_dict(self, origin, base_url):
        origindiscover = {
                            "FriendlyName": "%s %s" % (self.plugin_utils.config.dict["fhdhr"]["friendlyname"], origin),
                            "Manufacturer": self.plugin_utils.config.dict["hdhr"]["reporting_manufacturer"],
                            "ModelNumber": self.plugin_utils.config.dict["hdhr"]["reporting_model"],
                            "FirmwareName": self.plugin_utils.config.dict["hdhr"]["reporting_firmware_name"],
                            "TunerCount": self.plugin_utils.origins.origins_dict[origin].tuners,
                            "FirmwareVersion": self.plugin_utils.config.dict["hdhr"]["reporting_firmware_ver"],
                            "DeviceID": self.get_DeviceID(origin),
                            "DeviceAuth": self.plugin_utils.config.dict["fhdhr"]["device_auth"],
                            "BaseURL": "%s/hdhr/%s" % (base_url, origin),
                            "LineupURL": "%s/hdhr/%s/lineup.json" % (base_url, origin)
                        }
        return origindiscover

    def lineup_post_scan_start(self, origin):
        try:
            self.plugin_utils.tuners.tuner_scan(origin)
        except TunerError as e:
            self.plugin_utils.logger.info(str(e))

    def lineup_post_scan_abort(self, origin):
        self.plugin_utils.tuners.stop_tuner_scan(origin)

    def lineup_post_favorite(self, origin, favorite):
        channel_method = favorite['favorite'][0]
        channel_number = favorite['favorite'][1:]

        if str(channel_number) not in [str(x) for x in self.plugin_utils.channels.get_channel_list("number", origin)]:
            return "801 - Unknown Channel"

        if channel_method == "+":
            self.plugin_utils.channels.set_channel_enablement("number", channel_number, channel_method, origin)
        elif channel_method == "-":
            self.plugin_utils.channels.set_channel_enablement("number", channel_number, channel_method, origin)
        elif channel_method == "x":
            self.plugin_utils.channels.set_channel_enablement("number", channel_number, "toggle", origin)

        return None

    def lineup_status(self, origin):
        tuner_status = self.plugin_utils.tuners.status(origin)

        tuners_scanning = 0
        for tuner_number in list(tuner_status.keys()):
            if tuner_status[tuner_number]["status"] == "Scanning":
                tuners_scanning += 1

        if tuners_scanning:
            jsonlineup = self.scan_in_progress(origin)
        else:
            jsonlineup = self.not_scanning()

        return jsonlineup

    def scan_in_progress(self, origin):
        jsonlineup = {
                      "ScanInProgress": "true",
                      "Progress": 99,
                      "Found": len(list(self.plugin_utils.channels.list[origin].keys()))
                      }
        return jsonlineup

    def not_scanning(self):
        jsonlineup = {
                      "ScanInProgress": "false",
                      "ScanPossible": "true",
                      "Source": self.plugin_utils.config.dict["hdhr"]["reporting_tuner_type"],
                      "SourceList": [self.plugin_utils.config.dict["hdhr"]["reporting_tuner_type"]],
                      }
        return jsonlineup
