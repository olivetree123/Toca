
class Value(object):
    def __init__(self, value:str=None, tp:str=""):
        self.type = tp
        self.value = value

    def __str__(self):
        return self.value


class Goml(object):
    def __init__(self, title:str, depth:int, category:str=""):
        # depth 根据缩进决定
        self._depth = depth
        self._title = title
        self._category = category
        self._name = title
        # self.children:List[Goml] = None
        self.children = [] # 子属性的名称集合，属性值可能是 str 或 Goml

    def __getattr__(self, attribute):
        return None

    def add_attr(self, attr:str, value:Value):
        setattr(self, attr, value)
        self.children.append(attr)
    
    def add_child(self, obj):
        if obj._category == "List":
            print("title = ", obj._title)
            r = getattr(self, obj._title)
            if not r:
                setattr(self, obj._title, [obj])
            else:
                r.append(obj)
            if obj._title not in self.children:
                self.children.append(obj._title)
        else:
            self.add_attr(obj._title, obj)
        
    def to_json(self):
        r = {}
        for child_name in self.children:
            r[child_name] = getattr(self, child_name)
        return r
    
    def print(self):
        if not self.children:
            return
        print("obj = ", self._title, "children = ", self.children)
        for child_name in self.children:
            r = getattr(self, child_name)
            if isinstance(r, Goml):
                # print(child_name, r)
                r.print()
            elif isinstance(r, Value):
                print(child_name, r.value)