import numpy as np
import pyaudio
import pygame
import colorsys
from scipy.fft import fft
import pygame.gfxdraw
import sys
import time
from collections import deque

class FrequencyBandsVisualizer:
    def __init__(self):
        # Audio parameters
        self.CHUNK = 2048  # Larger chunk for better frequency resolution
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
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
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.BG_COLOR = (10, 10, 15)  # Dark background
        
        # Frequency bands (roughly corresponding to different instrument ranges)
        self.bands = [
            (20, 150),     # Bass/low frequencies (red)
            (150, 400),    # Lower mid-range (orange)
            (400, 800),    # Mid-range (yellow)
            (800, 1500),   # Upper mid-range (green)
            (1500, 3000),  # Upper mid-high (blue)
            (3000, 6000),  # High frequencies (indigo)
            (6000, 20000)  # Very high frequencies (violet)
        ]
        
        # Base colors for each band (pastel versions)
        self.base_colors = [
            (255, 180, 180),  # Pastel red
            (255, 200, 150),  # Pastel orange
            (255, 255, 180),  # Pastel yellow
            (180, 255, 180),  # Pastel green
            (180, 200, 255),  # Pastel blue
            (200, 180, 255),  # Pastel indigo
            (230, 180, 255)   # Pastel violet
        ]
        
        # Energy history for each band
        self.history_length = 60
        self.band_energy_history = [deque(maxlen=self.history_length) for _ in range(len(self.bands))]
        for i in range(len(self.bands)):
            for _ in range(self.history_length):
                self.band_energy_history[i].append(0.0)
        
        # Smoothing and reactivity
        self.smoothing_factor = 0.2
        self.current_energies = [0.0] * len(self.bands)
        
        # Animation parameters
        self.flow_speed = 0.5
        self.flow_offset = 0
        self.wave_height = 0.4  # Controls the height of the waves
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Music Frequency Visualizer")
        self.clock = pygame.time.Clock()
    
    def get_frequency_data(self):
        """Capture audio and perform FFT to get frequency data"""
        try:
            # Read audio data
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Apply window function to reduce spectral leakage
            window = np.hanning(len(audio_data))
            audio_data = audio_data * window
            
            # Perform FFT
            fft_data = fft(audio_data)
            fft_data = np.abs(fft_data[:self.CHUNK//2])  # Only take the first half (real part)
            
            # Normalize
            fft_data = fft_data / (128 * self.CHUNK)
            
            # Calculate frequency resolution
            freq_resolution = self.RATE / self.CHUNK
            
            return fft_data, freq_resolution
            
        except Exception as e:
            print(f"Error capturing audio: {e}")
            return np.zeros(self.CHUNK//2), self.RATE / self.CHUNK
    
    def analyze_bands(self, fft_data, freq_resolution):
        """Extract energy from each frequency band"""
        band_energies = []
        
        for band_idx, (low_freq, high_freq) in enumerate(self.bands):
            # Convert frequencies to FFT indices
            low_idx = int(low_freq / freq_resolution)
            high_idx = min(int(high_freq / freq_resolution), len(fft_data)-1)
            
            # Get band energy
            band_data = fft_data[low_idx:high_idx+1]
            energy = np.mean(band_data) * 10  # Amplify
            
            # Apply smoothing with previous value
            self.current_energies[band_idx] = self.current_energies[band_idx] * (1 - self.smoothing_factor) + energy * self.smoothing_factor
            
            # Store in history
            self.band_energy_history[band_idx].append(self.current_energies[band_idx])
            
            band_energies.append(self.current_energies[band_idx])
        
        return band_energies
    
    def draw_gradient_waves(self, band_energies):
        """Draw flowing gradient waves for each band"""
        # Clear the screen
        self.screen.fill(self.BG_COLOR)
        
        # Calculate height for each band
        band_height = self.HEIGHT / len(self.bands)
        
        # Update flow offset for animation
        self.flow_offset = (self.flow_offset + self.flow_speed) % self.WIDTH
        
        # Draw each band from bottom to top
        for i, (energy, history) in enumerate(zip(band_energies, self.band_energy_history)):
            # Calculate wave properties based on energy
            amplitude = min(band_height * 0.8, energy * band_height * self.wave_height)
            frequency = 0.01 + (energy * 0.03)
            
            # Get band color
            base_color = self.base_colors[i]
            
            # Create points for the top of the wave
            wave_top_points = []
            for x in range(self.WIDTH):
                # Calculate wave using a combination of sine waves for complexity
                phase = (x + self.flow_offset) * frequency
                wave = amplitude * (0.6 * np.sin(phase) + 
                                   0.3 * np.sin(phase * 2.1) + 
                                   0.1 * np.sin(phase * 4.5))
                
                # Intensity based on history at this x-position
                intensity_idx = int((x / self.WIDTH) * (len(history) - 1))
                intensity = history[intensity_idx] * 0.8 + energy * 0.2
                
                # Adjust y-coordinate (bottom-up)
                y_base = self.HEIGHT - (i * band_height) - band_height
                y = y_base + wave
                
                wave_top_points.append((x, y))
            
            # Create points for the bottom of the wave
            wave_bottom_points = [(x, self.HEIGHT - i * band_height) for x in range(self.WIDTH)]
            
            # Create polygon points by combining top and bottom waves
            polygon_points = wave_top_points + wave_bottom_points[::-1]
            
            # Create a gradient surface for this band
            gradient_surf = pygame.Surface((self.WIDTH, int(band_height * 1.5)), pygame.SRCALPHA)
            
            # Calculate colors for the gradient
            color1 = base_color  # Current band color
            color2 = self.base_colors[(i+1) % len(self.bands)]  # Next band color
            
            # Draw the gradient
            for y in range(int(band_height * 1.5)):
                ratio = y / (band_height * 1.5)
                
                # Make more transparent toward the bottom
                alpha = int(200 * (1 - ratio * 0.7))
                
                # Blend between colors
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                
                # Draw a line of this color
                pygame.draw.line(gradient_surf, (r, g, b, alpha), (0, y), (self.WIDTH, y))
            
            # Draw the gradient polygon
            pygame.gfxdraw.filled_polygon(self.screen, polygon_points, base_color + (180,))
            
            # Overlay the gradient
            self.screen.blit(gradient_surf, (0, self.HEIGHT - (i+1) * band_height), special_flags=pygame.BLEND_ADD)
            
            # Add some glow particles based on energy
            self.draw_glow_particles(i, energy, wave_top_points, base_color)
    
    def draw_glow_particles(self, band_idx, energy, wave_points, color):
        """Draw glowing particles on waves to enhance visual impact"""
        if energy < 0.1:
            return
            
        # Number of particles based on energy
        num_particles = int(energy * 30)
        
        for _ in range(num_particles):
            # Random position along the wave
            point_idx = np.random.randint(0, len(wave_points))
            x, y = wave_points[point_idx]
            
            # Random offset
            x_offset = np.random.randint(-20, 20)
            y_offset = np.random.randint(-10, 10)
            
            # Position
            px = x + x_offset
            py = y + y_offset
            
            # Size based on energy
            size = int(2 + energy * 6)
            
            # Make sure we're on screen
            if 0 <= px < self.WIDTH and 0 <= py < self.HEIGHT:
                # Draw glow effect
                for r in range(size, 0, -1):
                    alpha = int(100 * (r/size))
                    pygame.gfxdraw.filled_circle(self.screen, int(px), int(py), r, color + (alpha,))

    def run(self):
        """Main visualization loop"""
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        # Adjust wave height
                        elif event.key == pygame.K_UP:
                            self.wave_height = min(1.0, self.wave_height + 0.1)
                        elif event.key == pygame.K_DOWN:
                            self.wave_height = max(0.1, self.wave_height - 0.1)
                        # Adjust flow speed
                        elif event.key == pygame.K_RIGHT:
                            self.flow_speed += 0.2
                        elif event.key == pygame.K_LEFT:
                            self.flow_speed = max(0.1, self.flow_speed - 0.2)
                
                # Get frequency data
                fft_data, freq_resolution = self.get_frequency_data()
                
                # Analyze frequency bands
                band_energies = self.analyze_bands(fft_data, freq_resolution)
                
                # Draw visualization
                self.draw_gradient_waves(band_energies)
                
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
    visualizer = FrequencyBandsVisualizer()
    visualizer.run()