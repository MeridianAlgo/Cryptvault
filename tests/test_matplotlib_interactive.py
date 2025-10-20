"""Test matplotlib interactivity"""
import matplotlib.pyplot as plt
import numpy as np

# Create simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)
ax.set_title('Test Interactive Plot - Try zooming and panning')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.grid(True)

print("Opening interactive window...")
print("Look for toolbar at the bottom with zoom/pan buttons")
print("Try clicking the buttons and using them")
print("Close window when done")

plt.show()
