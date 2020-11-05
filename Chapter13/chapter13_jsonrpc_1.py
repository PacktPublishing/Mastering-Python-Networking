# Based on ryu/services/protocols/bgp/api/jsonrpc.py

from ryu.base import app_manager
from ryu.lib import hub
from ryu.app.wsgi import websocket, ControllerBase, WSGIApplication
from ryu.app.wsgi import rpc_public, WebSocketRPCServer
from ryu.services.protocols.bgp.api.base import call
from ryu.services.protocols.bgp.api.base import PREFIX
from ryu.services.protocols.bgp.rtconf.common import LOCAL_AS
from ryu.services.protocols.bgp.rtconf.common import ROUTER_ID
from ryu.services.protocols.bgp.rtconf import neighbors


bgp_instance_name = 'bgp_api_app'
url = '/bgp/ws'


class BgpWSJsonRpc(app_manager.RyuApp):
    _CONTEXTS = {
        'wsgi': WSGIApplication,
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the rpc manager.

        Args:
            self: (todo): write your description
        """
        super(BgpWSJsonRpc, self).__init__(*args, **kwargs)

        wsgi = kwargs['wsgi']
        wsgi.register(
            BgpWSJsonRpcController,
            data={bgp_instance_name: self},
        )
        self._ws_manager = wsgi.websocketmanager

    @rpc_public('core.start')
    def _core_start(self, as_number=64512, router_id='10.0.0.1'):
        """
        Starts a new application.

        Args:
            self: (todo): write your description
            as_number: (int): write your description
            router_id: (str): write your description
        """
        common_settings = {}
        common_settings[LOCAL_AS] = as_number
        common_settings[ROUTER_ID] = str(router_id)
        waiter = hub.Event()
        call('core.start', waiter=waiter, **common_settings)
        waiter.wait()
        return {}

    @rpc_public('neighbor.create')
    def _neighbor_create(self, ip_address='192.168.177.32',
                         remote_as=64513, is_route_reflector_client=False):
        """
        Create neighbor neighbor neighbor.

        Args:
            self: (todo): write your description
            ip_address: (str): write your description
            remote_as: (str): write your description
            is_route_reflector_client: (bool): write your description
        """
        bgp_neighbor = {}
        bgp_neighbor[neighbors.IP_ADDRESS] = str(ip_address)
        bgp_neighbor[neighbors.REMOTE_AS] = remote_as
        bgp_neighbor[neighbors.IS_ROUTE_REFLECTOR_CLIENT] = bool(is_route_reflector_client)
        call('neighbor.create', **bgp_neighbor)
        return {}

    @rpc_public('network.add')
    def _prefix_add(self, prefix='10.20.0.0/24'):
        """
        Add a prefix to the network.

        Args:
            self: (todo): write your description
            prefix: (str): write your description
        """
        networks = {}
        networks[PREFIX] = str(prefix)
        call('network.add', **networks)
        return {}

    @rpc_public('neighbors.get')
    def _neighbors_get(self):
        """
        Get neighbors of neighbors

        Args:
            self: (todo): write your description
        """
        return call('neighbors.get')

    @rpc_public('show.rib')
    def _show_rib(self, family='ipv4'):
        """
        Shows details of the specified show

        Args:
            self: (todo): write your description
            family: (str): write your description
        """
        show = {}
        show['params'] = ['rib', family]
        return call('operator.show', **show)


class BgpWSJsonRpcController(ControllerBase):
    def __init__(self, req, link, data, **config):
        """
        Initialize a flask app.

        Args:
            self: (todo): write your description
            req: (str): write your description
            link: (str): write your description
            data: (todo): write your description
            config: (todo): write your description
        """
        super(BgpWSJsonRpcController, self).__init__(
            req, link, data, **config)
        self.bgp_api_app = data[bgp_instance_name]

    @websocket('bgp', url)
    def _websocket_handler(self, ws):
        """
        Create an rpc server handler.

        Args:
            self: (todo): write your description
            ws: (todo): write your description
        """
        rpc_server = WebSocketRPCServer(ws, self.bgp_api_app)
        rpc_server.serve_forever()
