#!/usr/bin/env python3
"""
3D Dragon Flying Animation using VPython
"""

from vpython import *
import math

# Set up the scene
scene = canvas(title='Dragon Flight', width=1200, height=800, background=color.cyan)
scene.camera.follow = None

# Create the ground
ground = box(pos=vector(0, -5, 0), size=vector(200, 1, 200), color=color.green)

# Create clouds
clouds = []
for i in range(10):
    x = (i - 5) * 20
    y = 10 + i * 3
    z = (i % 3) * 15
    cloud = sphere(pos=vector(x, y, z), radius=3, color=color.white, opacity=0.7)
    clouds.append(cloud)

# Create dragon components
class Dragon:
    def __init__(self):
        # Body (elongated ellipsoid)
        self.body = ellipsoid(
            pos=vector(0, 0, 5),
            size=vector(4, 2, 1.6),
            color=color.red,
            axis=vector(1, 0, 0)
        )
        
        # Head
        self.head = sphere(
            pos=vector(2, 0, 5.3),
            radius=0.8,
            color=color.orange
        )
        
        # Eyes
        self.eye1 = sphere(
            pos=vector(2.5, 0.3, 5.5),
            radius=0.15,
            color=color.yellow
        )
        self.eye2 = sphere(
            pos=vector(2.5, -0.3, 5.5),
            radius=0.15,
            color=color.yellow
        )
        
        # Wings
        self.wing1 = box(
            pos=vector(0, 1.5, 5.5),
            size=vector(0.2, 3, 2),
            color=color.red,
            opacity=0.8
        )
        self.wing2 = box(
            pos=vector(0, -1.5, 5.5),
            size=vector(0.2, 3, 2),
            color=color.red,
            opacity=0.8
        )
        
        # Tail
        self.tail = ellipsoid(
            pos=vector(-2, 0, 5),
            size=vector(1, 3, 1),
            color=color.red,
            axis=vector(-1, 0, 0)
        )
        
        # Group all components
        self.components = [
            self.body, self.head, self.eye1, self.eye2,
            self.wing1, self.wing2, self.tail
        ]
        
        # Flight parameters
        self.time = 0.0
        self.flight_speed = 0.5
        
    def update_position(self, dt):
        """Update dragon's position and animation"""
        self.time += dt * self.flight_speed
        
        # Create smooth flying path (circular with vertical movement)
        radius = 15
        x = radius * math.cos(self.time * 0.3)
        y = radius * math.sin(self.time * 0.3)
        z = 5 + 3 * math.sin(self.time * 0.5)  # Vertical oscillation
        
        # Calculate heading (direction of movement)
        heading = math.atan2(y, x)
        pitch = -0.2 - 0.1 * math.sin(self.time * 0.5)
        
        # Update all components' positions relative to body
        base_pos = vector(x, y, z)
        
        # Body position
        self.body.pos = base_pos
        self.body.axis = vector(math.cos(heading), math.sin(heading), 0)
        
        # Head position (relative to body)
        head_offset = vector(1.5 * math.cos(heading), 1.5 * math.sin(heading), 0.3)
        self.head.pos = base_pos + head_offset
        
        # Eyes (relative to head)
        eye_offset1 = vector(0.3 * math.cos(heading + math.pi/2), 0.3 * math.sin(heading + math.pi/2), 0.2)
        eye_offset2 = vector(0.3 * math.cos(heading - math.pi/2), 0.3 * math.sin(heading - math.pi/2), 0.2)
        self.eye1.pos = self.head.pos + eye_offset1
        self.eye2.pos = self.head.pos + eye_offset2
        
        # Wings with flapping animation
        wing_flap = 0.5 * math.sin(self.time * 2)
        wing1_offset = vector(
            0,
            1.5 * math.cos(heading + math.pi/2) + wing_flap * math.cos(heading),
            0.5
        )
        wing2_offset = vector(
            0,
            -1.5 * math.cos(heading + math.pi/2) + wing_flap * math.cos(heading),
            0.5
        )
        self.wing1.pos = base_pos + wing1_offset
        self.wing2.pos = base_pos + wing2_offset
        
        # Wing rotation for flapping effect
        self.wing1.axis = vector(
            math.cos(heading),
            math.sin(heading),
            wing_flap
        )
        self.wing2.axis = vector(
            math.cos(heading),
            math.sin(heading),
            -wing_flap
        )
        
        # Tail position
        tail_offset = vector(-1.5 * math.cos(heading), -1.5 * math.sin(heading), 0)
        self.tail.pos = base_pos + tail_offset
        self.tail.axis = vector(-math.cos(heading), -math.sin(heading), 0)
        
        return base_pos

# Create the dragon
dragon = Dragon()

# Set up camera to follow dragon
def update_camera(dragon_pos):
    """Update camera to follow the dragon"""
    camera_offset = vector(
        -15 * math.cos(dragon.time * 0.3),
        -15 * math.sin(dragon.time * 0.3),
        5
    )
    scene.camera.pos = dragon_pos + camera_offset
    scene.camera.axis = dragon_pos - scene.camera.pos

# Animation loop
print("Dragon Flight Animation Started!")
print("Close the window to exit.")

while True:
    rate(60)  # 60 frames per second
    
    # Update dragon position
    dragon_pos = dragon.update_position(0.016)  # ~60 FPS
    
    # Update camera
    update_camera(dragon_pos)
    
    # Animate clouds (slow drift)
    for i, cloud in enumerate(clouds):
        cloud.pos.x += 0.01 * math.sin(i)
        if cloud.pos.x > 100:
            cloud.pos.x = -100

