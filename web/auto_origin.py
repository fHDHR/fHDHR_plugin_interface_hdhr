from flask import request, abort, redirect
import urllib.parse


class Auto_Origin():
    endpoints = ['/hdhr/<origin>/auto/<channel>']
    endpoint_name = "hdhr_auto_origin"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, origin, channel, *args):
        return self.get(origin, channel, *args)

    def get(self, origin, channel, *args):

        if origin in self.fhdhr.origins.valid_origins:

            duration = request.args.get('duration', default=0, type=int)
            transcode_quality = request.args.get('transcode', default=None, type=str)
            accessed_url = urllib.parse.quote(request.url)

            channel_number, error = self.interface.channel_number_convert(channel)
            if error:
                self.fhdhr.logger.error(error)
                abort(501, error)

            redirect_url = self.interface.get_tuner_api_url(channel_number, origin, duration, transcode_quality, accessed_url)
            return redirect(redirect_url)

        else:
            abort(501, "Not Implemented")
