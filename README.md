# Toca
Automatic Testing


## 命令行
```
# toca help
usage: toca ACTION [-c toca.toml]

ACTION should be:
    ls           列出所有 API
    run          运行所有 API
    help, -h, --help    打印帮助

optional arguments:
    -c toca.toml  指定配置文件, 默认为当前路径下的 toca.toml
```

## 配置文件示例
```

[env]
class_id  = "123456"
school_id = "123456"

# 静态参数可以出现在所有地方
# 动态参数只允许出现在 uri/headers/params 中

[liteApp]
scheme = "http"
port = 4000
host = "localhost"
    [liteApp.headers]
    content-type = "application/json"
    [liteApp.Duration]
        [liteApp.Duration.CreateDuration]
        method = "post"
        uri    = "/liteapp/duration"
            [liteApp.Duration.CreateDuration.headers]
            content-type = "application/json"
            [liteApp.Duration.CreateDuration.params]
            begin_time = "2019-01-01"
            end_time   = "2019-06-01"
            class_id   = "{{class_id}}"
            school_id  = "{{school_id}}"
        [liteApp.Duration.GetDuration]
        method = "get"
        uri    = "/liteapp/duration/{$ liteApp.Duration.CreateDuration.response.data.uid $}"
        [liteApp.Duration.ListDuration]
        method = "get"
        uri    = "/liteapp/duration/list"
    
    [liteApp.Duty]
        [liteApp.Duty.CreateDuty]
        method = "post"
        uri = "/liteapp/duty/"
            [liteApp.Duty.CreateDuty.headers]
            content-type = "application/json"
            [liteApp.Duty.CreateDuty.params]
            duration_id = "{$ liteApp.Duration.CreateDuration.response.data.uid $}"
            duties      = "{$ _functions.loadJsonFromFile('duties.json') $}"
        [liteApp.Duty.GetDuty]
        method = "get"
        uri    = "/liteapp/duty/{$ liteApp.Duty.CreateDuty.response.data.uid $}"
    
    [liteApp.Section]
        [liteApp.Section.ListSection]
        method = "get"
        uri    = "/liteapp/school/{{school_id}}/sections/"

        

```