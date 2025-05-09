import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_tag_values(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    tag_dict = defaultdict(str)

    for child in root:
        tag_dict[child.tag] = child.text.strip() if child.text else ''

    return tag_dict
