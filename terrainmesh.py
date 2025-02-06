import numpy as np
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt.QtWidgets import QApplication
import struct
import pyaudio
import sys
import time

class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh surface
        """

        # setup the view window
        self.app = QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle('Terrain')
        self.window.setGeometry(0, 110, 1920, 1080)
        self.window.setCameraPosition(distance=30, elevation=12)
        self.window.show()

        # constants and arrays
        self.nsteps = 1.3
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)
        
        # Calculate exact CHUNK size based on points
        self.grid_points = len(self.xpoints) * len(self.ypoints)
        self.RATE = 44100
        self.CHUNK = max(1024, self.grid_points)  # Ensure minimum buffer size

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

        # perlin noise object with seed based on current time
        self.noise = OpenSimplex(seed=int(time.time()))

        # create the vertices array
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            faces=faces,
            vertexes=verts,
            faceColors=colors,
            drawEdges=True,
            smooth=False,
        )
        self.mesh1.setGLOptions('additive')
        self.window.addItem(self.mesh1)

    def mesh(self, offset=0, height=2.5, wf_data=None):
        if wf_data is not None:
            try:
                # Convert the waveform data to a numpy array of 16-bit integers
                wf_data = np.frombuffer(wf_data, dtype=np.int16)
                
                # Normalize the data to range [-1, 1]
                wf_data = wf_data.astype(np.float32) / 32768.0
                
                # Ensure proper size by reshaping
                wf_data = np.resize(wf_data, (len(self.xpoints), len(self.ypoints)))
                
                # Scale for visualization
                wf_data *= height
            except Exception as e:
                print(f"Error processing waveform data: {e}")
                wf_data = np.ones((len(self.xpoints), len(self.ypoints)))
        else:
            wf_data = np.ones((len(self.xpoints), len(self.ypoints)))

        faces = []
        colors = []
        
        # Create vertices with proper dimensions
        verts = np.array([
            [
                x, y, wf_data[xid][yid] * self.noise.noise2(x=xid / 5 + offset, y=yid / 5 + offset)
            ] for xid, x in enumerate(self.xpoints) for yid, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        # Generate faces with proper indexing
        nx, ny = len(self.xpoints), len(self.ypoints)
        for yid in range(ny - 1):
            for xid in range(nx - 1):
                # Calculate vertex indices for the current quad
                v0 = xid + yid * nx
                v1 = v0 + 1
                v2 = v0 + nx
                v3 = v2 + 1

                # Add two triangles to make a quad
                faces.append([v0, v2, v1])
                faces.append([v2, v3, v1])

                # Add colors for both triangles
                intensity = (wf_data[xid][yid] + 1) * 0.5
                colors.append([xid / nx, 1 - xid / nx, yid / ny, 0.7])
                colors.append([xid / nx, 1 - xid / nx, yid / ny, 0.8])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

    def update(self):
        """
        update the mesh and shift the noise each time
        """
        try:
            wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
            self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
            self.offset -= 0.05
        except Exception as e:
            print(f"Error in update: {e}")

    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QApplication.instance().exec()

    def animation(self, frametime=10):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()
        
    def __del__(self):
        """
        Cleanup resources
        """
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except:
            pass

if __name__ == '__main__':
    t = Terrain()
    t.animation()