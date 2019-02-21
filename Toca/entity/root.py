import re
import os
import toml
import json
from jinja2 import Template

from toca.entity.api import Api
from toca.entity.group import Group
from toca.entity.service import Service
from toca.utils.errors import HTTPMethodError
from toca.utils.functions import loadJsonFromFile, getRandomName, getRandomInt
from toca.utils.parse import replace_dynamic_arg, get_dynamic_args


class Toca(object):
    def __init__(self, file_path=None):
        self.service_list:List[Service] = []
        if file_path and os.path.isfile(file_path):
            self.load_from_file(file_path)
    
    def add_service(self, service:Service):
        if not isinstance(service, Service):
            raise TypeError("Invalid type, type of Service is expected, but {} found".format(type(service)))
        self.service_list.append(service)
    
    def get_dynamic_name(self, dynamic_name):
        r = re.search("\{\$\s*([\w._\(\)\'\"]+)\s*\$\}", dynamic_name)
        if not r:
            return None
        return r.groups()[0]
    
    def get_dynamic_value(self, dynamic_name):
        dynamic_name = self.get_dynamic_name(dynamic_name)
        if not dynamic_name:
            raise ValueError("Invalid dynamic_name {}".format(dynamic_name))
        service_name, dynamic_name = dynamic_name.split(".", 1)
        if service_name == "_functions":
            return eval(dynamic_name)
        for service in self.service_list:
            if not service.name == service_name:
                continue
            return service.get_dynamic_value(dynamic_name)
        
    def replace_dynamic_args(self, content):
        dy_names = get_dynamic_args(content)
        for dy_name in dy_names:
            dy_value = self.get_dynamic_value(dy_name)
            if isinstance(dy_value, (str, bytes)):
                content  = replace_dynamic_arg(content, dy_name, dy_value)
            else:
                content = dy_value
        return content
        
    def load_from_file(self, file_path):
        env = toml.load(file_path).get("env", {})
        with open(file_path, "r") as f:
            content = f.read()
        content = Template(content).render(**env)
        result = toml.loads(content)
        for service_name in result:
            if service_name == "env":
                continue
            service_dict = result[service_name]
            service = Service(
                service_name, 
                service_dict.pop("host"), 
                service_dict.pop("port"), 
                service_dict.pop("headers", None), 
                service_dict.pop("scheme", "http")
            )
            self.add_service(service)
            for group_name in service_dict:
                group_dict = service_dict[group_name]
                if not isinstance(group_dict, dict):
                    continue
                group = Group(group_name)
                service.add_group(group)
                for api_name in group_dict:
                    api_dict = group_dict[api_name]
                    uri      = api_dict.get("uri")
                    method   = api_dict.get("method")
                    api      = Api(api_name, method, uri)
                    group.add_api(api)
                    api.add_attr("params", api_dict.get("params", {}))
                    api.add_attr("headers", api_dict.get("headers", service.headers))

    def run(self, service_name=None, api_name=None):
        for service in self.service_list:
            if service_name and service.name != service_name:
                continue
            for group in service.group_list:
                for api in group.api_list:
                    if api_name and api.name != api_name:
                        continue
                    try:
                        uri = self.replace_dynamic_args(api.uri)
                        for key, value in api.params.items():
                            api.params[key] = self.replace_dynamic_args(api.params[key])
                    except AttributeError as e:
                        print(api.name, "ERROR = ", e)
                        continue
                    req = service.winney.add_url(method=api.method, uri=uri, function_name=api.name)
                    r = None
                    if   api.method.lower() == "get":
                        r = req(
                            data=api.params,
                            headers=api.headers
                        )
                    elif api.method.lower() in ("post", "put", "patch"):
                        r = req(
                            data=api.params if not api.is_json() else None, 
                            json=api.params if api.is_json() else None, 
                            headers=api.headers
                        )
                    elif api.method.lower() in ("head", "options", "delete"):
                        r = req(
                            headers=api.headers
                        )
                    else:
                        raise MethodError("Invalid request method: ", api.method)
                    if r.ok():
                        api.response = r.get_json() if api.is_json() else r.get_bytes()
                    # else:
                    #     print(r.status_code, r.content)
                    api.status_code = r.status_code
                    print(api.name, api.status_code)
                    if api.is_json():
                        print(json.dumps(api.response, indent=4, sort_keys=True))
                    else:
                        print(api.response)

    def ls(self, service_name=None):
        for service in self.service_list:
            if service_name and service.name != service_name:
                continue
            for group in service.group_list:
                for api in group.api_list:
                    print(service.name, api.name, "\t", api.method, api.uri)