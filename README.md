# Lighthouse API Client

The client is tightly tied to the Lighthouse RESTful API RAML specification, which can be found [here](http://ftp.opengear.com/download/api/lighthouse/).

## Authentication

The **Lighthouse API Client** expects the following environment variables:

- **(required)** `OGLH_API_USER` a valid Lighthouse user
- **(required)** `OGLH_API_PASS` a valid Lighthouse user's password
- **(required)** `OGLH_API_URL` the Lighthouse API URL without `/api/v3.4`

They can be combined with optional parameters at instantiation:

```python
api = LighthouseApiClient(url = "https://192.168.0.10",
                          username = "root",
                          password = "myP@ssw0rd")
```

## Conventions

All the methods follow the convention that a call to an URL like:

```
GET /system/global_enrollment_token HTTP/1.0
```

would be performed through the client as:

```python
>>> from oglhclient import LighthouseApiClient
>>> api = LighthouseApiClient()
>>> client = api.get_client()
>>> client.system.global_enrollment_token.get()
```

Basically, all `/` are replaced by `.` followed by an action as specified below.

#### GET: `find()`
Used when asking for a specific object.

Example:

```
GET /nodes/smartgroups/myGrouId HTTP/1.0
```

becomes:

```python
smartgroup = client.nodes.smartgroups.find(id='myGrouId')
```

or

```python
smartgroup = client.nodes.smartgroups.find('myGrouId')
```

In case of a child object like in `/nodes/{id}/tags/{tag_value_id}`, with a possible call like:

```
GET /nodes/nodes-13/tags/London HTTP/1.0
```

the Python call should be:


```python
tag = client.nodes.tags.find(id='London', parent_id='node-13')
```

It is also possible to use:

```python
tag = client.nodes.tags.find(id='London', node_id='node-13')
```

Always paying attention to the simple plural formatting removal:

- **nodes**: *node*
- **properties**: *property*

### GET: `list()`
Used when asking for a list of objects.

Example:

```
GET /nodes/smartgroups HTTP/1.0
```

becomes:

```python
smartgroups = client.nodes.smartgroups.list()
```

Parameters may apply, like `page`, `per_page`, and so on:

```python
smartgroups = client.nodes.smartgroups.list(page=1, per_page=5)
```

### GET: `get()`
Only used when the two previous do not apply, like:

```
GET /system/webui_session_timeout HTTP/1.0
```

which becomes:

```python
timeout = client.system.webui_session_timeout.get()
```

### POST: `create()`
As the name suggests, it is used to create objects, for instance:

```
POST /tags/node_tags HTTP/1.0
Content-Type: application/json
{"nodeTag": {"name": "Location", "values": [{"value": "USA.NewYork"}, {"value": "UK.London"}]}}
```

could be performed as:

```python
data = {
  "nodeTag": {
    "name": "Location",
    "values": [
      {
          "value": "USA.NewYork"
      },
      {
          "value": "UK.London"
      }
    ]
  }
}
result = client.tags.node_tags.create(data)
```

### PUT: `update()`
It is used to update a given object.

Example:

```
PUT /tags/node_tags/nodes_tags-1 HTTP/1.0
Content-Type: application/json
{"nodeTag": {"name": "Location", "values": [{"id": "tags_node_tags_values_5", "value": "UK.Cambridge"}, {"value": France.Paris"}]}}
```

is performed as:

```python
data = {
  "nodeTag": {
    "name": "Location",
    "values": [
      {
          "id": "tags_node_tags_values_5",
          "value": "UK.Cambridge"
      },
      {
          "value": "France.Paris"
      }
    ]
  }
}
RESULT = client.tags.node_tags.update(id='tags_node_tags-1', data=data)
```

### DELETE: `delete()`
It is used to delete an object by its `id`, for instance:

```
DELETE /tags/node_tags/nodes_tags-1 HTTP/1.0
```

is performed as:

```python
result = client.tags.node_tags.delete(id='tags_node_tags-1')
```
