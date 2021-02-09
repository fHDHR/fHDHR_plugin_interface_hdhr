

from .device_xml import HDHR_Device_XML
from .hdhr_html import HDHR_HTML

from .discover_json import Discover_JSON
from .discover_json_origin import Discover_JSON_Origin

from .lineup_json import Lineup_JSON
from .lineup_json_origin import Lineup_JSON_Origin

from .lineup_xml import Lineup_XML
from .lineup_xml_origin import Lineup_XML_Origin

from .lineup_status_json import Lineup_Status_JSON
from .lineup_status_json_origin import Lineup_Status_JSON_Origin


from .lineup_post import Lineup_Post
from .lineup_post_origin import Lineup_Post_Origin

from .auto import Auto
from .auto_origin import Auto_Origin

from .tuner import Tuner
from .tuner_origin import Tuner_Origin


class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.device_xml = HDHR_Device_XML(fhdhr)
        self.hdhr_html = HDHR_HTML(fhdhr, plugin_utils)

        self.discover_json = Discover_JSON(fhdhr)
        self.discover_json_origin = Discover_JSON_Origin(fhdhr)

        self.lineup_json = Lineup_JSON(fhdhr)
        self.lineup_json_origin = Lineup_JSON_Origin(fhdhr)

        self.lineup_xml = Lineup_XML(fhdhr)
        self.lineup_xml_origin = Lineup_XML_Origin(fhdhr)

        self.lineup_post = Lineup_Post(fhdhr)
        self.lineup_post_origin = Lineup_Post_Origin(fhdhr)

        self.lineup_status_json = Lineup_Status_JSON(fhdhr)
        self.lineup_status_json_origin = Lineup_Status_JSON_Origin(fhdhr)

        self.auto = Auto(fhdhr)
        self.auto_origin = Auto_Origin(fhdhr)

        self.tuner = Tuner(fhdhr)
        self.tuner_origin = Tuner_Origin(fhdhr)
