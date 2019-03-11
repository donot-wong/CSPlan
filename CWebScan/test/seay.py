from urllib.parse import urlparse
import hashlib
hash_size = 199999
def main(url):
	o = urlparse(url)
	# self.ret.scheme = o.scheme
	# self.ret.netloc = o.netloc
	# self.ret.path = o.path
	# self.ret.query = o.query
	path = o.path
	if len(path.split('/')[-1].split('.')) > 1:
		tail = path.split('/')[-1].split('.')[-1]
	elif len(path.split('/')) == 1:
		tail = path
	else:
		tail = '1'

	tail = tail.lower()
	path_length = len(path.split('/')) - 1
	path_value = 0
	path_list = path.split('/')[:-1] + [tail]

	for i in range(path_length + 1):
		if path_length -i == 0:
			path_value_end = str(path_value) + str(hashlib.md5(path_list[path_length - i].encode('utf-8')))
		else:
			path_value += len(path_list[path_length - i]) * (10**(i+1)) 
	netloc_value = hashlib.md5(o.netloc.encode('utf-8')).hexdigest()
	url_value = hashlib.md5((str(path_value)+str(netloc_value)).encode('utf-8')).hexdigest()
	return url_value


def test():
	m = hashlib.md5('a'.encode('utf-8')).hexdigest()
	print(m)

if __name__ == '__main__':
	print(main('http://auto.sohu.com/7/0903/70/column213117075.shtml'))
	print(main('http://auto.sohu.com/7/0903/95/column212969565.shtml'))
	print(main('http://auto.sohu.com/id/1/'))
	print(main('http://auto.sohu.com/id/2/'))

# 66262
# 69955
# 52087
# 83454
# 33395