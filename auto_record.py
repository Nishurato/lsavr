import obspython as obs #type: ignore
import socket
import psutil

s = None
game_executable = "hl2.exe"
timer_interval_ms = 200

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

def timer_state_check():
    global s
    
    if s is None:
        print("Reconnecting...") 
        connect()
        return
    try:
        s.send(b"getcurrenttimerphase\r\n")
        return s.recv(128).decode().strip("\n")
    except BlockingIOError:
        # Don't stop OBS
        pass
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("Reseting socket connection") 
        s = None

def start_recording():
    timer_phase = timer_state_check()
    if timer_phase == "Running":
            obs.obs_frontend_recording_start()
            print("Recording started") 

# Check game running state
def game_state_check(game_exec_local):
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['name'] == game_exec_local:
            return True
    return False

# A update function every tick
def check_recording_state():
    is_recording = obs.obs_frontend_recording_active()
    is_game_active = game_state_check(game_executable)

    if not is_recording and is_game_active:
        start_recording()
    elif is_recording and not is_game_active:
        obs.obs_frontend_recording_stop()

def script_load(settings):
    connect()
    # We need save PC resources
    obs.timer_add(check_recording_state, timer_interval_ms)  

def script_unload():
    global s
    if s:
        print("Closing socket connection")
        s.close()
        s = None