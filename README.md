# 3D Dragon Flying Animation

3D programs showing a dragon flying through a 3D scene, built with both Panda3D and VPython.

## Features

- Animated dragon flying in a smooth path
- Dynamic camera that follows the dragon
- Animated wing flapping
- 3D environment with lighting and clouds
- Smooth flight animation with vertical and horizontal movement

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

For VPython version, you'll also need:
```bash
pip install vpython
```

## Running the Programs

### Panda3D Version (Recommended)
```bash
python run.py
```

### VPython Version
```bash
python run_vpython.py
```

## Controls

- **ESC** or close the window to exit

## How It Works

Both programs create a 3D scene with:
- A dragon made from geometric primitives (body, head, wings, tail)
- Animated flight path (circular with vertical oscillation)
- Wing flapping animation
- Following camera that tracks the dragon's movement
- Basic lighting and environment

The dragon flies in a smooth path, and the camera follows it to provide a cinematic view of the flight.

### Differences

- **Panda3D version** (`run.py`): More advanced 3D engine with better lighting and rendering
- **VPython version** (`run_vpython.py`): Simpler, easier to understand code with real-time visualization

# dragon-fly-py
