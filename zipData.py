import zlib
import zipfile
import glob
import sys
import os

OUTPUT_FILENAME = 'generated_dataset.zip'
file_paths = set(map(lambda x: os.path.splitext(os.path.basename(x))[0], glob.glob('annot_audio/**', recursive=True)))
FOLDER_TO_ZIP = ['annot_audio/**', 'annot_sheet/**', 'pdf/**', 'midi/**']

# Populate zip_paths
file_path_candidates = []
for folder in FOLDER_TO_ZIP:
    file_path_candidates.extend(glob.glob(folder, recursive=True))

file_paths_zip = []
for file_path_candidate in file_path_candidates:
    filename = os.path.splitext(os.path.basename(file_path_candidate))[0]
    if '_beats' in filename: filename = filename.replace('_beats', '')
    if os.path.isfile(file_path_candidate) and filename in file_paths:
        file_paths_zip.append(file_path_candidate)

# Compression mode
compression = zipfile.ZIP_DEFLATED

# Create zip file
zf = zipfile.ZipFile(OUTPUT_FILENAME, mode='w')
try:
    for file_path in file_paths_zip:
        zf.write(file_path, file_path, compress_type=compression)
except FileNotFoundError:
    print("An error occurred")
finally:
    zf.close()


