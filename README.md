# Lighthouse API client

The client is tightly tied to the RESTfull API [RAML specification](http://ftp.opengear.com/download/api/lighthouse/og-rest-api-specification-v1.raml), which is very well exposed [here](http://ftp.opengear.com/download/api/lighthouse/og-rest-api-specification-v1.html).

## Authentication

The **Lighthouse API Client** expects to find the following environment variables:

- **(required)** `OGLH_API_USER` a valid Lighthouse user
- **(required)** `OGLH_API_PASS` a valid Lighthouse user's password
- **(required)** `OGLH_API_URL` the Lighthouse API url without `/api/v1`

## Conventions

All the methods follow the convention specified as follows. A call for an *url* like:

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

Basically, all `/` must be replaced by `.` followed by an action:

#### GET: `find()`
Used when asking for a specific object

Example:

```
GET /nodes/smartgroups/myGrouId HTTP/1.0
```

Becomes:

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

The python call should be:


```python
tag = client.nodes.tags.find(id='myTagId', parent_id='myNodeId')
```

Also possible to make:

```python
tag = client.nodes.tags.find(id='myTagId', node_id='myNodeId')
```

Always paying attention to the simple plural formatting removal:

- **nodes**: *node*
- **properties**: *property*

### GET: `list()`
Used when asking for a list of objects

Example:

```
GET /nodes/smartgroups HTTP/1.0
```

Becomes:

```python
smartgroups = client.nodes.smartgroups.list()
```

parameters may apply like `page`, `per_page`, and so on:

```python
smartgroups = client.nodes.smartgroups.list(page=1,per_page=5)
```

### GET: `get()`
Only used when the two previous do not apply, like:

```
GET /system/webui_session_timeout HTTP/1.0
```

Becomes:

```python
timeout = client.system.webui_session_timeout.get()
```


### POST: `create()`
As the name suggests, it is used to create objects, for instance:

```
POST /tags/node_tags HTTP/1.0
Content-Type: application/json

{"node_tag": {"name": "Location","values": [{"value": "USA.NewYork"},{"value": "UK.London"}]}}
```

could be performed as:

```python
result = client.tags.node_tags.create(data={"username":"root","password":"default"})
```

### PUT: `update()`
It is used to update a given object, like:

```
PUT /tags/node_tags/nodes_tags-1 HTTP/1.0
Content-Type: application/json

{"node_tag": {"name": "Location","values": [{"id": "tags_node_tags_values_90","value": "USA.NewYork"}]}}
```

could be performed as:

```python
data = {
  "node_tag": {
    "name": "Location",
    "values": [
      {
        "id": "tags_node_tags_values_90",
        "value": "USA.NewYork"
      }
    ]
  }
}
result = client.tags.node_tags.update(tag_value_id='nodes_tags-1', data=data)
```

### DELETE: `delete()`

It is used for deleting an object by its `id`, for instance:

```
DELETE /tags/node_tags/nodes_tags-1 HTTP/1.0
```

could be performed as:

```python
result = client.tags.node_tags.delete(tag_value_id='nodes_tags-1')
```
