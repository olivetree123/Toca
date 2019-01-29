import re

from entity.goml import Goml, Value
from entity.stack import Stack


class Lex(object):
    def __init__(self, path):
        self.name:str = ""
        self.value:Value = None
        self.depth:int = 1
        self.content = ""
        self.stack:Stack = Stack()
        self.root_obj:Goml = Goml("root", 0)
        self.current_obj:Goml = self.root_obj
        # 初始对象压栈
        self.stack.push(self.current_obj)
        # 双引号数量
        # 为奇数时表示当前处在双引号当中；
        # 为偶数时表示当前处在双引号之外
        self.quots_count = 0

        with open(path, encoding="utf8") as f:
            self.content = f.read()
        self.remove_comment()
        
        self.PATTERNS = {
            # 新对象即将出现，但是现在还不需要做任何动作，过滤掉即可
            "[\[]"    : "PREPARE",
            # 创建新对象，如果新对象的 depth 比当前对象大，则当前对象需要压栈；
            # 如果小或等于，则需要从栈中弹出一些对象，直到栈顶的对象的 depth 与新对象的 depth 相等
            "[\]]"    : "NEW_OBJECT",
            # 换行，depth 清0。如果 key/value 不为空，需要添加到对象中
            "\n"   : "NEW_LINE",
            # 遇到一个空格，不做任何处理
            " {1,3}"    : "PASS",
            # 遇到双引号，直接往后遍历，不用正则匹配，知道找到下一个双引号
            '"'    : "QUOTATION",
            # 遇到两个双引号，说明是个空字符串
            '""'   : "DOUBLE_QUOTATION",
            # 遇到单引号，应该直接跳到下一个引号的位置，取出中间的值
            # 算了，暂时不处理单引号，作为字符串的一部分
            # "'"    : "JUMP",
            # tab, depth 增加1
            "\t"   : "DEPTH_INCR",
            "="    : "ASSIGN",
            # 4个空格，depth 增加1
            " {4}" : "DEPTH_INCR",
            # 匹配 name
            # "[\w:]+": "NAME",
            # 匹配数字
            "[\d.]+": "NUMBER",
            # 匹配 字符串，字符串中不可以有双引号和换行符
            '[^"\s=\\n\[\]]+' : "VALUE",
        }
    
    def remove_comment(self):
        self.content = re.sub("#.*", "", self.content)
    
    def check_name(self, name):
        r = re.match("[\w-]+", name)
        if not r:
            return False
        value = r.group()
        if name == value:
            return True
        return False
    
    def in_quots(self):
        # 判断当前位置是否位于两个双引号之间
        if self.quots_count % 2 == 1:
            return True
        return False

    def match(self, word, action=False):
        # 匹配时，应做的动作。
        # 结束符有：换行符、[、]
        for pattern, action in self.PATTERNS.items():
            r = re.match(pattern, word)
            if not r:
                continue
            value = r.group()
            # 正则匹配的结果需要和 word 相同
            if not value == word:
                continue
            return action
        return None

    def act(self, action:str, word:str):
        if action == "QUOTATION":
            self.quots_count += 1
            if not self.in_quots():
                if not (self.name and self.value):
                    raise("Error2", "self.name = {}, self.value = {}".format(self.name, self.value))
                self.value.value = word
                self.value.tp = str
            return

        if action == "PREPARE":
            pass
        
        elif action == "DOUBLE_QUOTATION":
            self.value.value = ""
            self.value.tp = str

        elif action == "NEW_LINE":
            self.depth = 1
            if self.name and self.value:
                if getattr(self.current_obj, self.name) and self.current_obj._category != "List":
                    raise Exception("Name exists, name = {}".format(self.name))
                self.current_obj.add_attr(self.name, self.value)
            self.name = None
            self.value = None

        elif action == "DEPTH_INCR":
            if not (self.name or self.value):
                self.depth += 1

        elif action == "ASSIGN":
            self.name = self.value.value if self.value else None
            if not self.name:
                raise("name 为空，不能赋值")
            if not self.check_name(self.name):
                raise Exception("name 格式不合法, name = {}".format(self.name))
            self.value = Value()

        elif action == "NEW_OBJECT":
            self.stack.pop_until(self.depth)
            self.current_obj = self.stack.top()
            category = ""
            self.name = self.value.value
            if ":" in self.name:
                category, self.name = self.name.split(":")
            new_obj = Goml(self.name, self.depth, category)
            # print("NEW_OBJECT = ", new_obj._title, 
            #         "depth = ", self.depth, 
            #         "category = ", category, 
            #         "CURRENT = ", self.current_obj._title, self.current_obj._depth
            # )
            if self.current_obj:
                self.current_obj.add_child(new_obj)
                self.stack.push(new_obj)
            self.current_obj = new_obj
            self.name = None
            self.value = None

        elif action == "NUMBER":
            if self.value and self.value.value:
                raise("value 有值了，不能再赋值. self.value = {}, value = {}".format(self.value.value, word))
            self.value = Value(word, int)

        elif action == "VALUE":
            if self.value and self.value.value:
                raise Exception("value 有值了，不能再赋值. self.value = {}, value = {}".format(self.value.value, word))
            self.value = Value(word, str)
        
        elif action == "PASS":
            pass
        
    def get_value(self, names):
        name_list = names.split(".")
        obj = self.root_obj
        for name in name_list:
            obj = getattr(obj, name)
            if not obj:
                return
        if isinstance(obj, Value):
            return obj.value
        return
    
    # 将变量替换为真实的值
    def replace_variable(self, obj):
        for child_name in obj.children:
            value = getattr(obj, child_name)
            if isinstance(value, Goml):
                self.replace_variable(value)
            elif isinstance(value, Value):
                if not value.value.startswith("$."):
                    continue
                v = self.get_value(value.value[2:])
                value.value = v
                # print("++++ replace, name = ", child_name, "value = ", v)
            else:
                raise Exception("Invalid type, expect Value, but {} found".format(type(value)))

    
    def run(self):
        word, action = "", ""
        for c in self.content:
            if self.in_quots():
                action = self.match(c)
                if action == "QUOTATION":
                    print("++++ QUOTATION, word = ", word)
                    self.act(action, word)
                    word = ""
                else:
                    word += c
            else:
                word += c 
                status = self.match(word)
                if not status:
                    action = self.match(word[:-1], True)
                    self.act(action, word[:-1])
                    word = c
        print("======================")
        self.root_obj.print()
        self.replace_variable(self.root_obj)
        # print("======================")
        # print(self.root_obj.ischool.name)
        # print(self.root_obj.ischool.url)
        # print(self.root_obj.ischool.chat.name)
        # print(self.root_obj.ischool.chat.CreateChat.headers.Authorization)
        