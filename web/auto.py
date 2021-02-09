from flask import request, abort, redirect
import urllib.parse


class Auto():
    endpoints = ['/auto/<channel>', '/hdhr/auto/<channel>']
    endpoint_name = "hdhr_auto"

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, channel, *args):
        return self.get(channel, *args)

    @property
    def source(self):
        if self.fhdhr.config.dict["hdhr"]["source"]:
            return self.fhdhr.config.dict["hdhr"]["source"]
        elif len(self.fhdhr.origins.valid_origins):
            return self.fhdhr.origins.valid_origins[0]
        else:
            return None

    def get(self, channel, *args):

        if self.source in self.fhdhr.origins.valid_origins:

            redirect_url = "/api/tuners?method=stream"

            if channel.startswith("v"):
                channel_number = channel.replace('v', '')
            elif channel.startswith("ch"):
                channel_freq = channel.replace('ch', '').split("-")[0]
                subchannel = None
                if "-" in channel:
                    subchannel = channel.replace('ch', '').split("-")[1]
                if subchannel:
                    self.fhdhr.logger.error("Not Implemented %s-%s" % (channel_freq, subchannel))
                    abort(501, "Not Implemented %s-%s" % (channel_freq, subchannel))
                else:
                    self.fhdhr.logger.error("Not Implemented %s" % (channel_freq, subchannel))
                    abort(501, "Not Implemented %s" % channel_freq)
            else:
                channel_number = channel

            redirect_url += "&channel=%s" % str(channel_number)
            redirect_url += "&origin=%s" % str(self.source)
            redirect_url += "&stream_method=%s" % self.fhdhr.origins.origins_dict[self.source].stream_method

            duration = request.args.get('duration', default=0, type=int)
            if duration:
                redirect_url += "&duration=%s" % str(duration)

            transcode_quality = request.args.get('transcode', default=None, type=str)
            if transcode_quality:
                redirect_url += "&transcode=%s" % str(transcode_quality)

            redirect_url += "&accessed=%s" % urllib.parse.quote(request.url)

            return redirect(redirect_url)

        else:
            abort(501, "Not Implemented")
