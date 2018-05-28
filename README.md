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

To get started you'll first have to install crystal using pip as follows:

``` bash
pip install crystal
```

If you want to run the crystal dashboard from any directory, then you will need to add `~/crystal_data/bin/`
to you .bashrc file:

Make the bash file under: `~/Crystal_data/bin/crystal` executable:
Run the following from the folder containing crystal bash script.

```bash
chmod +x crystal
```

```bash
vim ~/.bashrc
```

Add the bin folder in `~/Crystal_data/bin/` in the .bashrc file:
Paste the following at the end of the file.

`export PATH=$PATH:~/Crystal_data/bin/`

Now, source the changes by running:

`source ~/.bashrc`


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

If you don't mind running it manually then:

In the environment contaning crytal installation run:

```bash
python
```

In the python interpreter, run:
```python
from crystal import app
app.app.run()
```


## Insert image here:




### Docs coming soon!


## How can this be helpful?

## Where can I learn more?

## How can I contribute?

