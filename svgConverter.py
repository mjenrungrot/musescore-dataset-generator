from svgpathtools import svg2paths

paths, attributes = svg2paths('test-1.svg')
pack = zip(paths, attributes)
filtered_pack = filter(lambda x: x[1]['class'] == 'Note', pack)
paths, attributes = zip(*filtered_pack)
bboxes = list(map(lambda path: path.bbox(), paths))