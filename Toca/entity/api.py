
class Api(object):
    def __init__(self, name, method, uri):
        self.uri = uri
        self.name = name
        self.method   = method
        self.params   = {}
        self.headers  = None
        self.response = None
        self.status_code = 0
    
    def is_json(self):
        if not self.headers:
            return False
        for key, value in self.headers.items():
            if key.lower() == "content-type" and value and value.lower() == "application/json":
                return True
        return False
    
    def check_name(self, name):
        if name.lower() in ("method", "content-type", "headers", "params", "uri", "version", "files"):
            return True
        return False

    def add_attr(self, name, value):
        status = self.check_name(name)
        if not status:
            # print("Failed to add attr to api, invalid name = {}".format(name))
            raise NameError("Invalid name = {}".format(name))
        setattr(self, name, value)
    
    def get_dynamic_value(self, dynamic_name):
        obj = self
        attr, dynamic_name = dynamic_name.split(".", 1)
        obj = getattr(self, attr)
        if not obj:
            raise AttributeError("Attribute {} not found".format(attr))
        while "." in dynamic_name:
            attr, dynamic_name = dynamic_name.split(".", 1)
            obj = obj.get(attr)
            if not obj:
                raise AttributeError("Attribute {} not found".format(attr))
        return obj.get(dynamic_name)