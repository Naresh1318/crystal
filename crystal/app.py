# -*- coding: utf-8 -*-
"""
crystal app.py

A multipurpose real-time plotting library.

"""

import os
import sqlite3
import numpy as np
import crystal.sql_table_utils as utils
from flask import Flask, render_template, jsonify, request, send_file

# Get main dataset directory
home_dir = os.path.expanduser("~")
main_data_dir = home_dir + "/Crystal_data"
database_name = "/crystal.db"

current_index = {}  # Used to keep track of the index for plotting


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)  # This replaces your existing "app = Flask(__name__)"


@app.route('/')
def index():
    """
    Renders the dashboard when the server is initially run.
    Points to the latest run under the latest project by default.
    :return: Object that is taken care by flask.
    """
    # Reset current index values
    print(current_index)
    for k, v in current_index.items():
        current_index[k] = 0

    print("Current Index reset.")

    # render the template (below) that will use JavaScript to read the stream
    return render_template("crystal_dashboard.html")


@app.route('/update', methods=['POST', 'GET'])
def update():
    """
    Called by the XMLHTTPrequest function periodically to get new graph data. This function queries the database and
    returns all the newly added values.
    :return: JSON Object, passed on to the JS script.
    """
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    if request.method == 'POST':
        # Get figure stats
        selected_run = request.form['selected_run']
        variable_names = utils.get_variables(selected_run).items()

        data = {}
        for _, v_n in variable_names:
            data[v_n] = {'x': [], 'y': []}

        if len(current_index) < 1:
            for _, v_n in variable_names:
                current_index["{}".format(v_n)] = 0

        print("Update index:")
        print(current_index)

        try:
            # values for each variable
            for _, v_n in variable_names:
                c.execute("""SELECT * FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n, current_index[v_n]))

                values = np.array(c.fetchall())
                try:
                    n_values = len(values[:, 0].tolist())
                    data[v_n] = {'x': values[:, 0].tolist(), 'y': values[:, 1].tolist()}
                    current_index["{}".format(v_n)] += n_values
                    print("New value found and updated")
                except IndexError:
                    print("No new data point found")
        except KeyError:
            print("I think the run variable has changes. So, I'm passing no data.")

        return jsonify(data)


@app.route('/get_projects')
def get_projects():
    projects = utils.get_projects()
    return jsonify(projects)


@app.route('/get_runs', methods=['POST', 'GET'])
def get_runs():
    if request.method == "POST":
        selected_project = request.form["selected_project"]
        runs = utils.get_runs(selected_project)
        return jsonify(runs)
    # TODO: Add catches


@app.route('/get_variables', methods=['POST', 'GET'])
def get_variables():
    if request.method == "POST":
        selected_run = request.form["selected_run"]
        variables = utils.get_variables(selected_run)

        # Reset current_index when you select a new run
        variable_names = variables.items()

        global current_index
        current_index = {}

        if len(current_index) < 1:
            for _, v_n in variable_names:
                current_index["{}".format(v_n)] = 0

        return jsonify(variables)


@app.route('/get_graph_csv', methods=['POST', 'GET'])
def get_graph_csv():
    if request.method == "POST":
        selected_variable_table = request.form["selected_variable_table"]
        filename = utils.generate_graph_csv(selected_variable_table)
        return send_file(filename, as_attachment=True, attachment_filename='{}.csv'.format(selected_variable_table))


if __name__ == '__main__':
    app.run(debug=True)
