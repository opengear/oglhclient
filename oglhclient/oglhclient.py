# -*- coding: utf-8 -*-
"""
Opengear Lighthouse API Client

It implements Lighthouse RESTful API RAML specification, which can be
found here: http://ftp.opengear.com/download/api/lighthouse/
"""

import json
import os
import re

from collections import namedtuple
from functools import partial
from urllib.parse import urlencode

import requests
import yaml


def ensure_auth(f):
    """
    Ensures the client has a valid session id (token).
    When a function is called and the client is not authenticated,
    it will try to authenticate and call the function again.
    """
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if 'error' in result._asdict() and 'Invalid session ID' in result.error[0].text:
            args[0]._do_auth()
            return f(*args, **kwargs)
        return result

    return wrapper


class LighthouseApiClient:
    """
    The basic API client, with methods for GET, POST, PUT, and DELETE.
    """

    def __init__(self, url="", username="", password="", version="3.4"):
        self.url = url if url else os.environ.get('OGLH_API_URL')
        self.username = username if username else os.environ.get('OGLH_API_USER')
        self.password = password if password else os.environ.get('OGLH_API_PASS')

        if not (self.url and self.username and self.password):
            raise RuntimeError("""
    Missing some of the required environment variables. Please refer
    to the documentation at https://github.com/opengear/oglhclient""")

        requests.packages.urllib3.disable_warnings()
        self.api_url = self.url + f"/api/v{version}"
        self.token = None
        self.pending_name_ids = {}
        self.s = requests.Session()
        self.version = version

        try:
            ramlfile = os.path.join(
                os.path.dirname(__file__),
                f"og-rest-api-specification-v{self.version.replace('.', '-')}.raml"
            )
            with open(ramlfile, "r", encoding="ascii") as stream:
                self.raml = yaml.load(
                    re.sub(r'\t', '  ', re.sub(r'\\\/', '/', re.sub(r':\"', ': \"', stream.read()))),
                    Loader=yaml.FullLoader
                )
        except Exception as e:
            print(e)
            print("Trying remote file...")
            lighthouse_url = "http://ftp.opengear.com/download/api/lighthouse"
            r = self.s.get(f"{lighthouse_url}/og-rest-api-specification-v{self.version.replace('.', '-')}.raml")
            self.raml = yaml.load(
                re.sub(r'\t', '  ', re.sub(r'\\\/', '/', re.sub(r':\"', ': \"', r.text))),
                Loader=yaml.FullLoader
            )

        if not isinstance(self.raml, dict):
            raise RuntimeError("""
    Lighthouse RESTful API specification couldn't be loaded, locally nor
    at http://ftp.opengear.com/download/api/lighthouse""")

        self.raml = self._fix_raml(self.raml)

    def _update_raml_nodes(self, raml, elem, path_parts, node):
        """
        Adds path parts to raml dictionaries.
        """
        if not path_parts:
            raml[elem] = node
        else:
            if elem not in raml:
                raml[elem] = {}
            raml[elem].update(
                self._update_raml_nodes(raml[elem], '/' + path_parts[0], path_parts[1:], node)
            )
        return raml

    def _fix_raml(self, raml):
        """
        Fixes some objects that are split like:
        /system
        /system/time

        instead of:
        /system
            /time

        It is helpful for parsing the RAML file.
        """
        top_paths = [p for p in raml.keys() if re.match(r'^\/', p)]
        for p in top_paths:
            path_parts = p.split('/')
            if len(path_parts) >= 3 and ('/' + path_parts[1]) in top_paths:
                raml = self._update_raml_nodes(raml, '/' + path_parts[1], path_parts[2:], raml[p])
                del raml[p]
            else:
                raml[p] = self._fix_raml(raml[p])
        return raml

    def _headers(self):
        headers = {'Content-type': 'application/json'}
        if self.token:
            headers.update({'Authorization': 'Token ' + self.token})
        return headers

    def _do_auth(self):
        data = {'username': self.username, 'password': self.password}
        body = self.post('/sessions', data=data)

        if 'error' in body._asdict():
            raise RuntimeError(body.error[0].text)

        self.token = body.session

        if not self.token:
            raise RuntimeError('Auth failed')
        self.s.headers = self._headers()

    def _get_api_url(self, path):
        return self.api_url + path

    def _parse_response(self, response):
        try:
            # return json.loads(response.text)
            return json.loads(
                response.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values())
            )
        except ValueError:
            return response.text

    def _get_url(self, path, **kwargs):
        return self._get_api_url(str.format(path, **kwargs))

    def _get_url_params(self, path, *args, **kwargs):
        for a in args:
            if type(a) is dict:
                kwargs.update(a)
        params = urlencode({
            k: v for k, v in kwargs.items()
                if not re.match(r'.*\{' + k + r'\}', path)
        })
        return self._get_url(path, **kwargs), params

    def _apply_ids(self, path, **kwargs):
        """
        Properly replaces names in case of kwargs with ids for objects and/or parents.
        """
        if len(kwargs) > 0 and not re.match(r'.*\{id\}$', path):
            child_name = re.sub(r'\{(.*)\}', r'\1', path.split('/')[-1])
            if 'id' in kwargs:
                kwargs[child_name] = kwargs['id']
                del kwargs['id']
            if re.match(r'.*\{id}', path):
                parent_name = re.sub(r's$','',re.sub(r'ies$','y',path.split('/')[1]))
                parent_id_str = parent_name + '_id'
                if 'parent_id' in kwargs:
                    kwargs['id'] = kwargs['parent_id']
                    del kwargs['parent_id']
                elif parent_id_str in kwargs:
                    kwargs['id'] = kwargs[parent_id_str]
                    del kwargs[parent_id_str]
        return kwargs

    @ensure_auth
    def get(self, path, *args, **kwargs):
        kwargs = self._apply_ids(path, **kwargs)
        url, params = self._get_url_params(path, *args, **kwargs)
        r = self.s.get(url, params=params, verify=False)
        return self._parse_response(r)

    @ensure_auth
    def find(self, path, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            id_name = re.sub(r'\{(.*)\}', r'\1', path.split('/')[-1])
            kwargs = { id_name: args[0] }
            args = []
        elif len(args) == 0:
            kwargs = self._apply_ids(path, **kwargs)

        url, params = self._get_url_params(path, *args, **kwargs)
        r = self.s.get(url, params=params, verify=False)
        return self._parse_response(r)

    @ensure_auth
    def post(self, path, data={}, **kwargs):
        kwargs = self._apply_ids(path, **kwargs)

        if 'data' in kwargs and data == {}:
            data = kwargs['data']
            del kwargs['data']
        url = self._get_url(path, **kwargs)
        r = self.s.post(url, data=json.dumps(data), verify=False)
        return self._parse_response(r)

    @ensure_auth
    def put(self, path, data, **kwargs):
        kwargs = self._apply_ids(path, **kwargs)
        if 'data' in kwargs and data == {}:
            data = kwargs['data']
            del kwargs['data']
        url = self._get_url(path, **kwargs)
        r = self.s.put(url, data=json.dumps(data), verify=False)
        return self._parse_response(r)

    @ensure_auth
    def delete(self, path, **kwargs):
        kwargs = self._apply_ids(path, **kwargs)
        r = self.s.delete(self._get_url(path, **kwargs), verify=False)
        return self._parse_response(r)

    def get_client(self):
        return self._get_client(self.raml, '')

    def _get_client(self, node, path):
        top_children = set([key.split('/')[1] for key in node.keys()
            if re.match(r'^\/', key) and len(key.split('/')) == 2])
        sub_children = set(['__'.join(key.split('/')[1:]) for key in node.keys()
            if re.match(r'^\/', key) and len(key.split('/')) > 2])
        middle_children = set([s.split('__')[0] for s in sub_children])
        actions = set([key for key in node.keys() if re.match(r'^[^\/]', key)])

        kwargs = { 'path': path }

        for k in actions:
            if k == 'get' and re.match(r'.*(I|i)d\}$', path):
                kwargs['find'] = partial(self.find, path)
            elif k == 'get' and (len([l for l in top_children if re.match(r'\{.+\}', l)]) > 0
                    or
                ('description' in node['get'] and
                    re.match(r'.*(A|a|(T|t)he)\ (l|L)ist\ of', node['get']['description']))):
                kwargs['list'] = partial(self.get, path)
            elif k == 'get':
                kwargs['get'] = partial(self.get, path)
            elif k == 'put':
                kwargs['update'] = partial(self.put, path)
            elif k == 'post':
                kwargs['create'] = partial(self.post, path)
            elif k == 'delete':
                kwargs['delete'] = partial(self.delete, path)
            else:
                kwargs[k] = node[k]

        for k in top_children:
            if re.match(r'\{.+\}', k):
                inner_props = self._get_client(node['/' + k], path + '/' + k)
                for l in inner_props._asdict():
                    kwargs[l] = inner_props._asdict()[l]
            else:
                kwargs[k] = self._get_client(node['/' + k], path + '/' + k)

        for k in list(middle_children):
            subargs = {}
            if re.match(r'\{.+\}', k):
                continue
            else:
                for s in [l for l in list(sub_children) if re.match(r'^' + k, l)]:
                    sub = re.sub(r'^' + k + '__', '', s)
                    subargs[sub] = self._get_client(node['/' + k + '/' + sub],
                        path + '/' + k + '/' + sub)
            SubClient = namedtuple('SubClient', ' '.join(subargs.keys()))
            kwargs[k] = SubClient(**subargs)

        SynClient = namedtuple('OgLhClient', ' '.join(kwargs.keys()))
        return SynClient(**kwargs)
