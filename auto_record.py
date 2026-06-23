import obspython as obs #type: ignore
import socket
import psutil

s = None
game_executable = "hl2.exe"
game_is_active = False

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
        s.send(b"getcurrenttimerphase\r\n")
        timer_phase = s.recv(128).decode().strip("\n")
        # Nice!
        if timer_phase == "Running":
            obs.obs_frontend_recording_start()
            print("Recording started") 
    except BlockingIOError:
        # Don't stop OBS
        pass
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("Reseting socket connection") 
        s = None

# Check game running state
def game_state_check(game_exec_local):
    is_active = False

    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['name'] == game_exec_local:
            is_active = True
            break
        is_active = False
    
    return is_active

# A update function every tick
def script_tick(seconds):
    is_recording = obs.obs_frontend_recording_active()
    is_game_active = game_state_check(game_executable)

    if not is_recording and is_game_active:
        start_recording()
    elif is_recording and not is_game_active:
        obs.obs_frontend_recording_stop()

def script_load(settings):
    connect()

def script_unload():
    global s
    if s:
        print("Closing socket connection")
        s.close()
        s = None