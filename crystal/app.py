# -*- coding: utf-8 -*-
"""
    crystal.app
    ~~~~~~~~~~~~~~

    A multipurpose real-time plotting library.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
import sqlite3
import numpy as np
import crystal.sql_table_utils as utils
from flask import Flask, render_template, jsonify, request, send_file, json

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
    Renders the dashboard when the server is initially run. The rendered HTML allows the user to select a project
    and the desired run.
    :return: Template to render, Object that is taken care by flask.
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


@app.route('/get_projects', methods=['POST', 'GET'])
def get_projects():
    """
    Send a dictionary of projects that are available on the database.
    This function is usually called to get and display the list of projects available in the database.
    :return: JSON, {<int_keys>: <project_name>}
    """
    try:
        projects = utils.get_projects()

        return jsonify(projects)
    except Exception as e:
        print("{}".format(e))


@app.route('/get_runs', methods=['POST', 'GET'])
def get_runs():
    """
    Send a dictionary of runs associated with the selected project.
    This function is usually called to get and display the list of runs associated with a selected project available
    in the database.
    :return: JSON, {<int_keys>: <run_name>}
    """
    assert request.method == "POST", "POST request expected received {}".format(request.method)
    if request.method == "POST":
        try:
            selected_project = request.form["selected_project"]
            runs = utils.get_runs(selected_project)

            return jsonify(runs)
        except Exception as e:
            print("{}".format(e))


@app.route('/get_variables', methods=['POST', 'GET'])
def get_variables():
    """
    Send a dictionary of variables associated with the selected run.
    This function is usually called to get and display the list of runs associated with a selected project available
    in the database for the user to view.
    :return: JSON, {<int_keys>: <run_name>}
    """
    assert request.method == "POST", "POST request expected received {}".format(request.method)
    if request.method == "POST":
        try:
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
        except Exception as e:
            print("{}".format(e))


@app.route('/get_graph_csv', methods=['POST', 'GET'])
def get_graph_csv():
    """
    Allows the user to download a graph's data as a CSV file.
    :return: show a dialog box that allows the user to download the CSV file.
    """
    assert request.method == "POST", "POST request expected received {}".format(request.method)
    if request.method == "POST":
        try:
            selected_variable_table = request.form["selected_variable_table"]
            filename = utils.generate_graph_csv(selected_variable_table)
            return send_file(filename, as_attachment=True, attachment_filename='{}.csv'.format(selected_variable_table))
        except Exception as e:
            print("{}".format(e))


@app.route('/delete_run', methods=['GET', 'POST'])
def delete_run():
    """
    Delete the selected run from the database.
    :return:
    """
    if request.method == "POST":
        try:
            selections = json.loads(request.form["selections"])
            utils.drop_run(selections["project"], selections["run"])
            return jsonify({"response": "deleted {}".format(selections["run"])})
        except Exception as e:
            print("{}".format(e))


if __name__ == '__main__':
    app.run(debug=True)
