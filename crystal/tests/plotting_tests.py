"""
realtime_sinewave.py
"""

import time
import numpy as np
from crystal import Crystal

cr = Crystal(project_name="Realtime_sine")
x_range = np.arange(0, 1000, 0.1)

for i in x_range:
    value = np.sin(2*np.pi*i)
    cr.scalar(value=value, step=i, name="sine_wave")
    print("step: {} \t value: {}".format(i, value))
    time.sleep(1)  # one value a second
