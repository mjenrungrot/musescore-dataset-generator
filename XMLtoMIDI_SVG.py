import glob
import os
import tqdm
import lxml.etree
from parallel_utils import parallel_process

# Set environment variable to prevent QXcbConnection: Could not connect to display problem
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

if not os.path.exists('svg'):
  os.mkdir('svg') 

if not os.path.exists('midi'):
  os.mkdir('midi') 

def f(xml_path):
  filename = os.path.splitext(os.path.basename(xml_path))[0]
  os.system("musescore {:} -r 300 -f -o midi/{:}.mid".format(xml_path, filename))
  os.system("musescore {:} -r 300 -f -o svg/{:}.svg".format(xml_path, filename))

xml_paths = glob.glob('xml/*.xml')
parallel_process(xml_paths, f)
