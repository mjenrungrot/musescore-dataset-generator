import music21
from svgpathtools import svg2paths
import pandas as pd
import glob
import os
import pretty_midi
import pdb
from parallel_utils import parallel_process

def get_annotation_data(xml_file):
  c = music21.converter.parse(xml_file)
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
          measure_num = measure.number

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

  cumulative_notehead_strips = []
  notehead_measures = {}
  notehead_beats = {}
  for x in data:
    cumulative_notehead_strips.extend(x['cumulative_notehead_strips'])
    keys = x['notehead_measures'].keys()
    for key in keys:
      notehead_measures[key] = x['notehead_measures'][key]
    keys = x['notehead_beats'].keys()
    for key in keys:
      notehead_beats[key] = x['notehead_beats'][key]

  return {
    'cumulative_notehead_strips': cumulative_notehead_strips,
    'notehead_measures': notehead_measures,
    'notehead_beats': notehead_beats,
  }

def get_centers(svg_file):
  paths, attributes = svg2paths(svg_file)
  pack = zip(paths, attributes)
  filtered_pack = list(filter(lambda x: x[1]['class'] == 'Note', pack))
  paths, attributes = zip(*filtered_pack)
  bboxes = list(map(lambda path: path.bbox(), paths))
  centers = list(map(lambda box: (round((box[0]+box[1])/2, 2), round((box[2]+box[3])/2, 2)), bboxes))
  return centers

def splitCentersByStrips(centers, splitter_array):
  # Sort by rows
  row_sorted_centers = sorted(centers, key=lambda x: x[1]) 

  # Split notehead into strips
  strips = {}
  current_offset = 0
  counter = 0
  for i in range(1,len(splitter_array)+1):
    strip = []
    for note_center in row_sorted_centers[current_offset:]:
      strip.append(note_center)
      counter += 1
      if counter == splitter_array[i-1]: break

    strips[i] = strip
    current_offset = counter
    if current_offset == len(centers):
      return strips, i

  assert False, "Should haven't been here"
    
def splitCentersByMeasures(centers, splitter_dict, offset_measure=0):
  # Sort by columns
  column_sorted_centers = sorted(centers, key=lambda x: x[0])

  keys = list(filter(lambda x: x >= offset_measure, sorted(splitter_dict.keys())))
  measures = {}
  current_offset = 0
  total_counter = 0
  counter = 0
  for key in keys:
    measure = []
    counter = 0
    for note_center in column_sorted_centers[current_offset:]:
      measure.append(note_center)
      counter += 1
      if counter == splitter_dict[key]: break
    
    measures[key] = measure
    current_offset += counter
    total_counter += counter
    
    if total_counter >= len(centers): 
      return measures, key

  assert False, "Should haven't been here"

def splitCentersByBeats(centers, splitter_dict):
  # Sort by columns
  column_sorted_centers = sorted(centers, key=lambda x: x[0])

  beats = {}
  current_offset = 0
  total_counter = 0
  counter = 0
  for key in sorted(splitter_dict.keys()):
    beat = []
    counter = 0
    for note_center in column_sorted_centers[current_offset:]:
      beat.append(note_center)
      counter += 1
      if counter == splitter_dict[key]: break
    
    if len(beat) > 0: beats[key] = beat
    current_offset += counter
    total_counter += counter
    
  assert total_counter == len(centers), "Number of notes in the measure doesn't match the expectation"

  return beats

def summarizeBeatInfo(note_centers_list):
  x_positions = list(map(lambda center: center[0], note_centers_list))
  return max(set(x_positions), key=x_positions.count)

def filterIntegerBeats(beat_locations_dict):
  for measure_key in beat_locations_dict.keys():
    for beat_key in list(beat_locations_dict[measure_key].keys()):
      if int(beat_key) != beat_key:
        del beat_locations_dict[measure_key][beat_key]
      else:
        beat_locations_dict[measure_key][int(beat_key)] = beat_locations_dict[measure_key].pop(beat_key)
  return beat_locations_dict

def process(score_name, xml_file, svg_filepaths, midi_filepath):
  xml_annotations = get_annotation_data(xml_file)
  # print(xml_file)
  # print(len(xml_annotations), len(svg_filepaths))
  # assert len(xml_annotations) == len(svg_filepaths), "Number of pages mismatches"

  df_score = pd.DataFrame(columns=['score', 'measure', 'beat', 'strip', 'page', 'hpixel'])
  df_audio = pd.DataFrame(columns=['measure', 'time'])

  offset_strips = 0
  offset_measure = 0
  for page_num in range(len(svg_filepaths)):
    centers = get_centers(svg_filepaths[page_num])
    strips, offset_strip = splitCentersByStrips(centers, xml_annotations['cumulative_notehead_strips'][offset_strips:])
    offset_strips += offset_strip

    # Split to measures
    measures = {}
    measure_strip_dict = {}
    for strip_num in strips.keys():
      tmp_measures, end_measure = splitCentersByMeasures(strips[strip_num], xml_annotations['notehead_measures'], offset_measure=offset_measure)
      offset_measure = end_measure + 1
      for key in tmp_measures.keys():
        measures[key] = tmp_measures[key]
        measure_strip_dict[key] = strip_num

    # Split to beats
    beat_notes = {}
    for key in measures.keys():
      beat_notes[key] = splitCentersByBeats(measures[key], xml_annotations['notehead_beats'][key])

    # Get the mode of x-position for each beat position
    beat_locations = {}
    for measure_key in measures.keys():
      beat_locations[measure_key] = {}
      for beat_key in beat_notes[measure_key].keys():
        beat_locations[measure_key][beat_key] = summarizeBeatInfo(beat_notes[measure_key][beat_key])

    # Filter for only integer-number beats
    beat_locations = filterIntegerBeats(beat_locations)
    
    # print(measures.keys())

    # Update dataframe
    for measure_key in measures.keys():
      for beat_key in beat_locations[measure_key].keys():
        df_score = df_score.append({
          'score': score_name,
          'measure': measure_key,
          'beat': beat_key,
          'strip': measure_strip_dict[measure_key],
          'page': page_num,
          'hpixel': beat_locations[measure_key][beat_key],
        }, ignore_index=True)

  mid = pretty_midi.PrettyMIDI(midi_filepath)
  beats = mid.get_beats()

  assert len(beats) % len(xml_annotations['notehead_measures'].keys()) == 0

  beat_per_measure = len(beats) // len(xml_annotations['notehead_measures'].keys())
  for i in range(len(beats)):
    measure_num = 1 + (i // beat_per_measure)
    beat_num = 1 + (i % beat_per_measure)
    df_audio = df_audio.append({
      'measure': '{:}.{:}'.format(measure_num, beat_num),
      'time': beats[i]
    }, ignore_index=True)

  return df_score, df_audio

def f(xml_path):
  filename = os.path.splitext(os.path.basename(xml_path))[0]
  svg_paths = glob.glob('svg/{:}*.svg'.format(filename))

  # Sort by pages
  svg_paths = sorted(svg_paths, key=lambda x: int(x.replace('.','-').split('-')[1]))

  # midi file
  midi_path = os.path.join('midi', filename + '.mid')

  # Convert to annotation
  df_score, df_audio = process(filename, xml_path, svg_paths, midi_path)

  # Write to csv 
  df_score.to_csv(os.path.join('annot_sheet', '{:}_beats.csv'.format(filename)), index=False)
  if not os.path.exists('annot_audio/{:}'.format(filename)):
    os.mkdir('annot_audio/{:}'.format(filename))
  df_audio.to_csv(os.path.join('annot_audio', filename, '{:}.csv'.format(filename)), index=False)

if not os.path.exists('annot_sheet'):
  os.mkdir('annot_sheet')

if not os.path.exists('annot_audio'):
  os.mkdir('annot_audio')

xml_paths = glob.glob('xml/*.xml')
parallel_process(xml_paths, f, front_num=0)
# f(xml_paths[5])
