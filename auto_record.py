import obspython as obs
import socket

s = None

# It needs for protecting OBS from stopping if something wrong with socket connection
def connect():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 16834))
        # No stoping OBS while script working
        s.setblocking(False)
        print("Connected to the LiveSplit local server")
    except:
        s = None
        print("Failed to connect to the LiveSplit local server")

def start_recording():
    global s
    
    if s is None:
        print("Reconnecting...") 
        connect()
        return
    try:
        s.send(b"getsplitindex\r\n")
        split_index = s.recv(128).decode().strip("\n")
        # That if statement needs some improvements
        if split_index >= "0":
            obs.obs_frontend_recording_start()
            print("Recording started") 
    except BlockingIOError:
        # Don't stop OBS
        pass
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("Reseting socket connection") 
        s = None

# A update function every tick
def script_tick(seconds):
    is_recording = obs.obs_frontend_recording_active()
    if not is_recording:
        start_recording()

def script_load(settings):
    connect()

def script_unload():
    global s
    if s:
        print("Closing socket connection")
        s.close()
        s = None