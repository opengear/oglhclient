"""
Opengear Lighthouse API Client

Usage:
>>> from oglhclient import LighthouseApiClient
>>> api = LighthouseApiClient()
>>> client = api.get_client()

Then, to execute GET /system/webui_session_timeout HTTP/1.0
>>> timeout = client.system.webui_session_timeout.get()

Check documentation at https://github.com/opengear/oglhclient
"""

from .oglhclient import LighthouseApiClient
