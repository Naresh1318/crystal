# Crystal

<p align=center>

<img src="https://raw.githubusercontent.com/Naresh1318/crystal/master/README/crystal_logo_cropped.png" alt="crystal logo" width=50%/>

A realtime plotting and project management library built using Plotly.
</p>


## What can it do?

Crystal is an alternative to the amazingly useful visualization tool
[Tensorboard](https://github.com/tensorflow/tensorboard) with some additional features that 
make it useful not just for Machine Learning but, in any project that needs realtime data 
visualizations. You can include realtime plots in your python (more languages to come) easily 
with jsut two line of code.

To get started you'll first have to install crystal using pip as follows:

`pip install crystal`

**Note:** 
* Currently, only python 3 is supported.


Here's how you'd plot a sine wave in realtime:

```python 
"""
realtime_sinewave.py
"""

import time
import numpy as np
from crystal import Crystal

cr = Crystal(project_name="Realtime sine")

for i in range(1000):
    cr.scalar(value=np.sin(2*np.pi*i), step=i, name="This is a sine wave")
    time.sleep(1)  # one value a second

```

**Output:**

## Insert image here:


### Docs coming soon!


## How can this be helpful?

## Where can I learn more?

## How can I contribute?

