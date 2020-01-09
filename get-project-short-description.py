import requests
import sys
from lxml import html
url=sys.argv[1]
response=requests.get(url)
tree=html.fromstring(response.content)
title=tree.xpath('//span[@itemprop="about"]/text()')
strings=title[0].split()
result=''
for string in strings:
    result+=string+' '
result=result[:-1]
print(result)
