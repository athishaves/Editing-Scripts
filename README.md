# Editing-Scripts

Welcome to the Editing-Scripts repository! This collection of Python scripts empowers you to perform video editing and subtitle generation effortlessly. Make sure you have `ffmpeg` installed to leverage these tools effectively.

## Features

1. **Video Editing with `process.py`**

   - **Usage:** `python3 process.py <input_path> <start_time xx:xx> <end_time xx:xx> <output_path>`
   - Cut and extract a portion of a video from the specified start to end time.

2. **Subtitle Generation with `subtitles.py`**

   - **Usage:** `python3 subtitles.py <input_file>`
   - Automatically generate subtitles for a video using `pvleopard`. Edit the subtitles interactively with a user-friendly popup window created using `tkinter`. When you close the window, the edited subtitles will be added to the video.

**Note:** While these scripts work on various platforms, it is recommended to use Mac or Ubuntu for the best results, as Windows has limitations on the number of characters that can be used to run a command.

## Prerequisites

Before using the scripts, ensure that you have `ffmpeg` installed on your system. You can download it from [here](https://ffmpeg.org/download.html).

Additionally, you need to install the `pvleopard` package:

```bash
pip install pvleopard
