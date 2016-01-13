# -*- coding: utf-8 -*-

import sys, os, json

tgm = 'http://121.254.173.77:1555/templategeneration/templator/'
dm = 'http://121.254.173.77:2357/agdistis/run'
#tgm = 'http://121.254.173.77:2360/ko/tgm/stub/service'
#dm = 'http://121.254.173.77:2361/ko/dm/stub/service'
qgm = 'http://121.254.173.77:38401/queries'
kb = 'http://dbpedia.org/sparql'


input_string = "{"
#input_string += "'string': '어떤 강이 서울을 흐르는가?', "
#input_string += "'string': 'Which rivers flow through Seoul?', "
input_string += "'string': 'Who is the president of the United States?', "
input_string += "'language': 'en', "
#input_string += "'language': 'en', "
input_string += "'conf': {'tgm': ['" + tgm + "'], 'dm': ['" + dm + "'], 'qgm': ['" + qgm + "'], 'kb': ['" + kb + "'], 'answer_num': '5'}"
input_string += "}"

print input_string
input_string = '"' + input_string.replace("'", "\\\"") + '"'
print input_string

#print json.loads(input_string)

os.system('python controller_terminal.py ' + input_string)
