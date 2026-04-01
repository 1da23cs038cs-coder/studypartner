"""
start.py — Study Partner launcher for Windows
Usage: python start.py
"""
import subprocess, sys, os, time, signal, ctypes

def kill_port_8501():
    """Force kill whatever is on port 8501."""
    try:
        result = subprocess.check_output(
            'netstat -ano | findstr ":8501" | findstr "LISTENING"',
            shell=True, text=True, stderr=subprocess.DEVNULL
        )
        for line in result.strip().splitlines():
            parts = line.strip().split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and pid != "0":
                    subprocess.call(f"taskkill /F /T /PID {pid}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
                    print(f"  Killed PID {pid} on port 8501")
    except Exception:
        pass

def main():
    # First make sure port is free before starting
    kill_port_8501()
    time.sleep(0.5)

    print("\n  ========================================")
    print("   Study Partner")
    print("  ========================================")
    print("  URL: http://localhost:8501")
    print("  Press Ctrl+C ONCE to stop")
    print("  ========================================\n")

    # Use CREATE_NEW_PROCESS_GROUP so we can kill the whole group
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.address=localhost",
         "--server.port=8501",
         "--server.headless=true",
         "--browser.gatherUsageStats=false",
         "--global.developmentMode=false"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        creationflags=flags,
    )

    def stop(*_):
        print("\n\n  Stopping Study Partner...")
        try:
            # Kill entire process group
            subprocess.call(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
        time.sleep(1)
        kill_port_8501()
        print("  Done — port 8501 is free.\n")
        os._exit(0)   # hard exit, no exceptions

    # Register Ctrl+C handler
    signal.signal(signal.SIGINT,  stop)
    signal.signal(signal.SIGTERM, stop)
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, stop)

    try:
        proc.wait()
    except Exception:
        stop()

if __name__ == "__main__":
    main()