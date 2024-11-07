from easyprocess import EasyProcess

from pyvirtualdisplay.smartdisplay import SmartDisplay

import socket
import time
import numpy as np
import struct
import cv2
import traceback

spf = 1 / 20

def readPose(connection):
    curr = None

    while True:
        try:
            bytes = connection.recv(20, socket.MSG_PEEK)

            if len(bytes) < 20:
                raise Exception()

            curr = connection.recv(20)
        except:
            if curr is None:
                return None

            return struct.unpack('fffff', curr)


def run(executable, code, size, visible=False):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server, SmartDisplay(visible=visible, size=size, manage_global_env=False) as disp:
        server.bind(('localhost', 0))
        # Should probably close
        server.listen(1)

        with EasyProcess([executable, str(server.getsockname()[1])], env=disp.env()) as sim:
            with server.accept()[0] as connection:
                connection.setblocking(0)

                start = time.monotonic()
                pose = None
                while True:
                    image = cv2.cvtColor(np.array(disp.grab(False)), cv2.COLOR_RGB2BGR)
                    new_pose = readPose(connection)
                    if new_pose is not None:
                        pose = new_pose

                    if pose is not None:
                        try:
                            move = code(image, pose, time.monotonic())
                        except:
                            print(traceback.format_exc())
                            break

                        connection.send(struct.pack('ff', *move))
                    else:
                        connection.send(struct.pack('ff', 0, 0))

                    time.sleep(spf - ((time.monotonic() - start) % spf))
