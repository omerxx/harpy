import json

def parse_errors(data):
    counter = 0
    for item in data['log']['entries']:
        if item['response']['status'] != 200:
            counter += 1

    # TODO: check if there are timestamps to sample 30 - 40 - 50 - 60 seconds from load

    return counter


def audio_detection(data):
    # TODO: Iterate over network requests / responses search for audio files
    pass


if __name__ == "__main__":
    with open('har.json') as data_file:    
        parse_errors(json.load(data_file))
