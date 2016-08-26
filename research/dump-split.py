import os
import xml.etree.ElementTree as ET

chunk = 10000
file = '~/records.xml'

doc = ET.iterparse(file, events=('start',))
pattern = os.path.splitext(file)[0]
count = 0
buffer = []

for event, elem in doc:

    if elem.tag == 'record':

        buffer.append(ET.tostring(elem))
        count += 1

        if count % 1000 == 0:
            print(count)

        if count % chunk == 0:
            subfile = '%s-%d.xml' % (pattern, count / chunk)

            with open(subfile, 'w') as f:
                f.write('<collection>\n\n')
                for str in buffer:
                    f.write(str)
                f.write('</collection>')

            del buffer[:]

            print('processed: %s' % subfile)
