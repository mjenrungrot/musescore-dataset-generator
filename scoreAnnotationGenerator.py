import music21

c = music21.converter.parse('Final_Project.xml')
pages = music21.layout.divideByPages(c)

data = []
for page in pages.pages:
  strips = page.systems
  
  cumulative_notehead_strips = []
  notehead_measures = {}
  notehead_beats = {}
  nNotes_strip = 0
  for strip in strips:
    staves = strip.staves
    for staff in staves:
      measures = staff.getElementsByClass('Measure')
      for measure in measures:
        measure_num = measure.number - page.measureStart + 1
        if measure_num not in notehead_measures: notehead_measures[measure_num] = 0
        if measure_num not in notehead_beats: notehead_beats[measure_num] = {}
        if len(measure.voices) == 0:
          notes = measure.notes
          for note in notes: 
            note_beat = note.beat
            nNotes_strip += len(note.pitches)
            notehead_measures[measure_num] += len(note.pitches)
            if note_beat not in notehead_beats[measure_num]: notehead_beats[measure_num][note_beat] = 0
            notehead_beats[measure_num][note_beat] += len(note.pitches) 
        else:
          voices = measure.voices
          for voice in voices:
            notes = voice.notes
            for note in notes:
              note_beat = note.beat
              nNotes_strip += len(note.pitches)
              notehead_measures[measure_num] += len(note.pitches)
              if note_beat not in notehead_beats[measure_num]: notehead_beats[measure_num][note_beat] = 0
              notehead_beats[measure_num][note_beat] += len(note.pitches) 
    cumulative_notehead_strips.append(nNotes_strip)
  
  data.append({
    'cumulative_notehead_strips': cumulative_notehead_strips,
    'notehead_measures': notehead_measures,
    'notehead_beats': notehead_beats,
  })

def convertNoteBeatsToCumulative(note_beat_dict, n_beats):
  keys = sorted(note_beat_dict.keys())
  cum_note_beats = []
  cum_sum = 0
  for key in keys:
    cum_sum += note_beat_dict[key]
    if key == int(key):
      cum_note_beats.append((int(key), cum_sum))
  return cum_note_beats

import pprint
pprint.pprint(data)

# SHEET
from svgpathtools import svg2paths

paths, attributes = svg2paths('Final_Project-1.svg')
pack = zip(paths, attributes)
filtered_pack = filter(lambda x: x[1]['class'] == 'Note', pack)
paths, attributes = zip(*filtered_pack)
bboxes = list(map(lambda path: path.bbox(), paths))
centers = list(map(lambda box: ((box[0]+box[1])/2, (box[2]+box[3])/2), bboxes))

def splitCentersByStrips(centers, splitter_array):
  # Sort by rows and bsearch
  row_sorted_centers = sorted(centers, key=lambda x: x[1]) 
  splitter_arrays = data[0]['cumulative_notehead_strips']

  # Split notehead into strips
  strips = {}
  current_offset = 0
  counter = 0
  for i in range(1,len(splitter_arrays)+1):
    strip = []
    for note_center in row_sorted_centers[current_offset:]:
      strip.append(note_center)
      counter += 1
      if counter == splitter_arrays[i-1]: break

    strips[i] = strip
    current_offset = counter

  return strips

strips = splitCentersByStrips(centers, data[0]['cumulative_notehead_strips'])

# Visualize strips
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.scatter(*zip(*strips[1]))
# plt.scatter(*zip(*strips[2]), color='red')
# plt.scatter(*zip(*strips[3]), color='green')
# plt.scatter(*zip(*strips[4]), color='yellow')
# plt.scatter(*zip(*strips[5]), color='black')
plt.gca().invert_yaxis()
plt.savefig('output.png')

# TODO: Sort by columns and bsearch
# TODO: Group by measures
# TODO: Group by beats
