
class Stack(object):
    def __init__(self):
        self.content:Goml = []
    
    def push(self, data):
        self.content.append(data)
    
    def pop(self):
        return self.content.pop()
    
    def pop_until(self, depth):
        # 弹出所有 depth 大于等于指定 depth 的对象
        while self.top()._depth >= depth:
            self.pop()
        # for i in range(len(self.content)-1, 0, -1):
        #     if self.content[i]._depth < depth:
        #         continue
        #     self.pop()
    
    def top(self):
        return self.content[-1]

