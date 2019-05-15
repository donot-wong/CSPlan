from urllib import parse
import json
test = json.loads(parse.unquote('%7B%22Accept-Language%22%3A%20%22zh-CN%2Czh%3Bq%3D0.9%22%2C%20%22Accept-Encoding%22%3A%20%22gzip%2C%20deflate%22%2C%20%22Referer%22%3A%20%22http%3A//123.206.98.106%3A8082/index.html%22%2C%20%22Accept%22%3A%20%22text/html%2Capplication/xhtml%2Bxml%2Capplication/xml%3Bq%3D0.9%2Cimage/webp%2Cimage/apng%2C%2A/%2A%3Bq%3D0.8%2Capplication/signed-exchange%3Bv%3Db3%22%2C%20%22User-Agent%22%3A%20%22Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/74.0.3729.131%20Safari/537.36%22%2C%20%22Upgrade-Insecure-Requests%22%3A%20%221%22%7D'))
# print(type(test))
for i in test:
	print(i)