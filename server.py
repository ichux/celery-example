import os
from flask import Flask, url_for, jsonify, request, make_response
from celery import Celery, states
from flask_cors import CORS, cross_origin

import numpy as np
import pandas as pd

import logging
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app)

app.config['CELERY_BROKER_URL'] = 'amqp://admin:password@localhost/test'
# app.config['CELERY_RESULT_BACKEND'] = 'amqp://localhost:5672/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/upload', methods=['POST'])
def get_csv_info():
    file_obj = request.files.get('file')
    file_name = file_obj.filename

    path = os.path.join('./uploads', file_name)

    file_obj.read(0)

    try:
        file_obj.save(path)
    except IOError:
        print 'I/O Error'

    file_obj.close()

    file_task = csv_info_task.apply_async(args=[path])

    return make_response(jsonify({'task_id': file_task.task_id}))



# Celery tasks
@celery.task(bind=True)
def csv_info_task(self, path):

    #read csv
    self.update_state(state=states.PENDING, meta={'desc': 'Computing dataset properties'})

    df = pd.read_csv(path)
    result = compute_properties(df)
    
    return result

def compute_properties(df):
    properties = {}

    properties['num_rows'] = len(df)
    properties['num_columns'] = len(df.columns)

    properties['column_data'] = compute_column_data(df)

    print properties

    return properties

def compute_column_data(df):
    result = []

    for c in df:
        info = {}
        col = df[c]

        info['name'] = c
        info['num_null'] = col.isnull().sum()

        if col.dtypes == 'int64':
            info['mean'] = np.mean(col)
            info['median'] = np.median(col)
            info['stddev'] = np.std(col)
            info['min'] = col.min()
            info['max'] = col.max()

        result.append(info)

    return result

if __name__ == '__main__':
    app.run(port=8889, debug=True)

