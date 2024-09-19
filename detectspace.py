import keyboard
import os
import time
import subprocess
import threading
import random

TRIGGER_KEY = ' '
RESTART_ON_PRESS = True
CLIP_LIST = '/home/kevin/clips.txt'
CLIP_SAMPLING = 'random_seq'

assert CLIP_SAMPLING in ['random', 'random_no_repeat', 'random_seq', 'ordered'], 'CLIP_SAMPLING must be "random" or "ordered"'
assert os.path.exists(CLIP_LIST), f'{CLIP_LIST} file expected to contain list of valid clip paths'

os.environ['AUDIODEV']="hw:0"

with open(CLIP_LIST, 'r') as fp:
    file_clips = fp.readlines()
    clips = []
    for clip in file_clips:
        clip = clip.strip()
        if len(clip) == 0:
            continue
        clip_exists = os.path.exists(clip)
        clip_valid = os.system(f"sox {clip} -n stat") == 0
        if not clip_exists or not clip_valid:
            print(f"Error finding or loadingclip {clip}, skipping...")
        else:
            print(f"Found valid clip {clip}!")
            clips.append(clip)

assert len(clips) > 0, "expected number of valid clips > 0 - maybe an issue with clip filenames?"

if CLIP_SAMPLING == 'random_seq':
    random.shuffle(clips)

def random_sample_index():
    global clips
    return random.randint(0, len(clips)-1)

last_clip_index = random_sample_index()

def play_sound(clip_path):
    global proc, done
    proc = subprocess.call(f"su kevin bash -c 'play {clip_path}'", shell=True)

key_up_reset = True

while True:
    try:
        if not keyboard.is_pressed(TRIGGER_KEY):
            key_up_reset = True
        if key_up_reset and keyboard.is_pressed(TRIGGER_KEY):
            key_up_reset = False
            if RESTART_ON_PRESS:
                print("Killing other playing instances!")
                os.system('killall play')
            if CLIP_SAMPLING == 'random':
                next_clip_index = random_sample_index()
            elif CLIP_SAMPLING == 'random_no_repeat':
                next_clip_index = random_sample_index()
                while len(clips) > 1 and next_clip_index == last_clip_index:
                    next_clip_index = random_sample_index()
            else: # Default is 'ordered' or 'random_seq'
                next_clip_index = (last_clip_index + 1) % len(clips)
            clip = clips[next_clip_index]
            last_clip_index = next_clip_index
            print(f'Playing clip {clip}')
            t = threading.Thread(target=play_sound, args=(clip,)).start()
    except Exception as e:
        print(e)
        break
