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
- [ ] 2019/01/30 完成Chrome插件及数据处理模块设计开发  
- [ ] 2019/02/30 完成任务调度模块设计开发  
- [ ] 2019/03/30 完成扫描平台及策略模块开发  


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


### DNSLOG平台
[https://github.com/BugScanTeam/DNSLog.git](https://github.com/BugScanTeam/DNSLog.git)

### 参考
sqlmap
awvs
xsstrike
腾讯扫描器实践
...