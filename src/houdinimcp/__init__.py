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

# Auto-load on import (skipped for headless — managed by headless_server.py)
if not os.environ.get("HOUDINIMCP_HEADLESS"):
    initialize_plugin()
