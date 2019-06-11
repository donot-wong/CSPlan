from multipart import *
from io import BytesIO

def on_field(field):
    print("Parsed field named: %s:%s" % (str(field.field_name, encoding='utf-8'),str(field.value, encoding='utf-8')))
    # print(field)

def on_file(file):
	print("Parsed file named: %s:%s" % (file.field_name,file.file_name))
	# print(file)

def test_parse_form():
    f = FormParser(
        'multipart/form-data',
        on_field,
        on_file,
        boundary='----WebKitFormBoundarywVX1k8jAxqB8RIVo'
    )
    data = b'------WebKitFormBoundarywVX1k8jAxqB8RIVo\r\nContent-Disposition: form-data; name="bdstoken"\r\n\r\n6a622c8ac38ccfeb94ece5c94a4bb3fb\r\n------WebKitFormBoundarywVX1k8jAxqB8RIVo\r\nContent-Disposition: form-data; name="psign"\r\n\r\n36b9e9bb94e7ac9b7238\r\n------WebKitFormBoundarywVX1k8jAxqB8RIVo\r\nContent-Disposition: form-data; name="staticpage"\r\n\r\nhttps://www.baidu.com/p/jump.html\r\n------WebKitFormBoundarywVX1k8jAxqB8RIVo\r\nContent-Disposition: form-data; name="file"; filename="donot.png"\r\nContent-Type: image/png\r\n\r\ndsadas\r\n------WebKitFormBoundarywVX1k8jAxqB8RIVo--\r\n'
    f.write(data)
    f.finalize()


if __name__ == '__main__':
	test_parse_form()