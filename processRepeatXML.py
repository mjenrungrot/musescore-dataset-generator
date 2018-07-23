import glob
import os 
import tqdm
import lxml.etree as le
from parallel_utils import parallel_process

xml_paths = glob.glob('xml/*.xml')

for xml_path in tqdm.tqdm(xml_paths):
  doc = le.parse(xml_path)
  
  tagsToRemove = []

  # Filter tags
  tagsToRemove.extend(doc.xpath('.//repeat'))
  tagsToRemove.extend(doc.xpath('.//bar-style[text()="heavy-light"]'))
  tagsToRemove.extend(doc.xpath('.//ending'))
  tagsToRemove.extend(doc.xpath('.//coda'))
  tagsToRemove.extend(doc.xpath('.//segno'))

  if len(tagsToRemove) > 0:
    for tag in tagsToRemove:
      parent = tag.getparent()
      parent.remove(tag)
  
    print(xml_path)
    
  doc.write(xml_path, pretty_print=True)
