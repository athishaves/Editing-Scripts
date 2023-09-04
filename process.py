import sys
import subprocess

OFFSET = 5
SUBTITLE = ".srt"
VIDEO = ".mkv"

def ms_to_time(time_ms, ms_separator = ","):
    total_seconds = time_ms // 1000
    milliseconds = time_ms % 1000
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{ms_separator}{milliseconds:03d}"

def time_to_ms(time_str):
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds, milliseconds = parts[2].split(',')
    seconds, milliseconds = int(seconds), int(milliseconds)
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds

def with_offset(time_ms, offset_s):
    return time_ms + offset_s * 1000

def get_subtitles_in_range(file_path, start_seconds, end_seconds):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    diff = end_seconds - start_seconds

    subtitles = []
    subtitle = None
    is_inside_range = False

    for line in lines:
        line = line.strip()
        if line.isdigit() and subtitle is None:
            subtitle = {'index': int(line)}

        elif ' --> ' in line:
            start, end = line.split(' --> ')
            start = start.strip()
            end = end.strip()

            subtitle_start_seconds = time_to_ms(start) - start_seconds
            subtitle_end_seconds = time_to_ms(end) - start_seconds

            if subtitle_start_seconds >= 0 and subtitle_end_seconds <= diff:
                is_inside_range = True
                subtitle['start'] = ms_to_time(subtitle_start_seconds)
                subtitle['end'] = ms_to_time(subtitle_end_seconds)

        elif not line:
            if is_inside_range:
                subtitles.append(subtitle)
                is_inside_range = False
            subtitle = None

        elif subtitle is not None:
            subtitle.setdefault('text', [])
            subtitle['text'].append(line)

    return subtitles

if len(sys.argv) != 5:
    print("Usage: python3 {} <input_path> <start_time xx:xx> <end_time xx:xx> <output_path>".format(sys.argv[0]))
    sys.exit(1)

file_path = sys.argv[1]
start_time = with_offset(time_to_ms("00:" + sys.argv[2] + ",000"), -OFFSET)
end_time = with_offset(time_to_ms("00:" + sys.argv[3] + ",000"), OFFSET)
output_path = sys.argv[4]

command = [
    "ffmpeg",
    "-i", file_path + VIDEO,
    "-ss", ms_to_time(start_time, ms_separator = "."),
    "-to", ms_to_time(end_time, ms_separator = "."),
    "-c:v", "copy",
    "-c:a", "copy",
    output_path + VIDEO
]

try:
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print("Video cut and saved successfully.")
except subprocess.CalledProcessError as e:
    print("Error:", e.stderr.decode("utf-8").strip())
    sys.exit(1)

subtitles_in_range = get_subtitles_in_range(file_path + SUBTITLE, start_time, end_time)

result = []

for subtitle in subtitles_in_range:
    result.append(f"{subtitle['index']}")
    result.append(f"{subtitle['start']} --> {subtitle['end']}")
    result.append("\n".join(subtitle['text']))

with open(output_path + SUBTITLE, "w") as file:
    for line in result:
        file.write(line + "\n")
