from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import io
import csv
import sqlite3
import logging
import numpy as np


class DatabaseDir:
    def __init__(self):
        self.database_name = "crystal.db"
        self.home_dir = os.path.expanduser("~")
        self.main_data_dir = os.path.join(self.home_dir, "Crystal_data")
        self.database_dir = os.path.join(self.main_data_dir, self.database_name)

    def get_database_dir(self):
        return self.database_dir

    def set_database_dir(self, new_database_dir):
        self.database_dir = new_database_dir
        logging.info("Database dir set to: {}".format(self.database_dir))


# Get main dataset directory
dd = DatabaseDir()


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# TODO: Close database connections in all functions


def open_data_base_connection(skip_dir_check=False):
    """
    Creates a connections to the crystal database.
    :param skip_dir_check: bool, True  -> Skips checking database file and creates a new one if not present.
                                          This is used by Crystal.py to create a new database the first time.
                                 False -> Raises a error if the database file is not found.
    :return: conn, c -> connection and cursor object
    """
    if not skip_dir_check:
        assert os.path.isfile(dd.get_database_dir()), \
            "Database file not found in {}. " \
            "Please ensure that you have written data atleast once.".format(dd.get_database_dir())

    # Converts np.array to TEXT when inserting
    sqlite3.register_adapter(np.ndarray, adapt_array)

    # Converts TEXT to np.array when selecting
    sqlite3.register_converter("array", convert_array)

    conn = sqlite3.connect(dd.get_database_dir(), detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    return conn, c


def drop_run(project_name, run_name):
    """
    Deletes a run from a desired project. If this causes the run_table to be empty then the entire project gets deleted
    :param project_name: String, project which contains the desire run_name
    :param run_name: String, run to delete
    """
    conn, c = open_data_base_connection()
    # delete all the variable tables first
    c.execute("SELECT variable_name FROM {}".format(run_name))
    try:
        all_variables = np.array(c.fetchall()).squeeze(axis=1)
        for i in all_variables:
            variable_table_name = run_name + '_' + i
            c.execute("""DROP TABLE IF EXISTS {}""".format(variable_table_name))
    except np.core._internal.AxisError:
        print("Did not find any values, so deleting run table directly.")

    c.execute("""DROP TABLE IF EXISTS {}""".format(run_name))
    c.execute("""DELETE FROM {} WHERE run_name='{}'""".format(project_name + '_run_table', run_name))

    # delete project if project_name+'_run_table' is empty
    c.execute("""SELECT run_name FROM {}""".format(project_name + '_run_table'))
    all_runs = c.fetchall()
    if len(all_runs) == 0:
        c.execute("""DROP TABLE IF EXISTS {}""".format(project_name + '_run_table'))
        c.execute("""DELETE FROM main_table WHERE project_name='{}'""".format(project_name))

    conn.commit()
    print("{} table deleted".format(run_name))


def drop_project(project_name):
    """
    Deletes all the tables associated with a project and removes it from the main_table
    :param project_name: String, project to delete
    """
    conn, c = open_data_base_connection()
    # Need to delete all the run_tables before removing the project_table and the entry from the main_table
    run_table_name = project_name + '_run_table'

    c.execute("SELECT run_name FROM {}".format(run_table_name))
    run_names = np.array(c.fetchall()).squeeze(axis=1)

    # remove one run at a time
    for run in run_names:
        drop_run(project_name, run, conn)

    c.execute("DROP TABLE IF EXISTS {}".format(run_table_name))

    # Remove the project row from main table
    c.execute("""DELETE FROM main_table WHERE project_name='{}'""".format(project_name))
    conn.commit()
    print("{} project deleted".format(project_name))


def get_latest_run():
    """
    Returns the run latest run from the database.
    :return: dict -> {<int_keys>: <run_name>}
    """
    conn, c = open_data_base_connection()

    # Get latest project
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall())
    latest_project_name = project_names[-1][-1]

    # Get latest run
    c.execute("""SELECT run_name FROM {}""".format(latest_project_name + "_run_table"))
    run_names = np.array(c.fetchall())
    latest_run_name = convert_list_to_dict(np.squeeze(run_names, 1)[-1])
    conn.close()

    return latest_run_name


def get_latest_project_and_runs():
    """
    Returns both the latest project and runs from the database.
    :return: dict -> {"latest_project": <project_name>, "latest_runs": [<run_name>]}
    """
    conn, c = open_data_base_connection()

    # Get latest project
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall())
    latest_project_name = project_names[-1][-1]

    # Get latest run
    c.execute("""SELECT run_name FROM {}""".format(latest_project_name + "_run_table"))
    run_names = np.array(c.fetchall()).squeeze(axis=1)
    conn.close()

    return {"latest_project": latest_project_name, "latest_runs": run_names}


def get_figure_stats(run_table_name):
    """
    Returns the latest variable names
    :param run_table_name: str, required run table name
    :return: dict -> {<int_keys>: <variable_name>}
    """
    conn, c = open_data_base_connection()

    # Get latest project
    c.execute("""SELECT variable_name FROM {}""".format(run_table_name))
    variable_names = convert_list_to_dict(np.array(c.fetchall()).squeeze(axis=1))
    conn.close()

    return variable_names


def get_latest_stats():
    """
    Returns the latest run and variable names.
    :return: dict -> {"latest_run": <run_name>, "variable_name": {<int_keys>: <variable_name>}}
    """
    latest_run_name = get_latest_run()
    variable_names = get_figure_stats(latest_run_name)
    latest_stats = {'latest_run': latest_run_name, 'variable_names': variable_names}

    return latest_stats


def get_projects():
    """
    Returns a dict of projects present in the database.
    :return: dict -> {<int_keys>: <project_name>}
    """
    conn, c = open_data_base_connection()
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall()).squeeze(axis=1)
    project_names = convert_list_to_dict(project_names)
    conn.close()

    return project_names


def get_runs(project_name):
    """
    Returns a dict of runs present in project.
    :return: dict -> {<int_keys>: <project_name>}
    """
    conn, c = open_data_base_connection()
    c.execute("""SELECT run_name FROM {}""".format(project_name + "_run_table"))
    run_names = np.array(c.fetchall()).squeeze(axis=1)
    run_names = convert_list_to_dict(run_names)
    conn.close()

    return run_names


def get_variables(run_name):
    """
    Returns a dict of variables in the selected run table.
    :param run_name: str, required run table name
    :return: dict -> {<int_keys>: <variable_name>}
    """
    conn, c = open_data_base_connection()

    # Get latest project
    c.execute("""SELECT variable_name FROM {}""".format(run_name))
    variable_names = np.array(c.fetchall()).squeeze(axis=1)
    variable_names = convert_list_to_dict(variable_names)
    conn.close()

    return variable_names


def get_variable_update_dicts(current_index, variable_names, selected_run):
    """

    :return:
    """
    conn, c = open_data_base_connection()
    data = {}
    for _, v_n in variable_names:
        data[v_n] = {'x': [], 'y': [], 'z': [], 'vn': []}

    try:
        # values for each variable
        for _, v_n in variable_names:
            plot_type = v_n.split("_")[0]
            if plot_type == "scalar":
                try:
                    c.execute("""SELECT X_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    x_values = np.array(c.fetchall()).squeeze().tolist()
                    c.execute("""SELECT Y_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    y_values = np.array(c.fetchall()).squeeze().tolist()
                    data[v_n]["x"] = x_values
                    data[v_n]["y"] = y_values
                    n_values = len(x_values)
                    current_index["{}".format(v_n)] += n_values
                    logging.info("New value found and updated")
                except IndexError:
                    logging.info("No new data point found")
            elif plot_type == "heatmap":
                try:
                    c.execute("""SELECT X_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    x_values = np.array(c.fetchall()).squeeze().tolist()
                    c.execute("""SELECT Y_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    y_values = np.array(c.fetchall()).squeeze().tolist()
                    c.execute("""SELECT V_names FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    v_values = np.array(c.fetchall()).squeeze().tolist()
                    data[v_n]["x"] = x_values
                    data[v_n]["z"] = y_values
                    data[v_n]["vn"] = v_values
                    n_values = len(x_values)
                    current_index["{}".format(v_n)] += n_values
                    logging.info("New value found and updated")
                except sqlite3.OperationalError:
                    c.execute("""SELECT X_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    x_values = np.array(c.fetchall()).squeeze().tolist()
                    c.execute("""SELECT Y_value FROM {} WHERE rowid > {}""".format(selected_run + "_" + v_n,
                                                                                   current_index[v_n]))
                    y_values = np.array(c.fetchall()).squeeze().tolist()
                    data[v_n]["x"] = x_values
                    data[v_n]["z"] = y_values
                    n_values = len(x_values)
                    current_index["{}".format(v_n)] += n_values
                    logging.info("New value found and updated")
                except IndexError:
                    logging.info("No new data point found")
    except KeyError:
        logging.error("I think the run variable has changes. So, I'm passing no data.")

    conn.close()
    return data


def generate_graph_csv(variable_table_name):
    """
    Generates a temporary CSV file that contains the data for the selected variable table name.
    :param variable_table_name: str, variable table name
    :return: str, temp CSV file path
    """
    temp_csv = home_dir + "/PycharmProjects/crystal/crystal/static/temp.csv"
    conn, c = open_data_base_connection()

    # Get variable data
    c.execute("""SELECT * FROM {}""".format(variable_table_name))
    with open(temp_csv, "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in c.description])  # write headers
        csv_writer.writerows(c)
        print("File saved: {}".format(temp_csv))
        conn.close()

        return temp_csv


def convert_list_to_dict(input_list):
    """
    Convert a list of values into a dict with int as keys
    :param input_list: list, list to convert
    :return: dict -> {<int_keys>: <list_elements>}
    """
    return {k: v for k, v in enumerate(input_list)}
