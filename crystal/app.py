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
import sys
import sqlite3
import logging
import numpy as np
from flask import Flask, render_template, jsonify, request, send_file, json

import crystal.sql_table_utils as utils

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
    format='%(levelname)s '
           '%(asctime)s.%(msecs)06d: '
           '%(filename)s: '
           '%(lineno)d '
           '%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

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

    Usage description:
    The rendered HTML allows the user to select a project and the desired run.

    :return: Template to render, Object that is taken care by flask.
    """
    # Reset current index values when the page is refreshed
    for k, v in current_index.items():
        current_index[k] = 0

    logging.info("Dashboard refreshed")

    # render the template (below) that will use JavaScript to read the stream
    return render_template("crystal_dashboard.html")


@app.route('/update', methods=['POST'])
def update():
    """
    Called by XMLHTTPrequest function periodically to get new graph data.

    Usage description:
    This function queries the database and returns all the newly added values.

    :return: JSON Object, passed on to the JS script.
    """
    conn, c = utils.open_data_base_connection()

    if request.method == 'POST':
        # Get figure stats
        selected_run = request.form['selected_run']
        variable_names = utils.get_variables(selected_run).items()

        data = {}
        for _, v_n in variable_names:
            data[v_n] = {'x': [], 'y': []}

        if len(current_index) < 1:
            for _, v_n in variable_names:
                current_index[v_n] = 0

        logging.info("Current index: {}".format(current_index))

        try:
            # values for each variable
            for _, v_n in variable_names:
                try:
                    c.execute("""SELECT X_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    x_values = np.array(c.fetchall()).squeeze().tolist()
                    c.execute("""SELECT Y_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    y_values = np.array(c.fetchall()).squeeze().tolist()
                    data[v_n] = {'x': x_values, 'y': y_values}
                    n_values = len(x_values)
                    current_index["{}".format(v_n)] += n_values
                    logging.info("New value found and updated")
                except IndexError:
                    logging.info("No new data point found")
        except KeyError:
            logging.error("I think the run variable has changes. So, I'm passing no data.")

        return jsonify(data)


@app.route('/get_projects', methods=['GET'])
def get_projects():
    """
    Send a dictionary of projects that are available on the database.

    Usage description:
    This function is usually called to get and display the list of projects available in the database.

    :return: JSON, {<int_keys>: <project_name>}
    """
    assert request.method == "GET", "GET request expected received {}".format(request.method)
    try:
        if request.method == 'GET':
            projects = utils.get_projects()

            return jsonify(projects)
    except Exception as e:
        logging.error(e)
    return


@app.route('/get_runs', methods=['POST'])
def get_runs():
    """
    Send a dictionary of runs associated with the selected project.

    Usage description:
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
            logging.error(e)
    return


@app.route('/get_variables', methods=['POST'])
def get_variables():
    """
    Send a dictionary of variables associated with the selected run.

    Usage description:
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
            logging.error(e)
    return


@app.route('/get_graph_csv', methods=['POST'])
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
            logging.error(e)
    return


@app.route('/delete_run', methods=['GET', 'POST'])
def delete_run():
    """
    Delete the selected run from the database.
    :return:
    """
    assert request.method == "POST", "POST request expected received {}".format(request.method)
    if request.method == "POST":
        try:
            selections = json.loads(request.form["selections"])
            utils.drop_run(selections["project"], selections["run"])
            return jsonify({"response": "deleted {}".format(selections["run"])})
        except Exception as e:
            logging.error(e)
    return


if __name__ == '__main__':
    app.run(debug=True)
