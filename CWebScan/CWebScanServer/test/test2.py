from urllib import parse

test = "{'/delete': ['0'], '/file-change': ['0'], '/global/asset-version': ['3'], '/latest': ['1463'], '/logout': ['108'], '/new': ['331'], '/polls/248': ['0'], '/recover': ['0'], '/site/banner': ['0'], '/site/read-only': ['0'], '/topic/248': ['0'], '/whos-online': ['44022'], '__seq': ['11239']}"
print(parse.quote(test))