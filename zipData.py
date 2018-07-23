import zlib
import zipfile
import glob

OUTPUT_FILENAME = 'generated_dataset.zip'
FOLDER_TO_ZIP = ['score_annot/**', 'audio_annot/**', 'pdf/**', 'midi/**']

# Populate zip_paths
file_paths = []
for folder in FOLDER_TO_ZIP:
    file_paths.extend(glob.glob(folder, recursive=True))

# Compression mode
compression = zipfile.ZIP_DEFLATED

# Create zip file
zf = zipfile.ZipFile(OUTPUT_FILENAME, mode='w')
try:
    for file_path in file_paths:
        zf.write(file_path, file_path, compress_type=compression)
except FileNotFoundError:
    print("An error occurred")
finally:
    zf.close()


