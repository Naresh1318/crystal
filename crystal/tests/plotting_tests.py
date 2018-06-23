"""
realtime_sinewave.py
"""

import time
import numpy as np
from crystal import Crystal

cr = Crystal(project_name="plotly_plots")
x_range = np.arange(1, 100000, 0.1)

for i in x_range:
    value = np.sin(2*np.pi*i)
    cr.scalar(value=np.random.normal(value), step=i, name="sine_wave")
    cr.scalar(value=np.random.normal(i**2, 5), step=i, name="pow")
    cr.scalar(value=np.random.normal(i**-1), step=i, name="inverse")
    cr.scalar(value=np.random.normal(i % 5), step=i, name="norm")
    print("step: {} \t value: {}".format(i, value))
    time.sleep(0.1)  # one value a second
