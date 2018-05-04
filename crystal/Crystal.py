import os
import sqlite3
import datetime
import numpy as np


def get_time_stamp(path):
    """
    Gets the timestamp from the provided path.
    :param path: String, the complete path where data is stored for the run.
    :return: String, extracted timestamp
    """
    for i in path.split("/"):
        if "Time_" in i:
            # Remove all the invalid chars for SQL table names
            i = i.replace("-", "_").replace(":", "_").replace(" ", "_").replace(".", "_")
            return i
    raise ValueError('Not able to find the data directory, make sure that the File starts with Time')


class NeuroViz:
    """
    Provides methods to store various types of data onto the database.
    """
    def __init__(self, project_name, file_path):
        self.project_name = project_name
        self.file_path = file_path
        self.time_stamp = get_time_stamp(self.file_path)
        self.previous = [None]

        # Create a new database on the home directory
        home_dir = os.path.expanduser("~")
        main_data_dir = home_dir + "/NeuroViz_data"
        database_name = "/neuroviz_test.db"
        if not os.path.exists(main_data_dir):
            os.mkdir(main_data_dir)

        self.conn = sqlite3.connect(main_data_dir + database_name)
        self.c = self.conn.cursor()
        self.run_table_name = self.project_name+'_'+'run_table'
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

        if not self.project_name in project_names:
            self.c.execute("""INSERT INTO main_table (
                              project_name) VALUES ('{}'
                              )""".format(self.project_name))

        # run_table
        self.c.execute("""SELECT run_name FROM {run_table}""".format(run_table=self.run_table_name))
        run_names = np.array(self.c.fetchall()).squeeze()

        if not self.time_stamp in run_names:
            self.c.execute("""INSERT INTO {} (
                              run_name) VALUES ('{}'
                              )""".format(self.run_table_name, self.time_stamp))

        # variable_table -> time_stamp_table
        self.c.execute("""CREATE TABLE IF NOT EXISTS {} (
                          variable_name VARCHAR, variable_type VARCHAR
                          )""".format(self.time_stamp))

    def scalar(self, value, step, name):
        """
        Plot a scalar value.
        :param value: int or float, must be numpy arrays, Scalar -> [1], the value on the y-axis
        :param step: int or float, the value on the x-axis
        :param name: String, the name of the variable to be used during visualization
        """
        self.previous.append(name)
        if self.previous[-1] not in self.previous[:-1]:
            self.c.execute("""INSERT INTO {time_stamp_table} (
                              variable_name, variable_type
                              ) VALUES ('{variable}', '{type}')"""
                           .format(time_stamp_table=self.time_stamp, variable=name, type="scalar"))

        self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                          X_value FLOAT, Y_value FLOAT, time VARCHAR
                          )""".format(variable_table_name=self.time_stamp + '_' + name))

        self.c.execute("""INSERT INTO {variable_table_name} (
                          X_value, Y_value, time) VALUES ('{x}', '{y}', '{time}'
                          )""".format(variable_table_name=self.time_stamp + '_' + name,
                                      x=step, y=value, time=datetime.datetime.now()))
        self.conn.commit()

    def image(self, image, name):
        """
        Show image on the NeuroViz server.
        :param image:
        :param name:
        :return:
        """
        self.previous.append(name)
        if self.previous[-1] not in self.previous[:-1]:
            self.c.execute("""INSERT INTO {time_stamp_table} (
                              variable_name, variable_type
                              ) VALUES ('{variable}', '{type}')"""
                           .format(time_stamp_table=self.time_stamp, variable=name, type="image"))

        self.c.execute("""CREATE TABLE IF NOT EXISTS {variable_table_name} (
                          images BLOB, time VARCHAR
                          )""".format(variable_table_name=self.time_stamp + '_' + name))

        self.c.execute("""INSERT INTO {variable_table_name} (
                          images, time) VALUES ('{img}', '{time}'
                          )""".format(variable_table_name=self.time_stamp + '_' + name,
                                      img=sqlite3.Binary(np.array(image).tobytes()), time=datetime.datetime.now()))
        self.conn.commit()

    def histogram(self):
        pass

    def fft(self):
        pass
