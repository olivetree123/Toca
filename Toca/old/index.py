#coding:utf-8
import os
from entity.lex import Lex
from entity.goml import Goml
from entity.service import Api, Group, Service
from request import MolyRequest


if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "ischool.toml")
    # path = "/Users/gao/code/Moly/ischool.toml"
    print("path = ", path)
    conf = Lex(path)
    conf.run()
    print("services = ", conf.root_obj.children)
    services = []
    for child_name in conf.root_obj.children:
        if child_name.upper() == "ENV":
            continue
        service_conf_obj = getattr(conf.root_obj, child_name)
        service = Service(service_conf_obj.name or service_conf_obj._name, service_conf_obj.url)
        services.append(service)
        service.get_attr_from_goml(service_conf_obj)
    
    api_list = service.api_list()
    for api in api_list:
        # data = request(api)
        moly = MolyRequest(api)
        data = moly.request()
        print("response = ", data)


