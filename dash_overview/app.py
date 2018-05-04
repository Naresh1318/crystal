import random
import numpy as np
from time import sleep
from flask import Flask, render_template, request, jsonify
from math import sqrt
from flask import Response

app = Flask(__name__)


# Dummy data
def next_indx(v):
    n = 0
    while n < v:
        yield n
        n += 1


x = next_indx(1000)
y = np.random.rand(1000)


@app.route('/')
def index():
    # render the template (below) that will use JavaScript to read the stream
    return render_template('crystal_dashboard.html')


@app.route('/stream_sqrt')
def stream():
    idx = x.__next__()
    test_data = {'x': idx, 'y': y[idx]}
    return jsonify(test_data)


app.run(debug=True)
