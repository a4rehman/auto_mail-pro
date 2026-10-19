"""
Connect to the Streamlit Cloud websocket endpoint to see whether the app
runtime actually starts (app awake) or the connection is refused (asleep).

Run:  python scripts/check_live_ws.py
"""
import asyncio
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import websockets

APPS = [
    "ai-cold-outreach-system.streamlit.app",
    "automail-pro.streamlit.app",
]

# Minimal Streamlit protobuf BackMsg: rerun_script. We only need the socket to
# accept and send the initial ForwardMsg; we don't need a full handshake.
RERUN_SCRIPT = bytes.fromhex(
    "0a"  # field 1 (rerun_script), wire type 2 (LEN) -> actually tag 0x0a = field1 LEN
)


async def probe(host):
    url = f"wss://{host}/_stcore/stream"
    try:
        async with websockets.connect(
            url,
            subprotocols=["streamlit"],
            open_timeout=25,
            close_timeout=5,
            max_size=None,
            origin=f"https://{host}",
        ) as ws:
            print(f"  connected -> {url}")
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=20)
                size = len(msg) if isinstance(msg, (bytes, bytearray)) else len(str(msg))
                print(f"  first frame received: {size} bytes (runtime is serving)")
                return True
            except asyncio.TimeoutError:
                print("  connected but no frame within 20s")
                return True
            except Exception as exc:
                print("  recv error:", type(exc).__name__, exc)
                return True
    except Exception as exc:
        print(f"  connect failed: {type(exc).__name__}: {exc}")
        return False


async def main():
    print("=" * 72)
    for host in APPS:
        print("APP:", host)
        await probe(host)
    print("=" * 72)


asyncio.run(main())
