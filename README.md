# Doomscroll

Scroll, scroll, scroll. Unlimited doomscrolling by blinking your eyes.

## Features

- Blink to scroll down.
- Furrow your eyebrows to like the current video with a double-click in the center of the screen.
- Open your mouth to stop the program.
- Press `q` to stop manually.

The active TikTok, Reel, or Short window must be focused. The like action is a double-click at the center of the screen, matching the usual like gesture in short-video feeds.

## Requirements

- Python 3.10 or newer
- A webcam
- Windows, macOS, or Linux with a graphical desktop session

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

From this directory, run:

```bash
python main.py
```

On first run, the MediaPipe face-landmarker model is downloaded automatically. Keep the browser window with the short-video feed focused while the program is running.

## Controls

| Gesture / key | Action |
| --- | --- |
| Blink | Scroll down |
| Furrow eyebrows | Like current video |
| Open mouth | Exit |
| `q` | Exit |

## Further Development 

I want to create a small LLM and interface where you can tell the program in plain English which gestures you want to use for each action

## Privacy

The camera is processed locally by the Python program. No camera frames are uploaded by this project.
