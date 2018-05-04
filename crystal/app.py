# -*- coding: utf-8 -*-
"""
crystal app.py

A multipurpose real-time plotting library.

"""

import os
import sqlite3
import numpy as np
import crystal.sql_table_utils as utils
from flask import Flask, render_template, jsonify


# Get main dataset directory
home_dir = os.path.expanduser("~")
main_data_dir = home_dir + "/Crystal_data"
database_name = "/crystal_test.db"

app = Flask(__name__)

current_index = {}


@app.route('/')
def index():
    """
    Renders the html file when the server is initially run.
    :return: Object that is taken care by flask.
    """
    # Get figure stats
    latest_stats = utils.get_latest_stats()
    latest_run = latest_stats['latest_run']
    variable_names = latest_stats['variable_names']

    # render the template (below) that will use JavaScript to read the stream
    return render_template("crystal_dashboard.html", latest_run=latest_run, variable_names=variable_names)


@app.route('/update')
def update():
    """
    Called by the XMLHTTPrequest function periodically to get new graph data. This function queries the database and
    returns all the newly added values.
    :return: JSON Object, passed on to the JS script.
    """
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get figure stats
    latest_stats = utils.get_latest_stats()
    latest_run = latest_stats['latest_run']
    variable_names = latest_stats['variable_names']

    initial_data = {}

    # TODO: I think this will slow things down, try avoiding getting all the elements from the database
    global current_index
    if len(current_index) < 1:
        for v_n in variable_names:
            current_index["{}".format(v_n)] = 0

    print("Update index:")
    print(current_index)

    # values for each variable
    for v_n in variable_names:
        c.execute("""SELECT * FROM {}""".format(latest_run + "_" + v_n[0]))
        try:
            values = np.array(c.fetchall())
            initial_data[v_n[0]] = {'x': values[current_index["{}".format(v_n)]:, 0].tolist(), 'y': values[current_index["{}".format(v_n)]:, 1].tolist()}
            current_index["{}".format(v_n)] = len(values[:, 0].tolist())
            print("New value found and updated")
        except IndexError:
            print("No new data point found")

    return jsonify(initial_data)


if __name__ == '__main__':
    app.run(debug=True)
