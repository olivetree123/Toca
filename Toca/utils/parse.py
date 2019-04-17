import re


def get_dynamic_args(value):
    # 获取动态参数 {$ liteApp.Duration.CreateDuration.response.uid $}
    res = re.search("(\{\$[\w._ \-/\(\)\'\"]+\$\})", value)
    if not res:
        return []
    result = [r.strip() for r in res.groups()]
    return result

def replace_dynamic_arg(content, dynamic_name, value):
    return re.sub(re.escape(dynamic_name), value, content)

# def replace_dynamic_args(content):
#     dy_names = get_dynamic_args(content)
#     for dy_name in dy_names:
#         dy_value = root.get_dynamic_value(dy_name)
#         if isinstance(dy_value, (str, bytes)):
#             content  = replace_dynamic_arg(content, dy_name, dy_value)
#         else:
#             content = dy_value
#     return content