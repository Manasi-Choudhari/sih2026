import sys
import os
import signal
import time
import traceback
import contextlib
import faulthandler
import uvicorn
import uvicorn.server

faulthandler.enable()

# Completely neutralize Uvicorn's signal interception on Windows
uvicorn.server.HANDLED_SIGNALS = ()

@contextlib.contextmanager
def noop_capture_signals(self):
    yield

uvicorn.server.Server.capture_signals = noop_capture_signals
if hasattr(uvicorn, "Server"):
    uvicorn.Server.capture_signals = noop_capture_signals

def main():
    for sig_name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        if hasattr(signal, sig_name):
            try:
                signal.signal(getattr(signal, sig_name), signal.SIG_IGN)
            except Exception:
                pass

    while True:
        try:
            print(">>> [VAJRA Backend] Starting Uvicorn server on http://127.0.0.1:8000 ...", flush=True)
            config = uvicorn.Config(
                "backend.main:app",
                host="127.0.0.1",
                port=8000,
                log_level="info",
                access_log=True,
                loop="asyncio",
            )
            server = uvicorn.Server(config)
            server.install_signal_handlers = lambda: None
            server.run()
            print(">>> [VAJRA Backend] server.run() exited. Auto-restarting in 1s...", flush=True)
            time.sleep(1)
        except Exception as e:
            print(f">>> [VAJRA Backend] Exception caught: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            time.sleep(1)
        except BaseException as be:
            print(f">>> [VAJRA Backend] BaseException caught: {type(be)} {be}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            time.sleep(1)

if __name__ == "__main__":
    main()
