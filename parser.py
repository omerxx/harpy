import json

def parse_errors(data):
    counter = 0
    for item in data['log']['entries']:
        if item['response']['status'] != 200:
            counter += 1

    print 'Found {} errors'.format(counter)

with open('har.json') as data_file:    
    parse_errors(json.load(data_file))

