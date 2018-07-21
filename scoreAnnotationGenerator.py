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
# TODO: Read SVG
# TODO: Get list of centers
# TODO: Sort by rows and bsearch
# TODO: Group by strips
# TODO: Sort by columns and bsearch
# TODO: Group by measures
# TODO: Group by beats
