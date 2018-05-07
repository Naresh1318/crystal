import crystal
import numpy as np
import time
import os
import sqlite3
from crystal import sql_table_utils

# # Testing Crystal.py
# cr = crystal.Crystal()
# a = np.arange(0, 10000, 0.1)
#
# for i in a:
#     cr.scalar(i**2, i, "pow")
#     print(i)
#     time.sleep(1)
#
# print("Done!")

# # Testing sql_table_utils.py
# home_dir = os.path.expanduser("~")
# main_data_dir = home_dir + "/Crystal_data"
# database_name = "/crystal.db"
# conn = sqlite3.connect(main_data_dir + database_name)
# sql_table_utils.drop_project("tests", conn)

# Testing get_project
import crystal.sql_table_utils as utils
from flask import Flask, render_template, jsonify
projects = utils.get_projects()
print(projects)

