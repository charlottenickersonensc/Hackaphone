import pygame
import pygame.gfxdraw
import numpy as np
import pyaudio
import colorsys
import math
import random
from scipy.fft import fft
import sys
from collections import deque

class PsychedelicVisualizer:
    def __init__(self):
        # Audio parameters
        self.CHUNK = 1024  # Number of audio samples per frame
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100  # Audio sampling rate
        self.BUFFER_SIZE = 4  # REDUCED buffer size for faster response
        
        # Amplification factors - DRAMATICALLY INCREASED
        self.AUDIO_AMPLIFICATION = 20.0  # General audio amplification
        self.BASS_AMPLIFICATION = 10.0   # Bass specific amplification
        self.HIGH_AMPLIFICATION = 8.0    # High frequency amplification
        
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
        pygame.init()
        info = pygame.display.Info()
        self.WIDTH, self.HEIGHT = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Psychedelic Audio Visualizer")
        self.clock = pygame.time.Clock()
        
        # Color parameters - faster color cycling
        self.hue_offset = 0
        self.hue_speed = 0.005  # Increased from 0.003
        self.audio_hue_influence = 0.02  # NEW: audio directly affects color
        
        # Audio processing
        self.buffer = deque(maxlen=self.BUFFER_SIZE)
        for _ in range(self.BUFFER_SIZE):
            self.buffer.append(np.zeros(self.CHUNK))
            
        # Visualization elements - increased max counts
        self.particles = []
        self.max_particles = 1000  # Doubled from 500
        self.circles = []
        self.max_circles = 16  # Doubled from 8
        self.center_x = self.WIDTH // 2
        self.center_y = self.HEIGHT // 2
        
        # Frequency bands
        self.bands = {
            'sub_bass': [20, 60],
            'bass': [60, 250],
            'low_mid': [250, 500],
            'mid': [500, 2000],
            'high_mid': [2000, 4000],
            'high': [4000, 20000]
        }
        self.band_energy = {band: 0.0 for band in self.bands}
        
        # Effect parameters - increased base values
        self.spiral_rotation = 0
        self.spiral_speed = 1.0  # Doubled from 0.5
        self.wave_offset = 0
        self.bass_impact = 0
        
        # Create persistent surfaces for trails effect
        self.persistent_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
    def process_audio(self):
        """Read audio data from microphone and process it with higher sensitivity"""
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            self.buffer.append(audio_data)
            
            # Average with previous frames - LESS smoothing for faster response
            processed_data = np.zeros(self.CHUNK)
            for i, frame in enumerate(self.buffer):
                # Stronger weighting for recent frames
                weight = (i + 1) / self.BUFFER_SIZE
                processed_data += frame * weight
            
            processed_data = processed_data / len(self.buffer)
            # AMPLIFIED normalization
            normalized_data = (processed_data / 32768.0) * self.AUDIO_AMPLIFICATION
            
            # Calculate frequency spectrum
            fft_data = fft(normalized_data)
            fft_data = np.abs(fft_data[:self.CHUNK//2])  # Only first half is useful
            # AMPLIFY the fft data for more responsive visuals
            fft_data = fft_data * 3.0
            
            # Calculate energy in each frequency band - LESS smoothing
            freq_resolution = self.RATE / self.CHUNK
            for band, (low_freq, high_freq) in self.bands.items():
                low_bin = int(low_freq / freq_resolution)
                high_bin = int(high_freq / freq_resolution)
                # Ensure bins are within range
                low_bin = max(0, min(low_bin, len(fft_data)-1))
                high_bin = max(low_bin+1, min(high_bin, len(fft_data)))
                
                # Calculate energy in this band
                energy = np.sum(fft_data[low_bin:high_bin])
                
                # Apply specific amplification based on frequency band
                if band in ['bass', 'sub_bass']:
                    energy *= self.BASS_AMPLIFICATION
                elif band in ['high', 'high_mid']:
                    energy *= self.HIGH_AMPLIFICATION
                
                # MUCH less smoothing for faster response (0.5 old + 0.5 new)
                self.band_energy[band] = 0.5 * self.band_energy[band] + 0.5 * energy
            
            return normalized_data, fft_data
        except Exception as e:
            print(f"Error capturing audio: {e}")
            return np.zeros(self.CHUNK), np.zeros(self.CHUNK//2)
    
    def get_color(self, hue_offset=0, s=0.9, v=0.9, alpha=255):
        """Generate a color with the given offset from the current hue"""
        hue = (self.hue_offset + hue_offset) % 1.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, s, v)]
        return (r, g, b, alpha)
    
    def get_rainbow_gradient(self, num_colors, alpha=255):
        """Generate a rainbow gradient with num_colors"""
        colors = []
        for i in range(num_colors):
            hue = (i / num_colors + self.hue_offset) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.9, 0.9)]
            colors.append((r, g, b, alpha))
        return colors
    
    def create_particle(self, audio_intensity):
        """Create a new particle based on audio intensity"""
        if len(self.particles) < self.max_particles:
            # MUCH more particles when louder - 3x more likely
            if random.random() < audio_intensity * 2.0:  # Increased from 0.7
                angle = random.uniform(0, math.pi * 2)
                # Much higher speed range based on audio
                speed = random.uniform(2, 6 + audio_intensity * 25)  # Increased from 3+audio*10
                # Much larger size range based on audio
                size = random.uniform(3, 10 + audio_intensity * 30)  # Increased from 5+audio*15
                lifespan = random.randint(15, 60)  # Shorter lifespan for faster turnover
                hue_offset = random.uniform(0, 1)
                
                self.particles.append({
                    'x': self.center_x,
                    'y': self.center_y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': size,
                    'lifespan': lifespan,
                    'age': 0,
                    'hue_offset': hue_offset
                })
    
    def update_particles(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['age'] += 1
            
            # Remove particles that are too old or out of bounds
            if (particle['age'] >= particle['lifespan'] or
                particle['x'] < 0 or particle['x'] > self.WIDTH or
                particle['y'] < 0 or particle['y'] > self.HEIGHT):
                self.particles.remove(particle)
    
    def create_circle(self, audio_intensity):
        """Create a new expanding circle based on audio intensity"""
        if len(self.circles) < self.max_circles:
            # WAY more circles on beats - 4x more likely
            if random.random() < audio_intensity * 2.0:  # Increased from 0.5
                self.circles.append({
                    'radius': 0,
                    'max_radius': random.uniform(200, min(self.WIDTH, self.HEIGHT) * 0.8),  # Larger max
                    'growth_rate': random.uniform(5, 20),  # Faster growth 3-10 → 5-20
                    'width': random.uniform(2, 10),  # Thicker lines 2-6 → 2-10
                    'hue_offset': random.uniform(0, 1)
                })
    
    def update_circles(self):
        """Update all expanding circles"""
        for circle in self.circles[:]:
            circle['radius'] += circle['growth_rate']
            
            # Remove circles that have reached their maximum radius
            if circle['radius'] >= circle['max_radius']:
                self.circles.remove(circle)
    
    def draw_psychedelic_spiral(self, audio_data, fft_data):
        """Draw a psychedelic spiral that reacts to the audio"""
        # Use bass frequency to affect spiral size - MUCH more impact
        bass_intensity = self.band_energy['bass'] / 5000  # Reduced threshold from 50000 to 5000
        # Much faster response from bass (less smoothing)
        self.bass_impact = 0.6 * self.bass_impact + 0.4 * bass_intensity  # Changed from 0.9/0.1
        spiral_radius = min(self.WIDTH, self.HEIGHT) * 0.45
        
        # Draw spiral
        spiral_points = []
        num_rotations = 5
        points_per_rotation = 100
        total_points = num_rotations * points_per_rotation
        
        # Create a circular gradient of colors
        colors = self.get_rainbow_gradient(total_points, alpha=200)  # More opacity
        
        for i in range(total_points):
            # Calculate angle and radius - MUCH stronger audio effect
            angle = self.spiral_rotation + (i / points_per_rotation) * math.pi * 2
            radius_factor = (i / total_points) * (1 + self.bass_impact * 2.0)  # Increased from 0.5
            radius = spiral_radius * radius_factor
            
            # Apply audio modulation to radius - STRONGER effect
            if i < len(audio_data):
                idx = i % len(audio_data)
                radius += audio_data[idx] * radius * 0.6  # Increased from 0.2
            
            # Calculate position
            x = self.center_x + math.cos(angle) * radius
            y = self.center_y + math.sin(angle) * radius
            
            # Store point and color
            spiral_points.append((x, y, colors[i]))
        
        # Draw connected spiral segments
        for i in range(1, len(spiral_points)):
            x1, y1, color1 = spiral_points[i-1]
            x2, y2, color2 = spiral_points[i]
            
            # Calculate line width based on bass impact - THICKER lines
            line_width = int(3 + self.bass_impact * 20)  # Increased from 2+impact*8
            
            # Draw line with glow effect
            pygame.draw.line(self.screen, color1, (x1, y1), (x2, y2), line_width)
            
            # Draw "bloom" at certain points for accents - BIGGER blooms
            if i % 8 == 0:  # More frequent blooms (was 10)
                bloom_size = int(6 + self.bass_impact * 30)  # Increased from 4+impact*15
                pygame.draw.circle(self.screen, color1, (int(x2), int(y2)), bloom_size)
    
    def draw_frequency_bars(self, fft_data):
        """Draw frequency bars at the bottom of the screen"""
        bar_width = self.WIDTH // (len(fft_data) // 4)
        if bar_width < 1:
            bar_width = 1
        
        num_bars = self.WIDTH // bar_width
        if num_bars > len(fft_data):
            num_bars = len(fft_data)
        
        colors = self.get_rainbow_gradient(num_bars, alpha=180)  # More visible
        
        for i in range(num_bars):
            # Use logarithmic scaling for better visual representation
            idx = int(i ** 1.3) if i > 0 else 0
            if idx >= len(fft_data):
                idx = len(fft_data) - 1
                
            # Calculate height based on frequency magnitude - MUCH taller bars
            height = int(fft_data[idx] * 0.3)  # Increased multiplier from 0.1 to 0.3
            height = min(height, self.HEIGHT // 2)  # Larger max height (was HEIGHT/3)
            
            # Draw bar
            bar_x = i * bar_width
            pygame.draw.rect(
                self.screen, 
                colors[i], 
                (bar_x, self.HEIGHT - height, bar_width - 1, height)
            )
    
    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            # Calculate alpha based on particle age
            alpha = 255 * (1 - particle['age'] / particle['lifespan'])
            color = self.get_color(hue_offset=particle['hue_offset'], alpha=int(alpha))
            
            # Draw particle with glow effect - STRONGER glow
            size = int(particle['size'])
            for r in range(size, 0, -1):  # More detailed gradients
                glow_alpha = int(alpha * (r / size) * 0.9)  # Increased from 0.8
                glow_color = color[:3] + (glow_alpha,)
                pygame.gfxdraw.filled_circle(
                    self.screen, 
                    int(particle['x']), 
                    int(particle['y']), 
                    r, 
                    glow_color
                )
    
    def draw_circles(self):
        """Draw all expanding circles"""
        for circle in self.circles:
            color = self.get_color(hue_offset=circle['hue_offset'], alpha=180)  # More visible
            pygame.draw.circle(
                self.screen,
                color,
                (self.center_x, self.center_y),
                int(circle['radius']),
                int(circle['width'])
            )
    
    def draw_wave_pattern(self, audio_data):
        """Draw a wave pattern that reacts to audio"""
        # MUCH stronger response to frequencies
        high_freq_energy = self.band_energy['high'] / 5000  # Reduced from 20000
        mid_freq_energy = self.band_energy['mid'] / 7500    # Reduced from 30000
        
        num_waves = 3
        wave_colors = self.get_rainbow_gradient(num_waves, alpha=180)  # More visible
        
        for wave_idx in range(num_waves):
            wave_points = []
            wave_offset = self.wave_offset + wave_idx * (math.pi / num_waves)
            
            # Calculate wave amplitude - MUCH stronger response
            base_amplitude = self.HEIGHT * 0.2  # Increased from 0.15
            amplitude = base_amplitude * (1 + mid_freq_energy*3 + high_freq_energy*2)  # Stronger scaling
            
            # Calculate wave frequency
            freq_factor = 1 + wave_idx * 0.5
            frequency = 0.005 * freq_factor
            
            # Draw wave points
            for x in range(0, self.WIDTH, 4):
                # Calculate base wave position
                wave = math.sin(x * frequency + wave_offset) * amplitude
                
                # Add audio modulation - STRONGER effect
                audio_idx = int((x / self.WIDTH) * len(audio_data))
                if 0 <= audio_idx < len(audio_data):
                    wave += audio_data[audio_idx] * amplitude * 0.8  # Increased from 0.3
                
                y = self.HEIGHT // 2 + wave
                wave_points.append((x, y))
            
            # Draw wave - THICKER lines
            if len(wave_points) > 1:
                pygame.draw.lines(self.screen, wave_colors[wave_idx], False, wave_points, 4)  # Increased from 3
                
    def apply_trails_effect(self):
        """Apply a trails effect by gradually fading the previous frame"""
        # Darken the persistent surface for the trail effect - SHORTER trails
        dark_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 20))  # Higher alpha for shorter trails (was 10)
        self.persistent_surface.blit(dark_surface, (0, 0))
        
        # Blit the persistent surface onto the screen
        self.screen.blit(self.persistent_surface, (0, 0))
        
        # Capture current frame to persistent surface
        self.persistent_surface.blit(self.screen, (0, 0))
    
    def draw_visualization(self, audio_data, fft_data):
        """Draw the complete visualization"""
        # Fill with black for background
        self.screen.fill((0, 0, 0))
        
        # Apply trails effect for persistence
        self.apply_trails_effect()
        
        # Calculate overall audio intensity
        audio_intensity = np.abs(audio_data).mean()
        
        # Directly affect color cycling speed based on audio
        self.hue_speed = 0.005 + audio_intensity * self.audio_hue_influence
        
        # Draw visualization elements
        self.draw_psychedelic_spiral(audio_data, fft_data)
        self.draw_wave_pattern(audio_data)
        
        # Create new particles based on audio
        self.create_particle(audio_intensity)
        self.update_particles()
        self.draw_particles()
        
        # Create new circles based on bass hits - MUCH LOWER threshold
        if self.band_energy['bass'] > 2000:  # Reduced from 20000
            self.create_circle(self.band_energy['bass'] / 5000)  # Reduced from 50000
        self.update_circles()
        self.draw_circles()
        
        # Draw frequency bars
        self.draw_frequency_bars(fft_data)
        
        # Update animation parameters - FASTER rotation based on audio
        self.spiral_rotation += self.spiral_speed * (0.02 + audio_intensity * 0.15)  # Increased from 0.01+audio*0.05
        self.wave_offset += 0.08  # Faster waves (was 0.05)
        self.hue_offset = (self.hue_offset + self.hue_speed) % 1.0
    
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
                        # NEW: Add keyboard controls for sensitivity adjustment
                        elif event.key == pygame.K_UP:
                            self.AUDIO_AMPLIFICATION *= 1.5
                            print(f"Audio amplification: {self.AUDIO_AMPLIFICATION:.1f}")
                        elif event.key == pygame.K_DOWN:
                            self.AUDIO_AMPLIFICATION /= 1.5
                            print(f"Audio amplification: {self.AUDIO_AMPLIFICATION:.1f}")
                
                # Get and process audio data
                audio_data, fft_data = self.process_audio()
                
                # Draw the visualization
                self.draw_visualization(audio_data, fft_data)
                
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
    visualizer = PsychedelicVisualizer()
    visualizer.run()