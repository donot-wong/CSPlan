## Docker基础环境
### If you don't have a docker installed, you'll need to install docker 
curl -s https://get.docker.com/ | sh 

### Use pip to install docker-compose 
pip install docker-compose  

### Entry vulnerability directory 
cd /path/to/vuln/ 

### Compile (optional) 
docker-compose build 

### Run 
docker-compose up -d 

## Docker镜像环境
### Mysql(7.x)
docker pull hub.c.163.com/library/mysql:latest

### RabbitMQ
docker pull hub.c.163.com/library/rabbitmq:management

### Python
docker pull hub.c.163.com/library/python:latest

docker build -t donotscan .
```
FROM hub.c.163.com/library/python:laste

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]
```
docker-compose up -d