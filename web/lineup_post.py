from flask import request, abort, Response


class Lineup_Post():
    endpoints = ["/lineup.post", "/hdhr/lineup.post"]
    endpoint_name = "hdhr_lineup_post"
    endpoint_methods = ["POST"]

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = self.fhdhr.device.interfaces[self.plugin_utils.namespace]

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):

        if self.interface.source in self.fhdhr.origins.list_origins:

            if 'scan' in list(request.args.keys()):

                if request.args['scan'] == 'start':
                    self.interface.lineup_post_scan_start(self.interface.source)

                elif request.args['scan'] == 'abort':
                    self.interface.lineup_post_scan_abort(self.interface.source)

                else:
                    self.fhdhr.logger.warning("Unknown scan command %s" % request.args['scan'])
                    return abort(200, "Not a valid scan command")

            elif 'favorite' in list(request.args.keys()):
                if request.args['favorite'].startstwith(tuple(["+", "-", "x"])):

                    error = self.interface.lineup_post_favorite(self.interface.source, request.args['favorite'])
                    if error:
                        response = Response("Not Found", status=404)
                        response.headers["X-fHDHR-Error"] = error
                        self.fhdhr.logger.error(response.headers["X-fHDHR-Error"])
                        abort(response)

                else:
                    self.fhdhr.logger.warning("Unknown favorite command %s" % request.args['favorite'])
                    return abort(200, "Not a valid favorite command")

            else:
                return abort(501, "Not a valid command")

            return Response(status=200, mimetype='text/html')

        else:
            return abort(501, "Not Implemented")
