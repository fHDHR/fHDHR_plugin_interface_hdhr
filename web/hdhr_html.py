from flask import request, render_template_string, session
import pathlib
from io import StringIO


class HDHR_HTML():
    endpoints = ["/hdhr", "/hdhr.html"]
    endpoint_name = "page_hdhr_html"
    endpoint_access_level = 2
    endpoint_category = "pages"
    pretty_name = "HDHR"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.template_file = pathlib.Path(plugin_utils.config.dict["plugin_web_paths"][plugin_utils.namespace]["path"]).joinpath('hdhr.html')
        self.template = StringIO()
        self.template.write(open(self.template_file).read())

    def __call__(self, *args):
        return self.get(*args)

    def get(self, *args):

        base_url = request.url_root[:-1]
        origin_dict_list = []
        for origin in self.fhdhr.origins.valid_origins:
            origin_dict_list.append({
                                    "name": origin,
                                    "url": "%s/hdhr/%s" % (base_url, origin)
                                    })

        return render_template_string(self.template.getvalue(), request=request, session=session, fhdhr=self.fhdhr, origin_dict_list=origin_dict_list)
