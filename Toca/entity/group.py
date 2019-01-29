from toca.entity.api import Api


class Group(object):
    def __init__(self, name):
        self.name = name
        self.api_list:List[Api] = []
    
    def add_api(self, api:Api):
        if not isinstance(api, Api):
            raise Exception("Invalid type, Api is expected, but {} found".format(type(api)))
        self.api_list.append(api)
    
    def get_dynamic_value(self, dynamic_name):
        api_name, dynamic_name = dynamic_name.split(".", 1)
        for api in self.api_list:
            if not api.name == api_name:
                continue
            return api.get_dynamic_value(dynamic_name)
