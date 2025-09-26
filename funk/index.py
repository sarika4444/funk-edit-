import cv2
import os
import sys
import time
import numpy as np

# Use a faster flush method instead of os.system('clear')
def clear_terminal():
    sys.stdout.write("\x1b[H\x1b[J")  # ANSI escape for clear screen
    sys.stdout.flush()

def convert_frame_to_ascii(frame, width=80):
    """
    Convert a frame to ASCII art using brightness mapping.
    Optimized for speed.
    """
    ascii_chars = np.array(list(" .:-=+*#%@"))  # array lookup instead of string index

    # Keep aspect ratio (height compressed by ~2 for terminal font)
    height = max(1, int(frame.shape[0] * width / frame.shape[1] / 2))
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray_frame, (width, height))

    # Normalize and map pixels to ascii chars
    indices = (resized / 255 * (len(ascii_chars) - 1)).astype(np.int32)
    ascii_frame = "\n".join("".join(ascii_chars[row]) for row in indices)

    return ascii_frame

def play_video_in_terminal(video_path, width=80, fps=0):
    """
    Play a video in the terminal using ASCII characters.
    Keeps sync with actual video playback.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        return

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / (fps if fps > 0 else (video_fps or 30))

    start_time = time.time()
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ascii_art = convert_frame_to_ascii(frame, width)

            clear_terminal()
            sys.stdout.write(ascii_art)
            sys.stdout.flush()

            # Sync with real video time
            frame_idx += 1
            expected_time = start_time + frame_idx * frame_delay
            sleep_time = expected_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nVideo playback interrupted.")
    finally:
        cap.release()

if __name__ == "__main__":
    video_path = input("Enter the path to the video file: ").strip()

    try:
        width = int(input("Enter terminal width (default 80): ") or "80")
    except ValueError:
        width = 80

    try:
        fps = int(input("Enter FPS (default: use video FPS): ") or "0")
    except ValueError:
        fps = 0

    play_video_in_terminal(video_path, width, fps)
