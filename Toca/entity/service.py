from winney import Winney

from toca.entity.group import Group


class Service(object):
    def __init__(self, name, host, port, headers=None, scheme="http"):
        self.name = name
        self.host = host
        self.port = port
        self.scheme = scheme
        self.headers = headers
        self.group_list:List[Group] = []
        self.winney = Winney(host=self.host, port=self.port, headers=self.headers)
    
    def is_json(self):
        if not self.headers:
            return False
        for key, value in self.headers.items():
            if key.lower() == "content-type" and value.lower() == "application/json":
                return True
        return False
    
    def add_group(self, group:Group):
        if not isinstance(group, Group):
            raise Exception("Invalid type, Group is expected, but {} found".format(type(group)))
        self.group_list.append(group)
    
    def get_dynamic_value(self, dynamic_name):
        group_name, dynamic_name = dynamic_name.split(".", 1)
        for group in self.group_list:
            if not group.name == group_name:
                continue
            return group.get_dynamic_value(dynamic_name)
