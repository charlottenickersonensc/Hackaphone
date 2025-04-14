# ===== INSTALLATIONS =====
# pip install pyaudio PyOpenGL opensimplex

import pyaudio
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from opensimplex import OpenSimplex
import time
import colorsys

class AudioVisualizer:
    def __init__(self):
        # Audio setup
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.p = pyaudio.PyAudio()
        try:
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            self.p.terminate()
            raise
        
        # Graphics setup
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        gluPerspective(45, (800/600), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        
        # Enable depth testing for proper 3D rendering
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
        # Noise generator for warping
        self.noise = OpenSimplex(seed=42)  # Using a constant seed for consistent noise patterns
        
        # Create icosahedron vertices and faces
        self.create_icosahedron()
        
        # Lighting setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [20, 30, 50, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.3, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 1.0, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        
        # Material properties
        self.base_ambient = [0.1, 0.1, 0.2, 1]
        self.base_diffuse = [0.3, 0.3, 0.8, 1]
        self.base_specular = [1, 1, 1, 1]
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.base_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.base_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.base_specular)
        glMaterialf(GL_FRONT, GL_SHININESS, 90)
        
    def create_icosahedron(self):
        # Golden ratio for icosahedron construction
        phi = (1 + math.sqrt(5)) / 2
        
        # Base vertices
        self.vertices = np.array([
            [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
            [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
            [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
        ], dtype=np.float32)
        
        # Normalize vertices
        self.vertices /= np.linalg.norm(self.vertices[0])
        
        # Store original vertices for warping
        self.original_vertices = self.vertices.copy()
        
        # Icosahedron faces
        self.faces = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]
        
    def warp_sphere(self, bass_fr, tre_fr, pitch):
        current_time = time.time()
        
        # Map pitch to specific colors:
        # Low pitch (0-0.3): purple->blue->dark green (hue: 0.7-0.5)
        # High pitch (0.7-1.0): red->orange->yellow (hue: 0.0-0.15)
        if pitch < 0.3:
            # Map 0-0.3 to 0.7-0.5 (purple to blue/green)
            hue = 0.7 - (pitch / 0.3) * 0.2
            saturation = 0.9
            value = 0.7  # Darker for low pitch
        else:
            # Map 0.3-1.0 to 0.15-0.0 (orange to red/yellow)
            hue = 0.15 * (1 - ((pitch - 0.3) / 0.7))
            saturation = 1.0
            value = 1.0  # Brighter for high pitch
            
        rgb_color = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Update material colors based on rainbow color and audio intensity
        intensity = min(bass_fr * 3, 1.0)
        
        # Create dynamic colors based on pitch and audio levels
        ambient = [
            rgb_color[0] * 0.3 * (1 + intensity),
            rgb_color[1] * 0.3 * (1 + intensity),
            rgb_color[2] * 0.3 * (1 + intensity),
            1.0
        ]
        diffuse = [
            rgb_color[0] * 0.7,
            rgb_color[1] * 0.7,
            rgb_color[2] * 0.7,
            1.0
        ]
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        
        for i in range(len(self.vertices)):
            vertex = self.original_vertices[i]
            # Generate more dynamic noise value
            noise_val = self.noise.noise3(
                vertex[0] + current_time * 0.5,
                vertex[1] + current_time * 0.7,
                vertex[2] + current_time * 0.9
            )
            
            # More responsive distance modification
            bass_influence = min(bass_fr * 4, 1.0)  # Increased bass influence
            treble_influence = min(tre_fr * 6, 1.0)  # Increased treble influence
            distance = (1 + bass_influence) + (noise_val * treble_influence * 0.5)
            
            # Apply warping with increased effect
            self.vertices[i] = vertex * distance
            
    def draw_sphere(self):
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex_idx in face:
                vertex = self.vertices[vertex_idx]
                # Calculate and normalize normal vector
                normal = vertex / np.linalg.norm(vertex)
                glNormal3fv(normal)
                glVertex3fv(vertex)
        glEnd()
        
    def get_dominant_frequency(self, spectrum, frequencies):
        """Calculate the dominant frequency from the spectrum"""
        if np.max(spectrum) > 0:
            return frequencies[np.argmax(spectrum)]
        return 0

    def process_audio(self):
        try:
            # Read audio data
            data = np.frombuffer(self.stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.float32)
            
            # Perform FFT
            spectrum = np.abs(np.fft.fft(data)[:self.CHUNK//2])
            frequencies = np.fft.fftfreq(len(data))[:self.CHUNK//2] * self.RATE
            
            # Enhanced normalization with smoothing
            max_val = np.max(spectrum)
            spectrum = spectrum / max_val if max_val > 0 else spectrum
            
            # Split into frequency bands with more precise ranges
            bass_range = int(len(spectrum) * 0.1)  # First 10% for bass
            treble_range = int(len(spectrum) * 0.6)  # Above 60% for treble
            
            bass_frequencies = spectrum[:bass_range]
            treble_frequencies = spectrum[treble_range:]
            
            # Calculate enhanced metrics with peak detection
            bass_fr = np.max(bass_frequencies) * 1.5  # Amplify bass response
            tre_fr = np.max(treble_frequencies) * 1.3  # Amplify treble response
            
            # Get dominant frequency (pitch)
            dominant_freq = self.get_dominant_frequency(spectrum, frequencies)
            
            # Normalize pitch to 0-1 range for color mapping (using log scale for better distribution)
            pitch_normalized = np.clip(np.log10(dominant_freq + 1) / 4, 0, 1)
            
            # Apply smoothing to prevent sudden jumps
            if not hasattr(self, 'prev_bass'):
                self.prev_bass = bass_fr
                self.prev_treble = tre_fr
                self.prev_pitch = pitch_normalized
            
            smooth_factor = 0.7
            bass_fr = smooth_factor * self.prev_bass + (1 - smooth_factor) * bass_fr
            tre_fr = smooth_factor * self.prev_treble + (1 - smooth_factor) * tre_fr
            pitch_normalized = smooth_factor * self.prev_pitch + (1 - smooth_factor) * pitch_normalized
            
            self.prev_bass = bass_fr
            self.prev_treble = tre_fr
            self.prev_pitch = pitch_normalized
            
            return bass_fr, tre_fr, pitch_normalized
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            return 0.0, 0.0, 0.0  # Return zero values for bass, treble, and pitch
        
    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        self.stream.stop_stream()
                        self.stream.close()
                        self.p.terminate()
                        return
                        
                # Clear screen
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                # Process audio and update visualization
                bass_fr, tre_fr, pitch = self.process_audio()
                self.warp_sphere(bass_fr * 2, tre_fr * 4, pitch)
                
                # Dynamic rotation based on pitch and audio levels
                # Low pitch: very slow rotation (0.2-1)
                # High pitch: fast rotation (4-8)
                if pitch < 0.3:
                    # Slow rotation for low pitches
                    base_speed = 0.2 + (pitch / 0.3) * 0.8
                else:
                    # Fast rotation for high pitches
                    base_speed = 1.0 + ((pitch - 0.3) / 0.7) * 7.0
                
                rotation_speed = base_speed + (bass_fr * 1.5)  # Add slight bass influence
                glRotatef(rotation_speed, 3, 1 + pitch * 2, 1)
                
                # Draw sphere
                self.draw_sphere()
                
                # Update display
                pygame.display.flip()
                pygame.time.wait(10)
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            pygame.quit()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

if __name__ == "__main__":
    try:
        visualizer = AudioVisualizer()
        visualizer.run()
    except Exception as e:
        print(f"Failed to start visualizer: {e}")