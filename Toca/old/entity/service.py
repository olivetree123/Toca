# 最上面是 Service，最下面是 API，中间是 Group

from urllib.parse import urljoin

from entity.goml import Goml

class Api(object):
    def __init__(self, name, method):
        self.name = name
        self.method = method
    
    def __getattr__(self, attribute):
        return None

    def check_name(self, name):
        if name.lower() in ("method", "content-type", "headers", "params", "uri", "version"):
            return True
        return False

    def add_attr(self, name, value):
        status = self.check_name(name)
        if not status:
            print("Failed to add attr to api, invalid name = {}".format(name))
            return
        if not isinstance(value, Goml):
            setattr(self, name, value)
        else:
            setattr(self, name, value.to_json())

    def get_attr_from_goml(self, api_conf_obj:Goml):
        for attr in api_conf_obj.children:
            val = getattr(api_conf_obj, attr)
            if not val:
                continue
            self.add_attr(attr, val)
        

class Group(object):
    def __init__(self, name, uri=""):
        self.name = name
        self.uri = uri
        self.api_list:List[Api] = []
    
    def check_name(self, name):
        if name in ("uri", ):
            return True
        return False
    
    def add_api(self, api:Api):
        self.api_list.append(api)
    
    def add_attr(self, name, value):
        status = self.check_name(name)
        if not status:
            print("Invalid name = {}".format(name))
            return
        if not isinstance(value, Goml):
            setattr(self, name, value)
        else:
            raise Exception("Invalid value type, expect str , but {} found".format(type(value)))
    
    def get_attr_from_goml(self, group_conf_obj:Goml):
        for attr in group_conf_obj.children:
            val = getattr(group_conf_obj, attr)
            if not val:
                continue
            if not isinstance(val, Goml):
                self.add_attr(attr, val)
                continue
            api = Api(val.name, (val.method or val._category))
            self.add_api(api)
            api.get_attr_from_goml(val)
            


class Service(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.group_list:List[Group] = []
    
    def check_name(self, name):
        if name in ("url", ):
            return True
        return False

    def add_attr(self, name, value):
        if self.name.upper() != "ENV" and not self.check_name(name):
            raise Exception("Invalid name = {}".format(name))
        if not isinstance(value, Goml):
            setattr(self, name, value)
        else:
            raise Exception("Invalid value type, expect str , but {} found".format(type(value)))
    
    def add_group(self, group:Group):
        self.group_list.append(group)
    
    def get_attr_from_goml(self, conf_obj:Goml):
        for attr in conf_obj.children:
            val = getattr(conf_obj, attr)
            if not val:
                continue
            if not isinstance(val, Goml):
                self.add_attr(attr, val)
                continue
            group = Group(val.name)
            self.add_group(group)
            group.get_attr_from_goml(val)

    def api_list(self):
        result = []
        for group in self.group_list:
            for api in group.api_list:
                uri = api.uri or group.uri
                api.url = urljoin(str(self.url), str(uri))
                for key, value in api.params.items():
                    api.params[key] = value.tp(value.value)
                if api.headers:
                    for key, value in api.headers.items():
                        api.headers[key] = value.tp(value.value)
                result.append(api)
        return result
