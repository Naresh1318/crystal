from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import sqlite3
import datetime
import numpy as np

from . import sql_table_utils as utils


DATABASE_DIR_NAME = "Crystal_data"


def get_valid_time_stamp():
    """
    Get a valid time stamp without illegal characters.
    Adds time_ to make the time stamp a valid table name in sql.
    :return: String, extracted timestamp
    """
    time_stamp = str(datetime.datetime.now())
    time_stamp = "time_" + time_stamp.replace("-", "_").replace(":", "_").replace(" ", "_").replace(".", "_")
    return time_stamp


class Crystal:
    """
    Provides methods to store various types of data onto the database.
    docs:
    * Creates a new project using the script name if no project name has been provided.
    * Creates a new run table for every class instantiation.
    """

    def __init__(self, project_name=None):
        """
        Create a crystal instance that could be used to write data onto the database.
        :param project_name: str, default -> None, uses the script name the instance is being used from as the
                                                project name.
                                          -> str, uses this name instead.
        """
        if project_name is None:
            self.called_from = os.path.realpath(sys.argv[0])
            self.project_name = os.path.basename(self.called_from)[:-3]  # Remove .py
            self.project_name = self.project_name.split(".")[0]
        else:
            # Spaces not allowed for project name
            assert len(project_name.split(" ")) < 2, \
                "Ensure that you don't have spaces in your variable name, use '_' instead."
            self.project_name = project_name

        self.time_stamp = get_valid_time_stamp()
        self.previous = [None]

        # Create a new database on the home directory if not present
        home_dir = os.path.expanduser("~")
        main_data_dir = os.path.join(home_dir, DATABASE_DIR_NAME)
        if not os.path.exists(main_data_dir):
            print("Crystal_data directory not found. Creating a new one...")
            os.mkdir(main_data_dir)

        # Create new project and run tables if not already found
        self.conn, self.c = utils.open_data_base_connection(skip_dir_check=True)
        self.run_table_name = self.project_name + '_' + 'run_table'
        self.c.execute("""CREATE TABLE IF NOT EXISTS main_table (
                          project_name VARCHAR
                          )""")
        self.c.execute("""CREATE TABLE IF NOT EXISTS {} (
                          run_name VARCHAR
                          )""".format(self.run_table_name))

        # Add current project and run to the main table and run_table if not already present
        # main_table
        self.c.execute("""SELECT project_name FROM main_table""")
        project_names = np.array(self.c.fetchall()).squeeze()

        if self.project_name not in project_names:
            self.c.execute("""INSERT INTO main_table (
                              project_name) VALUES ('{}'
                              )""".format(self.project_name))

        # run_table
        self.c.execute("""SELECT run_name FROM {run_table}""".format(run_table=self.run_table_name))
        run_names = np.array(self.c.fetchall()).squeeze()

        if self.time_stamp not in run_names:
            self.c.execute("""INSERT INTO {} (
                              run_name) VALUES ('{}'
                              )""".format(self.run_table_name, self.time_stamp))

        # variable_table -> time_stamp_table
        self.c.execute("""CREATE TABLE IF NOT EXISTS {} (
                          variable_name VARCHAR, variable_type VARCHAR
                          )""".format(self.time_stamp))
        self.conn.commit()

    def scalar(self, value, step, name):
        """
        Plot a scalar value.
        :param value: int or float, the value on the y-axis
        :param step: int or float, the value on the x-axis
        :param name: String, the name of the variable to be used during visualization
        """
        # Spaces not allowed for scalar variable name
        assert len(name.split(" ")) < 2, "Ensure that you don't have spaces in your variable name, use '_' instead."
        name = "scalar_" + name
        self.previous.append(name)
        if self.previous[-1] not in self.previous[:-1]:
            self.c.execute("""INSERT INTO {time_stamp_table} (
                              variable_name, variable_type
                              ) VALUES ('{variable}', '{type}')"""
                           .format(time_stamp_table=self.time_stamp, variable=name, type="scalar"))
        else:
            self.previous.pop()

        self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                          X_value FLOAT, Y_value FLOAT, time VARCHAR
                          )""".format(variable_table_name=self.time_stamp + '_' + name))

        self.c.execute("""INSERT INTO {variable_table_name} (
                          X_value, Y_value, time) VALUES ('{x}', '{y}', '{time}'
                          )""".format(variable_table_name=self.time_stamp + '_' + name,
                                      x=step, y=value, time=datetime.datetime.now()))
        self.conn.commit()

    # TODO: Test this
    def image(self, image, name):
        """
        Show image on the Crystal server.
        :param image:
        :param name:
        :return:
        """
        assert len(name.split(" ")) < 2, "Ensure that you don't have spaces in your variable name, use '_' instead."
        name = "image_" + name
        self.previous.append(name)
        if self.previous[-1] not in self.previous[:-1]:
            self.c.execute("""INSERT INTO {time_stamp_table} (
                              variable_name, variable_type
                              ) VALUES ('{variable}', '{type}')"""
                           .format(time_stamp_table=self.time_stamp, variable=name, type="image"))
        else:
            self.previous.pop()

        self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                          images BLOB, time VARCHAR
                          )""".format(variable_table_name=self.time_stamp + '_' + name))

        self.c.execute("""INSERT INTO {variable_table_name} (
                          images, time) VALUES ('{img}', '{time}'
                          )""".format(variable_table_name=self.time_stamp + '_' + name,
                                      img=sqlite3.Binary(np.array(image).tobytes()), time=datetime.datetime.now()))
        self.conn.commit()

    def heatmap(self, value, step, name, value_names=None):
        """

        :param value_names:
        :param step:
        :param value:
        :param name:
        :return:
        """
        assert len(name.split(" ")) < 2, "Ensure that you don't have spaces in your variable name, use '_' instead."
        name = "heatmap_" + name
        self.previous.append(name)
        if self.previous[-1] not in self.previous[:-1]:
            self.c.execute("""INSERT INTO {time_stamp_table} (
                              variable_name, variable_type
                              ) VALUES ('{variable}', '{type}')"""
                           .format(time_stamp_table=self.time_stamp, variable=name, type="heatmap"))
        else:
            self.previous.pop()

        if value_names is None:
            self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                              X_value FLOAT, Y_value ARRAY, time VARCHAR
                              )""".format(variable_table_name=self.time_stamp + '_' + name))

            self.c.execute("""INSERT INTO {variable_table_name} (
                              X_value, Y_value, time) VALUES (?, ?, ?
                              )""".format(variable_table_name=self.time_stamp + '_' + name),
                           (step, value, datetime.datetime.now()))
        else:
            self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                              X_value FLOAT, Y_value ARRAY, V_names ARRAY, time VARCHAR
                              )""".format(variable_table_name=self.time_stamp + '_' + name))

            self.c.execute("""INSERT INTO {variable_table_name} (
                              X_value, Y_value, V_names, time) VALUES (?, ?, ?, ?
                              )""".format(variable_table_name=self.time_stamp + '_' + name),
                                          (step, value, value_names, datetime.datetime.now()))

        self.conn.commit()

    def fft(self):
        pass
