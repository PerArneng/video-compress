![Video Compress Logo](grfx/video-compress-150x.png)

# Video Compress

This is a simple command-line video converter tool that leverages ffmpeg to convert .mp4 files to different formats,
resolutions, and bitrates. It supports H.265 and AV1 codecs with FHD and UHD resolutions.

## Requirements

- Python 3.6 or later
- ffmpeg with libx265 and libaom-av1 support

## Installation

1. Clone the repository or download the source code.
2. Install ffmpeg with the required libraries.

## Usage

```sh
python3 src/main.py -i <input> -p <preset>
```
## Arguments

    -i, --input: Input file or folder path containing .mp4 files.
    -p, --preset: Video preset to use for conversion. Default is h265_fhd_6.
    -l, --list-presets: List available presets and exit.

## Presets
- `h265_fhd_6`: H.265 codec, FHD (1920x1080) resolution, 6 Mbps bitrate
- `h265_uhd_40`: H.265 codec, UHD (3840x2160) resolution, 40 Mbps bitrate
- `av1_fhd_5`: AV1 codec, FHD (1920x1080) resolution, 5 Mbps bitrate
- `av1_uhd_20`: AV1 codec, UHD (3840x2160) resolution, 20 Mbps bitrate
