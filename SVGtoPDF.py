# pylint: disable=invalid-name
"""
SVGtoPDF is a Python script for combining multiple SVG files for each
music sheet to a single PDF file.
"""
import glob
import os
from cairosvg import svg2pdf # pylint: disable=no-name-in-module
from PyPDF2 import PdfFileMerger
from parallel_utils import parallel_process

if not os.path.exists('pdf'):
    os.mkdir('pdf')

xml_paths = glob.glob('xml/*.xml')


def f(xml_path):
    """
    This function process SVG files based on the path to XML file.
    This function produces a single PDF file as a result.
    """
    filename = os.path.splitext(os.path.basename(xml_path))[0]
    svg_paths = glob.glob('svg/{:}*.svg'.format(filename))

    # Sort by pages
    svg_paths = sorted(
        svg_paths,
        key=lambda x: int(
            x.replace(
                '.',
                '-').split('-')[1]))

    # Individually convert SVG to PDF
    for idx, svg_path in enumerate(svg_paths):
        svg2pdf(url=svg_path, write_to='pdf/{:}-{:}.pdf'.format(filename, idx))

    # Merge pdf
    merger = PdfFileMerger()
    for idx, svg_path in enumerate(svg_paths):
        merger.append('pdf/{:}-{:}.pdf'.format(filename, idx))

    # Write PDF
    merger.write('pdf/{:}.pdf'.format(filename))

    # Remove tmp pdf files
    for idx, svg_path in enumerate(svg_paths):
        os.remove('pdf/{:}-{:}.pdf'.format(filename, idx))


xml_paths = glob.glob('xml/*.xml')
parallel_process(xml_paths, f)
