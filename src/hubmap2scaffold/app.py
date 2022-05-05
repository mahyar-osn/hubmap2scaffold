import os
import sys
import argparse

from hubmap2scaffold.main import get_coordinates
from hubmap2scaffold.expoints import EXPoint
from hubmap2scaffold.main import write_ex

GROUPS = {'LV': 'left ventricle myocardium',
          'RV': 'right ventricle myocardium',
          'LA': 'left atrium myocardium',
          'RA': 'right atrium myocardium',
          'AO': 'root of aorta',
          'MV': 'root of mitral valve',
          'TV': 'root of triscupid valve',
          'PV': 'root of pulmonary valve'}


class ProgramArguments(object):
    def __init__(self):
        self.input_ex = None
        self.output_ex = None


def read_ex(files_path):
    csv_data = {}
    for file in os.listdir(files_path):
        file_name = file.split('.')[0]
        points = []
        if file_name in GROUPS.keys():
            data = get_coordinates(os.path.join(files_path, file))
            for pts in data:
                points.append(_create_csv_point(pts))
            csv_data[GROUPS[file_name]] = points
    return csv_data


def _create_csv_point(pts):
    return EXPoint(float(pts[0]),
                   float(pts[1]),
                   float(pts[2]))


def main():
    args = parse_args()
    if os.path.exists(args.input_ex):
        if args.output_ex is None:
            output_ex = os.path.join(args.input_ex, 'combined.ex')
        else:
            output_ex = args.output_ex
        contents = read_ex(args.input_ex)
        if contents is None:
            sys.exit(-2)
        else:
            write_ex(output_ex, contents)
    else:
        sys.exit(-1)


def parse_args():
    parser = argparse.ArgumentParser(description="Transform HubMap extracted data files to ex format.")
    parser.add_argument("input_ex", help="Location of the input ex files.")
    parser.add_argument("--output-ex", help="Location of the output ex file. "
                                            "[defaults to the location of the input file if not set.]")

    program_arguments = ProgramArguments()
    parser.parse_args(namespace=program_arguments)

    return program_arguments


if __name__ == "__main__":
    main()
