import psutil
import time
import os
import sys
from colorama import Fore, Style, init

# --- CONFIGURATION ---
# The threshold specifically for the ROBLOX PROCESS (in KB/s)
# Since this isolates Roblox, 130 KB/s is a very clean signal.
# Depending on how sensitive you want this to be, change the threshold in order to be more lenient or strict with detecting receiving spikes.
TRIGGER_THRESHOLD_KB = 130.0
MAX_CONFIDENCE_KB = 3000.0 

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_roblox_pid():
    """Finds the specific Process ID for RobloxPlayerBeta.exe"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'RobloxPlayerBeta' in proc.info['name']:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def main():
    init(autoreset=True)
    cls()
    print(f"{Fore.CYAN}[*] Map scanner loaded")
    print(f"{Fore.CYAN}[*] Target: RobloxPlayerBeta.exe")
    print(f"{Fore.CYAN}[*] Upd: Process I/O Counters (Ignores Discord/Spotify/Chrome)")
    print(f"{Fore.WHITE}------------------------------------------------")

    pid = None
    
    
    while pid is None:
        print(f"\r{Fore.YELLOW}[?] Searching for Roblox process...", end="")
        pid = find_roblox_pid()
        time.sleep(1)
    
    print(f"\n{Fore.GREEN}[+] LOCKED ON. PID: {pid}")
    print(f"{Fore.GREEN}[+] Monitoring internal data throughput...")
    
    try:
        proc = psutil.Process(pid)
        

        last_io = proc.io_counters()
        last_total_bytes = last_io.read_bytes + last_io.write_bytes + last_io.other_bytes
        last_time = time.time()

        while True:
            if not psutil.pid_exists(pid):
                print(f"{Fore.RED}[!] Roblox closed. Exiting.")
                break

            current_time = time.time()
            time_delta = current_time - last_time
            
            # check every 0.1 seconds
            if time_delta >= 0.1:
                try:
                    
                    current_io = proc.io_counters()
                    current_total_bytes = current_io.read_bytes + current_io.write_bytes + current_io.other_bytes
                    
                    
                    diff = current_total_bytes - last_total_bytes
                    
                    
                    speed_bps = diff / time_delta
                    speed_kbps = speed_bps / 1024

                    
                    if speed_kbps > TRIGGER_THRESHOLD_KB:
                        
                        
                        confidence = ((speed_kbps - TRIGGER_THRESHOLD_KB) / (MAX_CONFIDENCE_KB - TRIGGER_THRESHOLD_KB)) * 100
                        if confidence > 100: confidence = 100.0
                        if confidence < 1: confidence = 1.0

                        
                        color = Fore.YELLOW
                        msg = "DATA ACTIVITY"
                        
                        if confidence > 50:
                            color = Fore.MAGENTA
                            msg = "HEAVY LOAD"
                        
                        if confidence > 85:
                            color = Fore.RED
                            msg = "MAP SPAWN"

                        print(f"{color}[!] ROBLOX I/O: {int(speed_kbps)} KB/s | Conf: {confidence:.1f}% | {msg}")

                    
                    last_total_bytes = current_total_bytes
                    last_time = current_time

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"{Fore.RED}[!] Lost access to process.")
                    break
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] Detached.")

if __name__ == "__main__":
    main()
