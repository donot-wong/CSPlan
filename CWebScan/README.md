# CWebScan
CScan是一个半自动化扫描器，需要配合人工进行漏洞扫描，扫描器以乙方安全人员的视角进行设计和开发，
扫描器的目标是配合安全人员的能力对目标进行漏洞检测，实现目标漏洞检测准确率100%


### 方案设计
- [ ] 基础数据采集模块 - Chrome插件  
- [ ] 数据处理模块 - 数据预处理及存储  
- [ ] 任务调度模块 - 扫描及其他任务调度  
- [ ] 扫描平台模块 - 只做扫描平台，不做扫描策略  
- [ ] 扫描策略模块 - 安全人员的主要战场，插件化扫描策略配置  


### 技术要点
Chrome Extension
Javascript
Python
RabitMQ
Mysql
...

### 时间轴
- [x] 2019/12/30 完成技术方案定型  
- [x] 2019/01/30 完成Chrome插件及数据处理模块设计开发  
- [x] 2019/02/28 完成任务调度模块设计开发  
- [ ] 2019/03/31 完成扫描平台及策略模块开发  
- [ ] 2019/04/15 完成文档及论文撰写


### 参数解析方案
1. chrometype的优先级是最高的，一般chrome识别出的formData不管其真实请求的ContentType是何种类型，其真实内容是都是x-www-form-urlencoded，因此在进行参数解析时，优先解析chrometype为formData的，然后使用json解析body，所有成功解析的均识别为x-www-form-urlencoded类型处理。
2. ContentType不能作为唯一解析标准，对于chrometype为raw类型的内容，先根据contentType进行处理，处理不成功的使用sqlmap中的jsonlike/xmllike等进行相似处理，最后处理不成功的纪录日志
3. 对于二进制数据，暂时不做处理

ContentType统计数据如下：
在共74286条数据中：

|ContentType 	|				  数量    |  占比 |
| ----------    |  ---------------------  | ---- 
|application/x-www-form-urlencoded | 66956 |  90.01% 
|application/json   				|  5368 | 7.22% 
|text/plain 						|  1449 |  1.95% 
|multipart/form-data                | 28 |    0.03%  
|Other							  |   1934 |   2.60% 

### 消息队列
不采用其他任务分发框架，通过RabbitMQ消息队列实现数据的分发，采用生产者-消费者模型，实现通过多个不同队列模型实现数据的扭转

CMonitor->CWebServer->数据处理队列->数据清洗->扫描任务分发队列->不同扫描类型任务队列->插件化扫描器->扫描结果队列->扫描结果处理队列
通过是否进入不同的扫描队列控制扫描类型


### 数据清洗
如何定义不需要扫描数据包？
1. 重复的请求包
2. 响应数据为空，根据响应头进行判断
3. 响应不正常请求（404、403/5xx等状态码）， 根据响应头，并实际进行请求进行二次判断
4. 不能进行重复的请求包
5. 不需要进行扫描的请求包

去重策略(多级去重key策略，以不存在为首要检索条件，即每次查表我希望是不存在的，如果存在再进行下一级去重key)：
去重的目的是要确定这个请求在已经获取的数据中存在 or 不存在，这是个二分类问题，因此只要我确定
含有不可忽略参数：

一级去重key：
```
md5(method+scheme+netloc+path)
```
二级去重key（目标是希望参数名不同）:
```
if method == 'get':
md5(get param key list) # 剔除诸如入\_p \_t \_csrf等可忽略参数
else method == 'post':
md5(post parm key list) # 剔除诸如入\_p \_t \_csrf等可忽略参数
```
三级去重key（响应包contenttype不同）：
```
resp.headers
content-type
```
四级去重key（响应包长度差别大于20%）
```
content-length 响应包长度 差别大于20%
```
五级去重key{未实现}:
```
if method == 'get':
md5(query) # 数字->{id}
elif method == 'post':
md5(body)
```
剔除可忽略参数后没参数的（只有路径）：类似于/index.php/article/1/ index/article/{hashstr}
采用的是seay之前的一种算法， 被我修改了一下
[实用科普：爬虫技术浅析 编写爬虫应注意的点](http://www.91ri.org/11469.html)
原算法主要是通过对url结构进行转换后hash，也就是拥有同样结构的url被认为是重复的url
这样去重任然存在误差，因此我在使用这种方法时结合了响应包长度。当响应包长度差别在大于40%时即认为该url是非重复的。



### 任务分发
数据库保存两份数据，一份清洗前数据，一份清洗后数据，数据清洗的目的是解决重复、无效等不需要进行扫描的数据包，任务分发依赖的数据为清洗后数据  
1. 每个有效Host，应接入端口、Server扫描（PortScan/ServerScan） - 信息扫描
2. 每个有效路径，应接入文件扫描、目录扫描（FileScan/FolderScan）- 信息扫描
3. 每个存在有效参数请求包，应接入Web漏洞扫描（SqliScan/XssScan/RceScan等） - Web漏洞扫描


### 扫描模块
扫描模块需要对每个参数进行扫描，发包较多，扫描模块该怎么设计发包？用协程吗？
协程该怎么写？不用协程需要用大量分支判断，用协程怎么写判断逻辑？


### 数据转换
scantask.vulntype:
{
	'sqli': 1,
	'rce': 2,
	'xss': 3
}

scantask.status:
{
	'running': 0,
	'completed': 1,
	'error': 2
}



### DNSLOG平台
[https://github.com/BugScanTeam/DNSLog](https://github.com/BugScanTeam/DNSLog)  
[https://github.com/donot-wong/dnslog](https://github.com/donot-wong/dnslog)


### 参考
sqlmap
awvs
xsstrike
腾讯扫描器实践
...
