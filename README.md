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

Some features provided by crystal include;
* Centralized database to store the results of all projects.
* Easy way to download results from the database if needed.
* Plots supported include scalar, histogram and images with more to come.


To get started just install crystal using pip as follows:

``` bash
$ pip install crystal
```

The installation adds a path to crystal script to `PATH` variable on linux which allows you to run
the crystal dashboard from any directory as follows:

```bash
$ crystal
```


**Note:** 
* If you install it on a virtual environment then you will only be able to run it only when
the environment is activated.


Here's how you'd plot a sine wave using crystal:

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

Let's have a closer look at some of the functions used in the above code:
* `cr = Crystal(project_name=..)` creates a new project in the database, if no project
name is provided then, the script name is used as the project name.
* `cr.scalar(value=..)` plots a scalar value and takes three parameters,
`value` stores the y-axis value which in this case is the sin output, `step` saves
the x-axis value and `name` provides a title for the plot.
* Each run in a project is assigned a unique run id that contains the time stamp. 
You can see them in the terminal and also the dashboard (described below).
* All the data is stores under `~/Crystal_data/crystal.db`.  

**Output:**

Run 

```bash
$ crystal 
```

and select a project and run name. You will see a plot that looks something like 
this:

<p align=center>

<img src="https://raw.githubusercontent.com/Naresh1318/crystal/master/README/crystal_test.gif" alt="crystal gif" width=40%/>

<p align="center"> A realtime plotting and project management library built using Plotly </p>
 
</p>


## How can this be helpful?

## Where can I learn more?

## How can I contribute?

