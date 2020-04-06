"""WebSocket IO definition."""

import json
import time
import asyncio
import websockets
import numpy as np

from threading import Thread, Event

from .io import IO


class WsIO(IO):
    """WebSocket IO implementation."""

    ws = None

    def __init__(self, part_name):
        """Init an io attached to the given part."""
        self.part_name = part_name
        self.motors = []

    @classmethod
    def shared_server(cls, part_name):
        """Create a new io with its ws server."""
        io = cls(part_name)

        if cls.ws is None:
            cls.ws = WsServer()
            cls.ws.run_in_background()
        cls.ws.register(io)

        return io

    def find_module(self, module_name):
        """Get a specific module from the IO.

        For the moment no module are really implemented. Only placeholders for code compatibility are provided.
        """
        if module_name == 'force_gripper':
            return WsFakeForceSensor()

        raise NotImplementedError

    def find_dxl(self, dxl_name, dxl_id):
        """Get a specific dynamixel motor from the IO.

        Only goal position is used atm.
        """
        m = WsMotor(name=f'{self.part_name}.{dxl_name}')
        self.motors.append(m)
        return m

    def find_orbital_disks(self):
        """Get a specific orbita module from the IO.

        Not currently supported.
        """
        raise NotImplementedError

    def close(self):
        """Close the WS."""
        self.ws.close()


class WsMotor(object):
    """Motor Placeholder.

    Only the goal position (ie. target_rot_position) is currently used.
    """

    def __init__(self, name):
        """Init the fake motor."""
        self.name = name

        self.compliant = False
        self.rot_position = 0
        self.target_rot_position = 0


class WsFakeForceSensor(object):
    """Force Sensor placeholder.

    Always return a nan as force.
    """

    def __init__(self):
        """Init the fake force sensor."""
        self.load = np.nan


class WsServer(object):
    """WebSocket server, sync value from the modules with their equivalent from the client."""

    def __init__(self, host='0.0.0.0', port=6171):
        """Prepare the ws server."""
        self.host, self.port = host, port
        self.running = Event()

        self.parts = []

    async def sync(self, websocket, path):
        """Sync loop that exchange modules state with the client."""
        self.running.set()

        while self.running.is_set():
            msg = json.dumps({
                'motors': [
                    {'name': m.name, 'goal_position': m.target_rot_position}
                    for m in sum([p.motors for p in self.parts], [])
                ]
            })
            await websocket.send(msg.encode('UTF-8'))
            time.sleep(0.01)

    def close(self):
        """Stop the sync loop."""
        self.running.clear()
        self.t.join()

    def register(self, io):
        """Register a new io (and its module) to be synced."""
        self.parts.append(io)

    def run_forever(self):
        """Run the sync loop forever."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        serve = websockets.serve(self.sync, self.host, self.port)

        loop.run_until_complete(serve)
        loop.run_forever()

    def run_in_background(self):
        """Run the sync loop forever in background."""
        self.t = Thread(target=self.run_forever)
        self.t.daemon = True
        self.t.start()