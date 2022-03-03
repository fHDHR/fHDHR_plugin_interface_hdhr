from flask import request, abort, redirect
import urllib.parse


class Tuner():
    endpoints = ['/tuner<tuner_number>/<channel>', '/hdhr/tuner<tuner_number>/<channel>']
    endpoint_name = "hdhr_tuner"

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, tuner_number, channel, *args):
        return self.get(tuner_number, channel, *args)

    def get(self, tuner_number, channel, *args):

        if self.interface.source in self.fhdhr.origins.list_origins:

            duration = request.args.get('duration', default=0, type=int)
            transcode_quality = request.args.get('transcode', default=None, type=str)
            accessed_url = urllib.parse.quote(request.url)

            channel_number, error = self.interface.channel_number_convert(channel)
            if error:
                self.fhdhr.logger.error(error)
                abort(501, error)

            redirect_url = self.interface.get_tuner_api_url(channel_number, self.interface.source, duration, transcode_quality, accessed_url, tuner_number)
            return redirect(redirect_url)

        else:
            abort(501, "Not Implemented")
