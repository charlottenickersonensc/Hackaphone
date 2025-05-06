# ===== INSTALLATIONS =====
# pip install pyo wxpython python-osc vispy

import numpy as np
from pythonosc import dispatcher, osc_server
from vispy import app, scene
import threading
import time
import os
import sys

class MusicVisualizer:
    def __init__(self):
        # Initialize variables to store OSC parameters
        self.pitch = 0.0
        self.speed = 1.0
        self.intensity = 0.0
        
        # Create Vispy canvas and view
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600))
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.fov = 45
        self.view.camera.distance = 5
        
        # Create the initial sphere mesh
        vertices, faces = self._create_sphere(1.0, 32, 32)
        self.mesh = scene.visuals.Mesh(
            vertices=vertices,
            faces=faces,
            color=(0.5, 0.7, 1.0, 1.0),
            shading='smooth'
        )
        self.view.add(self.mesh)
        
        # Set up basic scene parameters
        self.view.bgcolor = '#303030'
        
        # Add a grid to help with orientation
        grid = scene.visuals.GridLines(parent=self.view.scene)
        
        # Set camera to a good viewing angle
        self.view.camera.elevation = 30
        self.view.camera.azimuth = 45

    def _create_sphere(self, radius, rings, sectors):
        R = radius
        rings += 1
        sectors += 1

        # Vertices
        vertices = np.zeros((rings * sectors, 3))
        indices = []

        for i in range(rings):
            y = np.cos(np.pi * i / (rings - 1))
            r = np.sqrt(1 - y * y)
            
            for j in range(sectors):
                x = r * np.cos(2 * np.pi * j / (sectors - 1))
                z = r * np.sin(2 * np.pi * j / (sectors - 1))
                
                vertices[i * sectors + j] = [x * R, y * R, z * R]

        # Faces
        for i in range(rings - 1):
            for j in range(sectors - 1):
                indices.extend([
                    i * sectors + j,
                    (i + 1) * sectors + j,
                    i * sectors + j + 1
                ])
                indices.extend([
                    (i + 1) * sectors + j,
                    (i + 1) * sectors + j + 1,
                    i * sectors + j + 1
                ])

        return vertices, np.array(indices).reshape((-1, 3))

    def update_visualization(self):
        while True:
            # Create deformation based on current parameters
            vertices, faces = self._create_sphere(
                1.0 + 0.3 * np.sin(time.time() * self.speed),
                32, 32
            )
            
            # Apply pitch-based deformation
            vertices[:, 1] *= 1.0 + 0.2 * self.pitch
            
            # Apply intensity-based color and make it more vibrant
            color = np.clip([
                0.5 + 0.5 * self.intensity,
                0.2 + 0.8 * self.intensity,
                1.0,
                1.0
            ], 0, 1)
            
            # Update mesh
            self.mesh.set_data(vertices=vertices, faces=faces, color=color)
            time.sleep(1/60)  # Cap at 60 FPS

    def pitch_handler(self, address, *args):
        self.pitch = args[0]

    def speed_handler(self, address, *args):
        self.speed = args[0]

    def intensity_handler(self, address, *args):
        self.intensity = args[0]

def main():
    # Initialize visualizer
    visualizer = MusicVisualizer()
    
    # Set up OSC server
    disp = dispatcher.Dispatcher()
    disp.map("/pitch", visualizer.pitch_handler)
    disp.map("/speed", visualizer.speed_handler)
    disp.map("/intensity", visualizer.intensity_handler)
    
    server = osc_server.ThreadingOSCUDPServer(
        ('127.0.0.1', 5005),  # Change port as needed
        disp
    )
    
    # Start OSC server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Start visualization update thread
    viz_thread = threading.Thread(target=visualizer.update_visualization)
    viz_thread.daemon = True
    viz_thread.start()
    
    # Run the visualization
    visualizer.canvas.show()
    
    # Check if we should keep the visualization running indefinitely
    if os.environ.get('KEEP_RUNNING') == 'true':
        print("Visualization will run until explicitly stopped.")
        try:
            app.run(framerate=60)  # Specify framerate to ensure smooth animation
        except KeyboardInterrupt:
            print("Visualization stopped by user")
    else:
        # Legacy behavior - run for a short time
        app.run(framerate=60)

if __name__ == '__main__':
    main()