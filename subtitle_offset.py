#!/usr/bin/env python3

import argparse
import math
import os
import sys

SUB_BREAK = '\n'

def parse_args():
    parser = argparse.ArgumentParser(description=sys.argv[0])
    parser.add_argument('-o', '--offset', required=True, type=float, help='offset in seconds')
    parser.add_argument('-s', '--source_subtitle', required=True)
    parser.add_argument('-d', '--dest_subtitle', required=True)
    return vars(parser.parse_args())

def read_time(time_line):
    hours, mins, rest = time_line.split(':')
    seconds, milliseconds = rest.split(',')
    return float(hours) * 3600. + float(mins) * 60. + float(seconds) + float(milliseconds) * 1.e-3

def encode_time(f):
    hours = int(math.floor(f / 3600.))
    rest = f - 3600. * hours
    mins = int(math.floor(rest / 60))
    rest = rest - 60. * mins
    secs = int(rest)
    rest -= secs
    milliseconds = round(1.e+3 * rest)
    return f'{hours:02d}:{mins:02d}:{secs:02d},{milliseconds:03d}'

def offset_time(line, offset):
    line = line.rstrip()
    TIME_SEPARATOR = '-->'
    line_entries = line.split(' ')
    assert line_entries[1] == TIME_SEPARATOR
    from_, to_ = [encode_time(offset + read_time(line_entries[i])) for i in [0,2]]
    return ' '.join([from_, TIME_SEPARATOR, to_]) + SUB_BREAK


def subtitle_shift(source_subtitle, dest_subtitle, offset):
    assert os.path.exists(source_subtitle) and os.path.isfile(source_subtitle), 'no sub here: [{}]'.format(source_subtitle)
    dst_dir = os.path.dirname(dest_subtitle)
    assert os.path.exists(dst_dir) and os.path.isdir(dst_dir), 'dst dir is absent: [{}]'.format(dst_dir)
    try:
        assert not os.path.samefile(source_subtitle, dest_subtitle), 'prevents overwrite'
    except FileNotFoundError:
        pass

    max_num = -1
    with open(dest_subtitle, 'w') as dst_file, open(source_subtitle, 'r') as src_file:
        while True:
            try:
                num_line = next(src_file)
            except StopIteration:
                break
            max_num = max(max_num, int(num_line))
            dst_file.write(num_line)
            time_line = next(src_file)
            dst_file.write(offset_time(time_line, offset))

            text_read = False
            while not text_read:
                try:
                    sub_line = next(src_file)
                except StopIteration:
                    break
                dst_file.write(sub_line)
                text_read = sub_line == SUB_BREAK
    #print('done with latest entry going up to', max_num )


if '__main__' == __name__:
    #t1 = '01:55:24,000'
    #t2 = '01:55:27,280'
    #for t in [t1, t2]:
    #    rez = encode_time(read_time(t))
    #    assert rez == t, '{} /// {}'.format(t, rez)
    subtitle_shift(**parse_args())
