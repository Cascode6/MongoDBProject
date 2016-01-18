###taken directly from https://discussions.udacity.com/t/how-to-provide-sample-data-for-the-final-project/7118/13


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "buffalogrove.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()




with open(SAMPLE_FILE, 'wb') as output2:
    ##I am using python 3. 'w' does not allow bytes to be written, and 'wb' does not allow strings to be written.
    ##As this is not necessarily critical to project completion, I have ommitted the xml declaration for now.
    ##

    # Write every 10th top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % 10 == 0:
            output2.write(ET.tostring(element, encoding='utf-8'))

