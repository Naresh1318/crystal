import os
import sqlite3
import numpy as np


# Get main dataset directory
home_dir = os.path.expanduser("~")
main_data_dir = home_dir + "/Crystal_data"
database_name = "/crystal.db"

# TODO: Close database connections in all functions


def open_data_base_connection():
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()
    return conn, c


def drop_run(project_name, run_name, conn):
    """
    Deletes a run from a desired project. If this causes the run_table to be empty then the entire project gets deleted
    :param project_name: String, project which contains the desire run_name
    :param run_name: String, run to delete
    :param conn: No Idea, connection opened to an SQL database
    """
    c = conn.cursor()
    # delete all the variable tables first
    c.execute("SELECT variable_name FROM {}".format(run_name))
    all_variables = np.array(c.fetchall()).squeeze(axis=1)
    for i in all_variables:
        variable_table_name = run_name + '_' + i
        c.execute("""DROP TABLE IF EXISTS {}""".format(variable_table_name))

    c.execute("""DROP TABLE IF EXISTS {}""".format(run_name))
    c.execute("""DELETE FROM {} WHERE run_name='{}'""".format(project_name+'_run_table', run_name))

    # delete project if project_name+'_run_table' is empty
    c.execute("""SELECT run_name FROM {}""".format(project_name+'_run_table'))
    all_runs = c.fetchall()
    if len(all_runs) == 0:
        c.execute("""DROP TABLE IF EXISTS {}""".format(project_name+'_run_table'))
        c.execute("""DELETE FROM main_table WHERE project_name='{}'""".format(project_name))

    conn.commit()
    print("{} table deleted".format(run_name))


def drop_project(project_name, conn):
    """
    Deletes all the tables associated with a project and removes it from the main_table
    :param project_name: String, project to delete
    :param conn: No Idea, connection opened to an SQL database
    """
    c = conn.cursor()
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
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get latest project
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall())
    latest_project_name = project_names[-1][-1]

    # Get latest run
    c.execute("""SELECT run_name FROM {}""".format(latest_project_name + "_run_table"))
    run_names = np.array(c.fetchall())

    latest_run_name = np.squeeze(run_names, 1)[-1]

    return latest_run_name


def get_latest_project_and_runs():
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get latest project
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall())
    latest_project_name = project_names[-1][-1]

    # Get latest run
    c.execute("""SELECT run_name FROM {}""".format(latest_project_name + "_run_table"))
    run_names = np.array(c.fetchall()).squeeze(axis=1)

    return {"latest_project": latest_project_name, "latest_runs": run_names}


def get_figure_stats(run_table_name):
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get latest project
    c.execute("""SELECT variable_name FROM {}""".format(run_table_name))
    variable_names = np.array(c.fetchall())

    return variable_names


def get_latest_stats():
    latest_run_name = get_latest_run()
    variable_names = get_figure_stats(latest_run_name)
    latest_stats = {'latest_run': latest_run_name, 'variable_names': variable_names}

    return latest_stats


def get_projects():
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()
    c.execute("""SELECT project_name FROM main_table""")
    project_names = np.array(c.fetchall()).squeeze(axis=1)
    project_names = convert_list_to_dict(project_names)
    return project_names


def get_runs(project_name):
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get latest run
    c.execute("""SELECT run_name FROM {}""".format(project_name + "_run_table"))
    run_names = np.array(c.fetchall()).squeeze(axis=1)
    run_names = convert_list_to_dict(run_names)
    return run_names


def get_variables(run_name):
    conn = sqlite3.connect(main_data_dir + database_name)
    c = conn.cursor()

    # Get latest project
    c.execute("""SELECT variable_name FROM {}""".format(run_name))
    variable_names = np.array(c.fetchall()).squeeze(axis=1)
    variable_names = convert_list_to_dict(variable_names)
    return variable_names


def convert_list_to_dict(input_list):
    return {k: v for k, v in enumerate(input_list)}

