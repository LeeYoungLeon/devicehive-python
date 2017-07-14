from devicehive.data_formats.json_data_format import JsonDataFormat
from devicehive.connection_handler import ConnectionHandler
import traceback


class DeviceHive(object):
    """Device hive class."""

    def __init__(self, handler_class, handler_options):
        self._handler_options = {'handler_class': handler_class,
                                 'handler_options': handler_options}
        self._transport_name = None
        self._transport = None
        self._transport_exception_info = None

    def _init_transport(self):
        name = 'devicehive.transports.%s_transport' % self._transport_name
        class_name = '%sTransport' % self._transport_name.title()
        transport_module = __import__(name, globals(), locals(), [name])
        transport_class = getattr(transport_module, class_name)
        self._transport = transport_class(JsonDataFormat, {}, ConnectionHandler,
                                          self._handler_options)

    @staticmethod
    def transport_name(transport_url):
        if transport_url[0:4] == 'http':
            return 'http'
        if transport_url[0:2] == 'ws':
            return 'websocket'

    def connect(self, transport_url, **options):
        self._transport_name = self.transport_name(transport_url)
        assert self._transport_name, 'Unexpected transport url scheme'
        authentication = {'login': options.pop('login', None),
                          'password': options.pop('password', None),
                          'refresh_token': options.pop('refresh_token', None),
                          'access_token': options.pop('access_token', None)}
        self._handler_options['authentication'] = authentication
        self._init_transport()
        self._transport.connect(transport_url, **options)

    def join(self, timeout=None):
        self._transport.join(timeout)
        self._transport_exception_info = self._transport.exception_info()

    def exception_info(self):
        return self._transport_exception_info

    def print_exception(self):
        if not self._transport_exception_info:
            return
        traceback.print_exception(self._transport_exception_info[0],
                                  self._transport_exception_info[1],
                                  self._transport_exception_info[2])
