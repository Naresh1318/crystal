# Crystal

<p align=center>

<img src="https://raw.githubusercontent.com/Naresh1318/crystal/master/README/crystal_logo_cropped.png" alt="crystal logo" width=40%/>

<p align="center"> A realtime plotting and project management library built using Plotly </p>
 
</p>


## What can it do?

Crystal is an alternative to the amazingly useful visualization tool
[Tensorboard](https://github.com/tensorflow/tensorboard) with some additional features that 
make it useful not just for Machine Learning but, in any project that needs realtime data 
visualizations. You can include realtime plots in your python (more languages to come) easily 
with just two line of code.

To get started just install crystal using pip as follows:

``` bash
pip install crystal
```

The installation adds a path to crystal script to `PATH` on linux which allows you to run
the crystal dashboard from any directory by running on bash:

```bash
crystal
```


**Note:** 
* If you install it on a virtual environment then you will only be able to run it only when
the environment is activated.


Here's how you'd plot a sine wave in realtime:

```python 
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

```

**Output:**

Running crystal from the terminal  
(**Ensure that the virtual environment containing crystal has been loaded**):

```bash
crystal 
```


## Insert image here:




### Docs coming soon!


## How can this be helpful?

## Where can I learn more?

## How can I contribute?

