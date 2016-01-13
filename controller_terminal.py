# -*- coding: utf-8 -*-

import sys, re
from bottle import route, run, template, request, response, post
import urllib, urllib2, json
from time import sleep

# Configuration variables
address = {}

# Global variables
input_string = None
input_json = None
answers = []
answer_num = None

m_dir = 'm_data'

log = ''

def main():
  get_inputs()
  set_conf()
  get_answers()
  bye()



def get_inputs():
  global input_string
  global input_json

  input_string = sys.argv[1]
  input_json = json.loads(input_string)



def set_conf():
  global address
  global answer_num

  try:
    address['tgm'] = input_json['conf']['tgm']
    address['dm'] = input_json['conf']['dm']
    address['qgm'] = input_json['conf']['qgm']
    address['kb'] = input_json['conf']['kb']
    answer_num = int(input_json['conf']['answer_num'])

    input_json.pop('conf')
    
  except KeyError:  
    i_file = open(m_dir + 'conf.tsv', 'r')
    line = i_file.readline()
    while line:
      line = line[0:-1]
      s_line = re.split('\s', line)
        
      if s_line[0] == 'tgm_address':
        address['tgm'] = s_line[1:]
      elif s_line[0] == 'dm_address':
        address['dm'] = s_line[1:]
      elif s_line[0] == 'qgm_address':
        address['qgm'] = s_line[1:]
      elif s_line[0] == 'kb_address':
        address['kb'] = s_line[1:]
      elif s_line[0] == 'answer_num':
        answer_num = int(s_line[1])

      line = i_file.readline()
    i_file.close()

    # Fault tolerance
    try:
      address['tgm']
    except KeyError:
      fault('Error: TGM addresses are not configured')
    try:
      address['dm']
    except KeyError:
      fault('Error: DM addresses are not configured')
    try:
      address['qgm']
    except KeyError:
      fault('Error: QGM addresses are not configured')
    try:
      address['kb']
    except KeyError:
      fault('Error: KB addresses are not configured')
      
    if answer_num == None:
      fault('Error: answer_num is not configured')



def get_answers():  
  write_log('Controller input: ' + input_string)
  
  question = input_json['string']

  # ==================================
  # TGM
  # ==================================
  
  tgm_input_json = input_json
  tgm_input_string = json.dumps(tgm_input_json)
  tgm_outputs = []

  write_log('TGM input: ' + tgm_input_string)
  for tgm in address['tgm']:
    tgm_output_string = 'null'
    
    try:
      tgm_output_string = send_postrequest(tgm, tgm_input_string)
      write_log('TGM output: ' + tgm_output_string)
  
    # Fault checking
    except Exception as error:
      write_log(str(error))
      fault('Error: TGM error')

    # Fault checking
    if tgm_output_string == 'null':
      fault('Error: TGM returns null')

    # Fault checking
    try:
      tgm_output_string.decode('utf-8')
    except:
      fault('Error: TGM output is not UTF-8')

    # Fault checking
    try:
      if tgm == 'http://121.254.173.77:1555/templategeneration/templator/':
        tgm_outputs.append(json.loads(tgm_output_string)[0])
      else:
        tgm_outputs.append(json.loads(tgm_output_string))
    except:
      fault('Error: TGM output is not JSON format')

  # ==================================
  # TGM output => DM inputs
  # ==================================
  dm_inputs = tgm_outputs
  for dm_input in dm_inputs:
    dm_input['question'] = json.loads(tgm_input_string)['string']

  # ==================================
  # DM
  # ==================================
  for dm_input in dm_inputs:
    dm_output_string = ''
    dm_outputs = []

    write_log('DM input: ' + json.dumps(dm_input))
    for dm in address['dm']:    
      try:
        if dm == 'http://121.254.173.77:2357/agdistis/run': # AGDISTIS only supports the GET method.
          dm_output_string = urllib.urlopen(dm + '?' + 'data=' + json.dumps(dm_input).replace('\\"','"').replace('|','_')).read()
        else:
          dm_output_string = send_postrequest(dm, json.dumps(dm_input))
        write_log('DM output: ' + dm_output_string)

      # Fault checking
      except Exception as error:
        write_log(str(error))
        fault('Error: DM error')

      # Fault checking
      if dm_output_string == 'null':
        fault('Error: DM returns null')

      # Fault checking
      try:
        dm_output_string.decode('utf-8')
      except:
        fault('Error: DM output is not UTF-8')

      # Fault checking
      try:
        dm_outputs.append(json.loads(dm_output_string))
      except:
        fault('Error: DM output is not JSON format')

    # ==================================
    # DM output => QGM inputs
    # ==================================
    qgm_inputs = []
    for dm_output in dm_outputs:
      qgm_inputs.append({'template':dm_input, 'disambiguation':dm_output['ned'][0]})
    
    # ==================================
    # QGM
    # ==================================
    for qgm_input in qgm_inputs:
      qgm_output_string = ''
      qgm_outputs = []

      write_log('QGM input: ' + json.dumps(qgm_input))
      for qgm in address['qgm']:
        try:
            qgm_output_string = send_postrequest(qgm, json.dumps(qgm_input))
            write_log('QGM output: ' + qgm_output_string)

        # Fault checking
        except Exception as error:
          write_log(str(error))
          fault('Error: QGM error')

        # Fault checking
        if qgm_output_string == 'null':
          fault('Error: QGM returns null')

        # Fault checking
        try:
          qgm_output_string.decode('utf-8')
        except:
          fault('Error: QGM output is not UTF-8')

        # Fault checking
        try:
          qgm_outputs += json.loads(qgm_output_string)
        except:
          fault('Error: QGM output is not JSON format')

      # ==================================
      # QGM output => AGM inputs
      # ==================================
      agm_inputs = qgm_outputs

      # ==================================
      # AGM
      # ==================================
      #arguments = {'default-graph-uri':'http://dbpedia.org', 'format':'application/sparql-results+json', 'timeout':'0', 'debug':'on', 'query':''}
      arguments = {'default-graph-uri':'', 'format':'application/sparql-results+json', 'timeout':'0', 'debug':'on', 'query':''}
      write_log('AGM input: ' + json.dumps(agm_inputs))
      for agm_input in agm_inputs:
        arguments['query'] = agm_input['query'].encode('utf-8')
        
        sleep(0.1)
        for kb_address in address['kb']:
          arguments['query'] = arguments['query'] + '\n'

          full_url = kb_address + '?' + urllib.urlencode(arguments)
          try:
            raw_answer = urllib.urlopen(full_url).read()
            curr_answers = json.loads(raw_answer)

            a_num = 0

            var = curr_answers['head']['vars'][0]
            for binding in curr_answers['results']['bindings'] :
              answers.append(binding[var]['value'])
              a_num += 1
              
              if len(answers) >= answer_num:
                write_log(str(answers))
                sys.exit(0)

            if a_num > 0:
              write_log('AGM output (of one query): ' + json.dumps(curr_answers))
            else:
              write_log('AGM output (of one query): no answer')
          except SystemExit:
            write_log('AGM output: the adquate answers are obtained')
            bye()
          except:
            write_log('AGM output (of one query): not valid query')
            pass



def send_getrequest(url):
  opener = urllib2.build_opener()
  request = urllib2.Request(url, headers={'Content-Type':'application/json'})
  return opener.open(request).read()
  
def send_postrequest(url, input_string):
  opener = urllib2.build_opener()
  request = urllib2.Request(url, data=input_string, headers={'Content-Type':'application/json'})
  return opener.open(request).read()

def write_log(l):
  global log

  log += l + '\n'

def fault(message):
  write_log('')
  write_log(message)
  bye()

def bye():  
  output = {'log': log, 'answers': answers}

  sys.stdout.write(json.dumps(output))
  sys.stdout.flush()
  sys.exit(0)
    
main()
