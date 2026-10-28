# Polonez

A small pseudo-3D driving game in Python. You drive a Polonez down a winding road lined with trees, bushes and stones, with a 5-speed gearbox and a synthesized engine sound.

## Controls

| Key          | Action           |
|--------------|------------------|
| W / S        | Gas / brake      |
| A / D        | Steer left / right |
| Left Shift   | Gear up          |
| Left Ctrl    | Gear down        |
| Enter        | Start (menu)     |
| Space        | Skip intro       |
| Esc          | Quit             |

## What it uses

- Python 3
- [pygame](https://www.pygame.org/) – graphics, input, music
- [numpy](https://numpy.org/) + [sounddevice](https://python-sounddevice.readthedocs.io/) – real-time engine sound

## How to run

```
pip install pygame numpy sounddevice
python main.py
```

Run it from the project folder so the images and `assets/` are found.
