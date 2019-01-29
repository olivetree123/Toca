import re
import requests

from utils.log import loginfo
from entity.service import Api


class MolyRequest(object):
    def __init__(self, api:Api):
        self.api = api
        self.url = str(api.url)
        self.kwargs = {"headers":api.headers, "timeout":5}

    # 填充 url 中的参数
    def fill_get_args(self):
        if not self.api.method.upper() == "GET":
            return
        args = re.findall("<(\w+)>", self.url)
        for arg in args:
            value = str(self.api.params.pop(arg))
            self.url, _ = re.subn("<"+arg+">", value, self.url)
        self.url, params = self.url.split("?") if "?" in self.url else (self.url, "")
        params = params.split("&")
        for key, value in self.api.params.items():
            params.append(key+"="+str(value))
        params = "&".join([param for param in params if param])
        self.url = "?".join([self.url, params])
        print("Finally url = ", self.url)

    # 填充 post 参数
    def fill_post_args(self):
        if not self.api.method.upper() == "POST":
            return
        if self.api.headers:
            for key, value in self.api.headers.items():
                if key.upper() == "CONTENT-TYPE":
                    if value.lower() == "application/json":
                        self.kwargs["json"] = self.api.params
        if not (self.kwargs.get("json") or self.kwargs.get("data")):
            self.kwargs["data"] = self.api.params            
    
    def fill_file(self):
        if not self.kwargs.get("data"):
            return
        for key, value in self.kwargs["data"].items():
            if not value.startswith("file::"):
                continue
            path = value[6:]
            f = None
            if path.lower().startswith("http://"):
                f = self.downfile(path)
            else:
                f = open(path, "rb")
            files = {"file":f}
            self.kwargs["files"] = files
        
    def downfile(self, path):
        try:
            r = requests.get(path)
        except Exception as e:
            loginfo("下载文件失败", extra={"url": path, "Exception": e})
            return None
        if r.status_code != requests.codes.ok:
            loginfo("下载文件失败", extra={"url": path, "status_code": r.status_code, "message":r.text})
            return None
        return r.content

    def request(self):
        self.fill_get_args()
        self.fill_post_args()
        self.fill_file()
        # print("kwargs = ", self.kwargs)
        try:
            r = requests.request(self.api.method, self.url, **self.kwargs)
        except Exception as e:
            loginfo("获取数据失败", extra={"url": self.url, "Exception": e})
            return None
        if r.status_code != requests.codes.ok:
            loginfo("获取数据失败", extra={"url": self.url, "status_code": r.status_code, "message":r.text})
            return None
        data = r.json()
        return data


# def request(api:Api):
#     url = str(api.url)
#     # 找出 url 中的参数
#     args = re.findall("<(\w+)>", url)
#     for arg in args:
#         value = str(api.params.get(arg))
#         url = re.subn("<"+arg+">", value, url)[0]
#     # print("method = ", api.method, "url = ", url, "data = ", api.params, "headers = ", api.headers)
#     try:
#         r = requests.request(api.method, url, json=api.params, headers=api.headers, timeout=5)
#     except Exception as e:
#         loginfo("获取数据失败", extra={"url": url, "Exception": e})
#         return None
#     if r.status_code != requests.codes.ok:
#         loginfo("获取数据失败", extra={"url": url, "status_code": r.status_code, "message":r.text})
#         return None
#     data = r.json()
#     return data
