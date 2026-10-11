import atexit
import os
import hou
from .server import HoudiniMCPServer

def start_server():
    if not hasattr(hou.session, "houdinimcp_server") or hou.session.houdinimcp_server is None:
        hou.session.houdinimcp_server = HoudiniMCPServer()
        hou.session.houdinimcp_server.start()
    else:
        existing = hou.session.houdinimcp_server
        if not existing.running:
            existing.start()
        else:
            print("Houdini MCP Server is already running.")

def stop_server():
    if hasattr(hou.session, "houdinimcp_server") and hou.session.houdinimcp_server:
        hou.session.houdinimcp_server.stop()
        hou.session.houdinimcp_server = None

def initialize_plugin():
    if not hasattr(hou.session, "houdinimcp_use_assetlib"):
        hou.session.houdinimcp_use_assetlib = False
    start_server()
    atexit.register(stop_server)

# Auto-start only in an interactive GUI session. Never under headless hython:
# batch tools (e.g. a render farm's scene analysis) launch hython, where an
# unsolicited server thread breaks the run — and the UI-bound bridge cannot
# work headless anyway. Opt out in the GUI with HOUDINIMCP_AUTOSTART=0; start
# it on demand from the HoudiniMCP shelf when headless access is needed.
if hou.isUIAvailable() and os.environ.get("HOUDINIMCP_AUTOSTART", "1") != "0":
    initialize_plugin()
