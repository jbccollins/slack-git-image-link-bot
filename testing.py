import requests
def get_image_definitions():
    image_definitions = {}
    r = requests.get('https://raw.githubusercontent.com/jbccollins/images/master/images.text', auth=('EMAIL', 'GITHUB_PASSWORD'))
    for line in r.iter_lines():
        if line:
            split = line.split()
            image_definitions[split[0]] = split[1]
    return image_definitions

print get_image_definitions()