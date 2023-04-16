import argparse
import os
import subprocess
import logging
import sys
import time
from collections import namedtuple
from enum import Enum
from typing import Union, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CodecInfo:
    extension: str = None
    codec: str = None
    lib: str = None

    def __init__(self, extension: str, codec: str, lib: str):
        self.extension = extension
        self.codec = codec
        self.lib = lib

    def __str__(self):
        return f"codec:{self.codec} (ext:{self.extension}, lib:{self.lib})"


class Codec(Enum):
    h265 = CodecInfo("mp4", "h265", "libx265")
    av1 = CodecInfo("mkv", "av1", "libaom-av1")

    def __str__(self):
        return f"{self.value}"


class Resolution(Enum):
    fhd = "1920:1080"
    uhd = "3840:2160"


class VideoPresetInfo:
    codec: Codec = None
    resolution: Resolution = None
    bitrateMbps: int = None

    def __init__(self, codec: Codec, resolution: Resolution, bitrateMbps: int):
        self.codec = codec
        self.resolution = resolution
        self.bitrateMbps = bitrateMbps

    def __str__(self):
        return f"{self.codec} {self.resolution.name}:{self.resolution.value} {self.bitrateMbps}Mbps"


class VideoPreset(Enum):
    h265_fhd_6 = VideoPresetInfo(Codec.h265, Resolution.fhd, 6)
    h265_uhd_40 = VideoPresetInfo(Codec.h265, Resolution.uhd, 40)
    av1_fhd_5 = VideoPresetInfo(Codec.av1, Resolution.fhd, 5)
    av1_uhd_20 = VideoPresetInfo(Codec.av1, Resolution.uhd, 20)


def get_preset_by_name(preset_name: str) -> VideoPresetInfo or None:
    for preset in VideoPreset:
        if preset.name == preset_name:
            return preset.value
    return None


def get_mp4_files(path: Union[str, Path]) -> List[Path]:
    path = Path(path)
    mp4_files = []

    if path.is_file() and path.suffix.lower() == '.mp4':
        mp4_files.append(path)
    elif path.is_dir():
        for file in path.rglob('*'):
            if file.suffix.lower() == '.mp4':
                mp4_files.append(file)
    else:
        print(f"{path} is neither a valid file nor a folder.")
    return mp4_files


def exec_ffmpeg(input_path: Path, output_path: Path, preset: VideoPresetInfo) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)

    logging.info(f"converting: {input_path} to {output_path}")
    logging.info("input_path: " + str(input_path))
    logging.info("output_path: " + str(output_path))

    if not input_path.exists():
        error_msg = f"Input file {input_path} does not exist."
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    if output_path.exists():
        logging.warning(f"Output file {output_path} already exists. Skipping conversion.")
        return

    cmd = f'ffmpeg -i "{input_path}" -c:v {preset.codec.value.lib} -crf 23 -preset medium ' \
          f'-vf "scale={preset.resolution.value}" -c:a copy ' \
          f'-loglevel error "{output_path}"'

    logging.info(f"Executing command: {cmd}");

    try:
        subprocess.run(cmd, check=True, shell=True)
        logging.info(f"Conversion completed successfully. Output file: {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred during ffmpeg execution: {e}")
        raise


def process_mp4_files(mp4_files: List[Path], preset: VideoPresetInfo) -> None:
    total_files = len(mp4_files)
    start_time = time.time()

    for index, input_file in enumerate(mp4_files, start=1):
        extra_info = f"{preset.resolution.name}_{preset.codec.value.codec}_{preset.bitrateMbps}mbps"
        output_file = input_file\
            .with_stem(f"{input_file.stem}_{extra_info}") \
            .with_suffix("." + preset.codec.value.extension)

        exec_ffmpeg(input_file, output_file, preset)

        elapsed_time = time.time() - start_time
        time_per_file = elapsed_time / index
        remaining_files = total_files - index
        estimated_time_left = remaining_files * time_per_file

        logging.info(
            f"Processed {index}/{total_files}, Elapsed: {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}, Estimated time left: {time.strftime('%H:%M:%S', time.gmtime(estimated_time_left))}")


def main(input_path: Path, preset: VideoPresetInfo) -> None:
    mp4_files: List[Path] = get_mp4_files(input_path)

    process_mp4_files(mp4_files, preset)


if __name__ == "__main__":
    possible_presets: List[str] = [member.name for member in VideoPreset]

    parser = argparse.ArgumentParser(description="Find all .mp4 files in the given file or folder.")
    parser.add_argument("-i", "--input", required=False, help="Input file or folder path")
    parser.add_argument("-p", "--preset", default=possible_presets[0],
                        choices=possible_presets, help="Video Presets: "
                                                       + ", ".join(possible_presets) + ".")
    parser.add_argument("-l", "--list-presets", action="store_true", help="List numbers from 1 to 10")
    args = parser.parse_args()

    if args.list_presets:
        print("")
        print("PRESETS:")
        for member in VideoPreset:
            print(f"  * {member.name}: {member.value}")
        print("")
        exit(1)

    preset: VideoPresetInfo = get_preset_by_name(args.preset)

    logging.info(f"input: {args.input}")
    logging.info(f"preset: {preset}")

    main(args.input, preset)
