#!/usr/bin/python3

from oglhclient import LighthouseApiClient

def main():
    api = LighthouseApiClient(url = "https://192.168.34.249",
                              username = "root",
                              password = "default")

    client = api.get_client()

    # a few "GETs" as example...
    print(client.system.webui_session_timeout.get())

    print(client.nodes.tags.list(parent_id='nodes-1'))

    print(client.nodes.tags.find(id='nodes_tags-1', node_id='nodes-1'))

    print(client.search.nodes.get(searchparameters="config:status=Enrolled"))

    print(client.interfaces.find('lighthouse_configurations_system_net_conns-1'))


main()
