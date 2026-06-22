import obspython as obs
import socket

# For connecting a local TCP server to use LiveSplit commands
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 16834))
# No stoping OBS while script working
s.setblocking(False)

def start_recording():
    try:
        s.send(b"getsplitindex\r\n")
        split_index = s.recv(128).decode().strip("\n")
        # That if statement needs some improvements
        if split_index >= "0":
            obs.obs_frontend_recording_start()
    except BlockingIOError:
        pass

# A update function every tick
def script_tick(seconds):
    is_recording = obs.obs_frontend_recording_active()
    if is_recording == False:
        start_recording()