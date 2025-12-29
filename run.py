#!/usr/bin/env python3
"""
3D Dragon Flying Animation using Panda3D
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AmbientLight, DirectionalLight, Vec3, Vec4,
    CardMaker, NodePath, TransparencyAttrib,
    CollisionTraverser, GeomNode, Geom, GeomVertexData,
    GeomVertexWriter, GeomTriangles, GeomVertexFormat,
    InternalName, GeomVertexArrayFormat
)
import sys
import math

class DragonFlight(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Disable default camera controls
        self.disableMouse()
        
        # Set up the environment
        self.setup_environment()
        
        # Create the dragon
        self.create_dragon()
        
        # Set up camera
        self.setup_camera()
        
        # Set up keyboard controls
        self.setup_controls()
        
        # Start the flight animation
        self.flight_task = self.taskMgr.add(self.animate_dragon, "animateDragon")
        
        # Flight parameters
        self.time = 0.0
        self.flight_speed = 0.5
        
        # Dragon movement state
        self.dragon_velocity = Vec3(0, 0, 0)
        self.dragon_position = Vec3(0, 0, 5)
        self.dragon_heading = 0.0  # in degrees
        self.dragon_pitch = -10.0
        self.dragon_roll = 0.0
        
        # Movement parameters
        self.move_speed = 10.0  # units per second
        self.turn_speed = 90.0  # degrees per second
        self.pitch_speed = 60.0  # degrees per second
        self.vertical_speed = 8.0  # units per second
        
    def setup_environment(self):
        """Set up the 3D environment with lighting and sky"""
        # Set background color (sky blue)
        self.setBackgroundColor(0.5, 0.7, 1.0, 1.0)
        
        # Add ambient light
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(Vec4(0.4, 0.4, 0.4, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)
        
        # Add directional light (sun)
        directional_light = DirectionalLight('directional_light')
        directional_light.setDirection(Vec3(-5, -5, -5))
        directional_light.setColor(Vec4(0.8, 0.8, 0.8, 1))
        directional_light_np = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_light_np)
        
        # Create a simple ground plane using CardMaker
        cm = CardMaker("ground")
        cm.setFrame(-100, 100, -100, 100)
        self.ground = self.render.attachNewNode(cm.generate())
        self.ground.setPos(0, 0, -2)
        self.ground.setColor(0.2, 0.5, 0.2, 1.0)
        self.ground.setTwoSided(True)
        
        # Add some clouds
        self.create_clouds()
        
    def create_clouds(self):
        """Create simple cloud objects using spheres"""
        self.clouds = []
        for i in range(8):
            cloud_group = self.render.attachNewNode(f"cloud_{i}")
            
            # Create cloud from multiple overlapping spheres
            for j in range(3):
                cm = CardMaker(f"cloud_part_{i}_{j}")
                cm.setFrame(-2, 2, -2, 2)
                cloud_part = cloud_group.attachNewNode(cm.generate())
                cloud_part.setPos(
                    (j - 1) * 1.5,
                    (j % 2) * 1.0,
                    0
                )
                cloud_part.setScale(1.2, 1.2, 0.8)
                cloud_part.setColor(1.0, 1.0, 1.0, 0.7)
                cloud_part.setTransparency(TransparencyAttrib.MAlpha)
            
            cloud_group.setPos(
                (i - 4) * 25,
                20 + i * 8,
                8 + i * 3
            )
            self.clouds.append(cloud_group)
    
    def create_dragon(self):
        """Create a dragon using geometric primitives"""
        self.dragon = self.create_simple_dragon()
        self.dragon.reparentTo(self.render)
        self.dragon.setScale(2, 2, 2)
        self.dragon.setPos(0, 0, 5)
        self.dragon.setHpr(0, -10, 0)
    
    def create_simple_dragon(self):
        """Create a detailed dragon shape using Panda3D primitives"""
        dragon_group = self.render.attachNewNode("dragon")
        
        # Main body (elongated, cylindrical)
        body = self.create_ellipsoid(1.2, 0.8, 0.6, 16, 12)
        body.reparentTo(dragon_group)
        body.setPos(0, 0, 0)
        body.setColor(0.7, 0.2, 0.15, 1.0)
        body.setName("body")
        
        # Neck (connects body to head)
        neck = self.create_ellipsoid(0.5, 0.4, 0.5, 12, 10)
        neck.reparentTo(dragon_group)
        neck.setPos(1.2, 0, 0.2)
        neck.setHpr(20, 0, 0)
        neck.setColor(0.75, 0.25, 0.2, 1.0)
        
        # Head (larger, more detailed)
        head = self.create_ellipsoid(0.7, 0.6, 0.7, 16, 14)
        head.reparentTo(dragon_group)
        head.setPos(2.0, 0, 0.5)
        head.setColor(0.8, 0.3, 0.25, 1.0)
        head.setName("head")
        
        # Snout (pointed)
        snout = self.create_cone(0.3, 0.8, 12)
        snout.reparentTo(dragon_group)
        snout.setPos(2.6, 0, 0.4)
        snout.setHpr(0, -15, 0)
        snout.setColor(0.85, 0.35, 0.3, 1.0)
        
        # Nostrils
        for nostril_side in [-1, 1]:
            nostril = self.create_sphere(0.08, 8)
            nostril.reparentTo(dragon_group)
            nostril.setPos(2.5, nostril_side * 0.15, 0.5)
            nostril.setColor(0.3, 0.1, 0.1, 1.0)
        
        # Eyes (glowing)
        for eye_side in [-1, 1]:
            eye = self.create_sphere(0.15, 12)
            eye.reparentTo(dragon_group)
            eye.setPos(2.2, eye_side * 0.35, 0.65)
            eye.setColor(1.0, 0.9, 0.0, 1.0)
            eye.setName(f"eye_{eye_side}")
            
            # Eye pupil
            pupil = self.create_sphere(0.08, 8)
            pupil.reparentTo(dragon_group)
            pupil.setPos(2.25, eye_side * 0.35, 0.65)
            pupil.setColor(0.0, 0.0, 0.0, 1.0)
        
        # Horns
        for horn_side in [-1, 1]:
            horn = self.create_cone(0.12, 0.6, 8)
            horn.reparentTo(dragon_group)
            horn.setPos(2.1, horn_side * 0.4, 0.9)
            horn.setHpr(0, 20, horn_side * 15)
            horn.setColor(0.6, 0.5, 0.4, 1.0)
        
        # Wings (bat-like, detailed)
        for wing_side in [-1, 1]:
            wing = self.create_dragon_wing(wing_side)
            wing.reparentTo(dragon_group)
            wing.setPos(0.3, wing_side * 0.8, 0.3)
            wing.setName(f"wing_{wing_side}")
        
        # Front legs/claws
        for leg_side in [-1, 1]:
            # Upper leg
            upper_leg = self.create_ellipsoid(0.25, 0.3, 0.4, 10, 8)
            upper_leg.reparentTo(dragon_group)
            upper_leg.setPos(0.8, leg_side * 0.6, -0.3)
            upper_leg.setHpr(0, 0, leg_side * 20)
            upper_leg.setColor(0.7, 0.2, 0.15, 1.0)
            
            # Lower leg
            lower_leg = self.create_ellipsoid(0.2, 0.25, 0.5, 10, 8)
            lower_leg.reparentTo(dragon_group)
            lower_leg.setPos(0.8, leg_side * 0.9, -0.7)
            lower_leg.setHpr(0, 0, leg_side * 10)
            lower_leg.setColor(0.7, 0.2, 0.15, 1.0)
            
            # Claw/foot
            for claw_num in range(3):
                claw = self.create_cone(0.08, 0.2, 6)
                claw.reparentTo(dragon_group)
                claw.setPos(0.8, leg_side * 1.1, -1.0 + claw_num * 0.1)
                claw.setHpr(0, 90, 0)
                claw.setColor(0.4, 0.3, 0.2, 1.0)
        
        # Back legs/claws
        for leg_side in [-1, 1]:
            # Upper leg
            upper_leg = self.create_ellipsoid(0.25, 0.3, 0.4, 10, 8)
            upper_leg.reparentTo(dragon_group)
            upper_leg.setPos(-0.5, leg_side * 0.6, -0.3)
            upper_leg.setHpr(0, 0, leg_side * 20)
            upper_leg.setColor(0.7, 0.2, 0.15, 1.0)
            
            # Lower leg
            lower_leg = self.create_ellipsoid(0.2, 0.25, 0.5, 10, 8)
            lower_leg.reparentTo(dragon_group)
            lower_leg.setPos(-0.5, leg_side * 0.9, -0.7)
            lower_leg.setHpr(0, 0, leg_side * 10)
            lower_leg.setColor(0.7, 0.2, 0.15, 1.0)
            
            # Claw/foot
            for claw_num in range(3):
                claw = self.create_cone(0.08, 0.2, 6)
                claw.reparentTo(dragon_group)
                claw.setPos(-0.5, leg_side * 1.1, -1.0 + claw_num * 0.1)
                claw.setHpr(0, 90, 0)
                claw.setColor(0.4, 0.3, 0.2, 1.0)
        
        # Tail (long and flexible)
        tail_segments = 5
        for i in range(tail_segments):
            tail_seg = self.create_ellipsoid(
                0.4 - i * 0.06, 
                0.3 - i * 0.05, 
                0.4 - i * 0.06, 
                12, 10
            )
            tail_seg.reparentTo(dragon_group)
            tail_seg.setPos(-1.0 - i * 0.6, 0, -0.1 - i * 0.1)
            tail_seg.setColor(0.7, 0.2, 0.15, 1.0)
            if i == 0:
                tail_seg.setName("tail")
        
        # Tail tip/spike
        tail_tip = self.create_cone(0.15, 0.4, 8)
        tail_tip.reparentTo(dragon_group)
        tail_tip.setPos(-4.0, 0, -0.5)
        tail_tip.setHpr(0, 0, 0)
        tail_tip.setColor(0.6, 0.5, 0.4, 1.0)
        
        # Spines along the back
        for spine_pos in [-0.8, -0.3, 0.2, 0.7, 1.2]:
            spine = self.create_cone(0.1, 0.3, 6)
            spine.reparentTo(dragon_group)
            spine.setPos(spine_pos, 0, 0.5)
            spine.setHpr(0, 0, 0)
            spine.setColor(0.6, 0.5, 0.4, 1.0)
        
        return dragon_group
    
    def create_sphere(self, radius, segments=16):
        """Create a sphere using geometry"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('sphere', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Create sphere vertices
        vertices = []
        for i in range(segments + 1):
            theta = (i / segments) * 2 * math.pi
            for j in range(segments // 2 + 1):
                phi = (j / (segments // 2)) * math.pi
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.sin(phi) * math.sin(theta)
                z = radius * math.cos(phi)
                vertex.addData3(x, y, z)
                vertices.append((i, j))
        
        # Create triangles
        for i in range(segments):
            for j in range(segments // 2):
                v1 = i * (segments // 2 + 1) + j
                v2 = i * (segments // 2 + 1) + j + 1
                v3 = (i + 1) * (segments // 2 + 1) + j
                v4 = (i + 1) * (segments // 2 + 1) + j + 1
                
                prim.addVertices(v1, v2, v3)
                prim.addVertices(v2, v4, v3)
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        node = GeomNode('sphere')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_ellipsoid(self, rx, ry, rz, segments_u=16, segments_v=12):
        """Create an ellipsoid"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('ellipsoid', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Create vertices
        vertices = []
        for i in range(segments_u + 1):
            u = (i / segments_u) * 2 * math.pi
            for j in range(segments_v + 1):
                v = (j / segments_v) * math.pi
                x = rx * math.sin(v) * math.cos(u)
                y = ry * math.sin(v) * math.sin(u)
                z = rz * math.cos(v)
                vertex.addData3(x, y, z)
                vertices.append((i, j))
        
        # Create triangles
        for i in range(segments_u):
            for j in range(segments_v):
                v1 = i * (segments_v + 1) + j
                v2 = i * (segments_v + 1) + j + 1
                v3 = (i + 1) * (segments_v + 1) + j
                v4 = (i + 1) * (segments_v + 1) + j + 1
                
                prim.addVertices(v1, v2, v3)
                prim.addVertices(v2, v4, v3)
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        node = GeomNode('ellipsoid')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_cone(self, radius, height, segments=16):
        """Create a cone"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('cone', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Tip vertex
        vertex.addData3(0, 0, height / 2)
        tip_idx = 0
        
        # Base vertices
        base_vertices = []
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = -height / 2
            vertex.addData3(x, y, z)
            base_vertices.append(i + 1)
        
        # Create triangles (sides)
        for i in range(segments):
            v1 = tip_idx
            v2 = base_vertices[i]
            v3 = base_vertices[(i + 1) % segments]
            prim.addVertices(v1, v2, v3)
        
        # Create base
        for i in range(segments - 2):
            v1 = base_vertices[0]
            v2 = base_vertices[i + 1]
            v3 = base_vertices[i + 2]
            prim.addVertices(v1, v2, v3)
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        node = GeomNode('cone')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_dragon_wing(self, side):
        """Create a detailed bat-like wing"""
        wing_group = self.render.attachNewNode(f"wing_group_{side}")
        
        # Main wing membrane (large triangle-like shape)
        # Create wing using multiple connected cards
        wing_points = [
            (0, 0, 0),           # Base (attached to body)
            (0.5, side * 0.3, 0.2),  # Mid point
            (1.2, side * 0.8, 0.1),  # Wing tip
            (0.8, side * 1.0, -0.2), # Lower tip
            (0.3, side * 0.6, -0.1), # Lower mid
        ]
        
        # Create wing membrane using triangles
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('wing', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        for point in wing_points:
            vertex.addData3(point[0], point[1], point[2])
        
        geom = Geom(vdata)
        prim = GeomTriangles(Geom.UHStatic)
        
        # Create wing surface triangles
        # Main wing surface
        prim.addVertices(0, 1, 2)  # Base to tip
        prim.addVertices(0, 2, 4)  # Base to lower
        prim.addVertices(1, 2, 3)  # Mid sections
        prim.addVertices(1, 3, 4)  # Lower sections
        
        prim.closePrimitive()
        geom.addPrimitive(prim)
        
        node = GeomNode('wing')
        node.addGeom(geom)
        wing = NodePath(node)
        wing.reparentTo(wing_group)
        wing.setColor(0.6, 0.15, 0.1, 0.7)
        wing.setTransparency(TransparencyAttrib.MAlpha)
        wing.setTwoSided(True)
        
        # Wing bones/fingers (structural support)
        for bone_num in range(3):
            bone_length = 0.8 - bone_num * 0.2
            bone = self.create_cone(0.05, bone_length, 6)
            bone.reparentTo(wing_group)
            bone.setPos(0.2 + bone_num * 0.3, side * (0.3 + bone_num * 0.2), 0.1 - bone_num * 0.1)
            bone.setHpr(0, 0, side * (20 + bone_num * 10))
            bone.setColor(0.5, 0.4, 0.3, 1.0)
        
        return wing_group
    
    def setup_camera(self):
        """Set up the camera to follow the dragon"""
        self.camera.setPos(0, -20, 8)
        self.camera.lookAt(self.dragon)
    
    def setup_controls(self):
        """Set up keyboard controls for dragon movement"""
        # Key map to track which keys are pressed
        self.keyMap = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "space": False,
            "shift": False
        }
        
        # Accept keyboard events
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        
        self.accept("arrow_left", self.set_key, ["left", True])
        self.accept("arrow_left-up", self.set_key, ["left", False])
        
        self.accept("arrow_right", self.set_key, ["right", True])
        self.accept("arrow_right-up", self.set_key, ["right", False])
        
        # Space for up, Shift for down
        self.accept("space", self.set_key, ["space", True])
        self.accept("space-up", self.set_key, ["space", False])
        
        self.accept("shift", self.set_key, ["shift", True])
        self.accept("shift-up", self.set_key, ["shift", False])
        
        # Also accept escape to exit
        self.accept("escape", sys.exit)
    
    def set_key(self, key, value):
        """Update key state"""
        self.keyMap[key] = value
    
    def animate_dragon(self, task):
        """Animate the dragon based on keyboard input"""
        dt = globalClock.getDt()
        self.time += dt
        
        # Handle turning (left/right arrows)
        if self.keyMap["left"]:
            self.dragon_heading -= self.turn_speed * dt
        if self.keyMap["right"]:
            self.dragon_heading += self.turn_speed * dt
        
        # Handle pitch (up/down arrows for pitch, space/shift for vertical)
        if self.keyMap["up"]:
            self.dragon_pitch -= self.pitch_speed * dt
            if self.dragon_pitch < -45:
                self.dragon_pitch = -45
        if self.keyMap["down"]:
            self.dragon_pitch += self.pitch_speed * dt
            if self.dragon_pitch > 45:
                self.dragon_pitch = 45
        
        # Handle vertical movement (space = up, shift = down)
        vertical_movement = 0.0
        if self.keyMap["space"]:
            vertical_movement = self.vertical_speed * dt
        if self.keyMap["shift"]:
            vertical_movement = -self.vertical_speed * dt
        
        # Calculate forward movement based on heading and pitch
        heading_rad = math.radians(self.dragon_heading)
        pitch_rad = math.radians(self.dragon_pitch)
        
        # Forward movement (always moving forward when arrow keys are pressed)
        forward_movement = 0.0
        if self.keyMap["up"] or self.keyMap["down"] or self.keyMap["left"] or self.keyMap["right"]:
            forward_movement = self.move_speed * dt
        
        # Calculate movement in 3D space
        dx = forward_movement * math.cos(heading_rad) * math.cos(pitch_rad)
        dy = forward_movement * math.sin(heading_rad) * math.cos(pitch_rad)
        dz = -forward_movement * math.sin(pitch_rad) + vertical_movement
        
        # Update dragon position
        self.dragon_position += Vec3(dx, dy, dz)
        
        # Keep dragon within reasonable bounds
        if self.dragon_position.z < 1:
            self.dragon_position.z = 1
        if self.dragon_position.z > 30:
            self.dragon_position.z = 30
        
        # Update dragon position and orientation
        self.dragon.setPos(self.dragon_position)
        
        # Calculate roll based on turning (banking effect)
        if self.keyMap["left"]:
            self.dragon_roll = min(self.dragon_roll + 60 * dt, 30)
        elif self.keyMap["right"]:
            self.dragon_roll = max(self.dragon_roll - 60 * dt, -30)
        else:
            # Gradually return to level flight
            if self.dragon_roll > 0:
                self.dragon_roll = max(self.dragon_roll - 40 * dt, 0)
            elif self.dragon_roll < 0:
                self.dragon_roll = min(self.dragon_roll + 40 * dt, 0)
        
        self.dragon.setHpr(self.dragon_heading, self.dragon_pitch, self.dragon_roll)
        
        # Animate wings (flapping - faster when moving)
        wing_flap_speed = 2.0 if forward_movement > 0 else 1.0
        wing_flap = 20 * math.sin(self.time * wing_flap_speed * 2)
        wing1 = self.dragon.find("**/wing_-1")
        wing2 = self.dragon.find("**/wing_1")
        if wing1:
            wing1.setP(wing_flap)
        if wing2:
            wing2.setP(-wing_flap)
        
        # Animate tail (swishing)
        tail_swish = 10 * math.sin(self.time * 1.5)
        tail = self.dragon.find("**/tail")
        if tail:
            tail.setR(tail_swish)
        
        # Update camera to follow dragon (third-person view)
        # Camera follows behind and slightly above
        camera_distance = 15
        camera_height = 5
        camera_offset_x = -camera_distance * math.cos(math.radians(self.dragon_heading))
        camera_offset_y = -camera_distance * math.sin(math.radians(self.dragon_heading))
        
        self.camera.setPos(
            self.dragon_position.x + camera_offset_x,
            self.dragon_position.y + camera_offset_y,
            self.dragon_position.z + camera_height
        )
        self.camera.lookAt(self.dragon)
        
        return Task.cont

def main():
    """Main entry point"""
    try:
        app = DragonFlight()
        print("Dragon Flight Animation Started!")
        print("\nControls:")
        print("  Arrow Up    - Pitch down / Move forward")
        print("  Arrow Down  - Pitch up")
        print("  Arrow Left  - Turn left")
        print("  Arrow Right - Turn right")
        print("  Space       - Move up")
        print("  Shift       - Move down")
        print("  ESC         - Exit")
        print("\nThe dragon is always moving forward when you use arrow keys!")
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure Panda3D is installed: pip install panda3d")
        sys.exit(1)

if __name__ == "__main__":
    main()
