import crystal
import numpy as np
import time

# Testing Crystal.py
cr = crystal.Crystal()
a = np.arange(0, 10000, 0.1)

for i in a:
    cr.scalar(i**2, i, "pow")
    cr.scalar(np.cos(2*np.pi*i), i, "sin")
    print(i)
    time.sleep(2)

print("Done!")
