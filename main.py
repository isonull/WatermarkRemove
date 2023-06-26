import json
import argparse
from src.query import QueryProcessors
from src.remove import RemoveProcessors
from src.utility import video_writer_from_cap, add_audio_to_video
import cv2
import os


def get_files(dir):
    files = []
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files


MAGIC_NUMBER = 71326578936


def process_file(config_path, input_path, output_path, remove_tmp=True):
    noext, ext = os.path.splitext(output_path)
    if ext != '.mp4':
        raise Exception('only mp4v output is supported')
    dir = os.path.dirname(output_path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    print(f'processing {input_path} by config {config_path} to {output_path}')

    with open(config_path) as f:
        config = json.load(f)

    print('construct query processors')
    query_processors = QueryProcessors.from_config(config)

    cap = cv2.VideoCapture(input_path)
    affine, qrcode = query_processors.process_video(cap, release=True)

    print('construct remove processors')
    remove_processors = RemoveProcessors.from_config(config)

    cap = cv2.VideoCapture(input_path)
    tmp_output_path = f'{noext}-TMP-{MAGIC_NUMBER}.avi'
    writer = video_writer_from_cap(tmp_output_path, cap)

    remove_processors.process_cap(writer, cap, affine, qrcode, release=True)

    bitrate = config.get('bitrate', None)
    if bitrate is None:
        print('using default bitrate 4000k')
        bitrate = '4000k'
    print(f'using bitrate {bitrate}')
    add_audio_to_video(
        tmp_output_path, input_path, output_path, bitrate=bitrate)
    if remove_tmp:
        os.remove(tmp_output_path)


def process_dir(config_path, input_path, output_path, ext='mp4'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for file in os.listdir(input_path):
        input_file = os.path.join(input_path, file)
        output_file = os.path.join(output_path, file)
        output_file = os.path.splitext(output_file)[0]+'.mp4'
        if os.path.isfile(input_file):
            process_file(config_path, input_file, output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help='path to config file')
    parser.add_argument('--input', '-i', help='path to input mp4 video')
    parser.add_argument('--output', '-o', help='path to output mp4 video')

    args = parser.parse_args()

    config_path = args.config
    input_path = args.input
    output_path = args.output

    if input_path == output_path:
        print('input path and output path cannot be the same')
        return

    if os.path.isfile(input_path):
        process_file(config_path, input_path, output_path)
    elif not os.path.isfile(input_path):
        process_dir(config_path, input_path, output_path)
    else:
        print('input and output must both be either file or dir')


if __name__ == '__main__':
    main()
