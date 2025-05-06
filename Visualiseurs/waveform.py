import numpy as np
import pyaudio
import pygame
import pygame.gfxdraw
import colorsys
import sys
import math
from collections import deque

class WaveformVisualizer:
    def __init__(self):
        # Audio parameters
        self.CHUNK = 1024  # Number of audio samples per frame
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100  # Audio sampling rate
        self.BUFFER_SIZE = 10  # Number of chunks to keep in the buffer
        
        # Sensitivity settings
        self.AMPLIFICATION = 55.0  # Significantly increased from 3.5
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Visualization parameters
        self.WIDTH = 1200
        self.HEIGHT = 600
        self.BG_COLOR = (0, 0, 0)  # Black background
        self.LINE_WIDTH = 2
        self.SMOOTHING = 0.2  # Smoothing factor for waveform
        
        # Buffer for audio data
        self.buffer = deque(maxlen=self.BUFFER_SIZE)
        for _ in range(self.BUFFER_SIZE):
            self.buffer.append(np.zeros(self.CHUNK))
            
        # Color parameters
        self.hue_offset = 0
        self.hue_speed = 0.005  # Speed of color change
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Audio Waveform Visualizer")
        self.clock = pygame.time.Clock()
        
    def get_rainbow_colors(self, n, alpha=255):
        """Generate n rainbow colors with changing hue offset"""
        colors = []
        for i in range(n):
            hue = (i / n + self.hue_offset) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, 0.9)]
            colors.append((r, g, b, alpha))
        return colors
        
    def process_audio(self):
        """Read audio data from microphone and process it"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            self.buffer.append(audio_data)
            
            # Normalize and apply smoothing with previous frames
            processed_data = np.zeros(self.CHUNK)
            for i, frame in enumerate(self.buffer):
                weight = (i + 1) / self.BUFFER_SIZE
                processed_data += frame * weight
            
            processed_data = processed_data / len(self.buffer)
            return processed_data / 32768.0  # Normalize to -1.0 to 1.0
        except Exception as e:
            print(f"Error capturing audio: {e}")
            return np.zeros(self.CHUNK)
    
    def draw_waveform(self, audio_data):
        """Draw stylized waveform with rainbow gradient"""
        self.screen.fill(self.BG_COLOR)
        
        # Calculate amplitude scaling factor based on current audio levels - MUCH LARGER now
        amplitude = np.abs(audio_data).mean() * self.AMPLIFICATION
        
        # Use much more of the available height - increased from HEIGHT/3 to HEIGHT*0.9
        scale_factor = min(10.0, 0.5 + amplitude) * (self.HEIGHT * 0.4)
        
        # Create points for waveform
        points = []
        for i, sample in enumerate(audio_data):
            x = int(i / len(audio_data) * self.WIDTH)
            y = int(self.HEIGHT / 2 + sample * scale_factor)
            # Keep points within screen bounds
            y = max(5, min(self.HEIGHT - 5, y))
            points.append((x, y))
        
        # Create a mirrored version for symmetry
        mirror_points = []
        for i, sample in enumerate(audio_data):
            x = int(i / len(audio_data) * self.WIDTH)
            y = int(self.HEIGHT / 2 - sample * scale_factor)
            # Keep points within screen bounds
            y = max(5, min(self.HEIGHT - 5, y))
            mirror_points.append((x, y))
        
        # Draw the waveform with rainbow gradient
        if len(points) >= 2:
            colors = self.get_rainbow_colors(len(points)-1)
            
            # Draw lines with gradient - increased line width for visibility
            for i in range(len(points)-1):
                pygame.draw.line(self.screen, colors[i], points[i], points[i+1], self.LINE_WIDTH+1)
                pygame.draw.line(self.screen, colors[i], mirror_points[i], mirror_points[i+1], self.LINE_WIDTH+1)
            
            # Draw particles based on audio intensity
            self.draw_particles(audio_data, colors, scale_factor)
        
        # Update hue offset for next frame
        self.hue_offset = (self.hue_offset + self.hue_speed) % 1.0
    
    def draw_particles(self, audio_data, colors, scale_factor):
        """Draw particle effects based on audio amplitude"""
        num_particles = 50
        amplitude = np.abs(audio_data).mean()
        
        for i in range(num_particles):
            # Position particles based on audio data points that exceed threshold
            idx = int(i / num_particles * len(audio_data))
            if abs(audio_data[idx]) > 0.05:  # Lower threshold to show more particles
                x = int(idx / len(audio_data) * self.WIDTH)
                
                # Use the same scale_factor as the waveform for consistency
                offset = audio_data[idx] * scale_factor * 0.8
                y = int(self.HEIGHT / 2 + offset)
                
                # Keep particles within screen bounds
                y = max(5, min(self.HEIGHT - 5, y))
                
                # Particle size based on amplitude - increased for visibility
                size = int(4 + abs(audio_data[idx]) * 20)
                color_idx = min(idx, len(colors)-1)
                
                # Draw glow effect
                for r in range(size, 0, -1):
                    alpha = 120 if r == size else 60 if r == size-1 else 30
                    color = colors[color_idx][:3] + (alpha,)
                    pygame.gfxdraw.filled_circle(self.screen, x, y, r, color)
    
    def run(self):
        """Main loop for the visualizer"""
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        # Add keyboard controls for sensitivity adjustment
                        elif event.key == pygame.K_UP:
                            self.AMPLIFICATION *= 1.2
                            print(f"Amplification: {self.AMPLIFICATION:.1f}")
                        elif event.key == pygame.K_DOWN:
                            self.AMPLIFICATION /= 1.2
                            print(f"Amplification: {self.AMPLIFICATION:.1f}")
                
                # Get and process audio data
                audio_data = self.process_audio()
                
                # Draw the visualization
                self.draw_waveform(audio_data)
                
                # Update display
                pygame.display.flip()
                self.clock.tick(60)  # Limit to 60 FPS
        
        except KeyboardInterrupt:
            print("Visualization stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'p') and self.p:
            self.p.terminate()
        pygame.quit()

if __name__ == "__main__":
    visualizer = WaveformVisualizer()
    visualizer.run()