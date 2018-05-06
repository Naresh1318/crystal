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
database_name = "/crystal.db"

app = Flask(__name__)

current_index = {}  # Used to keep track of the index for plotting


@app.route('/')
def index():
    """
    Renders the dashboard when the server is initially run.
    Points to the latest run under the latest project by default.
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
    variable_names = latest_stats['variable_names'].squeeze(axis=1)

    data = {}
    for v_n in variable_names:
        data[v_n] = {'x': [], 'y': []}

    if len(current_index) < 1:
        for v_n in variable_names:
            current_index["{}".format(v_n)] = 0

    print("Update index:")
    print(current_index)

    # values for each variable
    for v_n in variable_names:
        c.execute("""SELECT * FROM {} WHERE rowid > {}""".format(latest_run + "_" + v_n, current_index[v_n]))

        values = np.array(c.fetchall())
        try:
            n_values = len(values[:, 0].tolist())
            data[v_n] = {'x': values[:, 0].tolist(), 'y': values[:, 1].tolist()}
            current_index["{}".format(v_n)] += n_values
            print("New value found and updated")
        except IndexError:
            print("No new data point found")

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
