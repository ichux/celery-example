import os

import numpy as np
import pandas as pd
from celery import Celery, states
from flask import Flask, jsonify, request, make_response, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['CELERY_BROKER_URL'] = 'redis://:4376046362e3d3c9d407c2425809b6da@192.168.56.20:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:4376046362e3d3c9d407c2425809b6da@192.168.56.20:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

BASE_DIRECTORY = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))
UPLOADS = os.path.join(BASE_DIRECTORY, 'uploads')

# create a directory for uploads
if not os.path.exists(UPLOADS):
    try:
        os.mkdir(UPLOADS)
    except (Exception,):
        pass


@celery.task(bind=True)
def read_csv_task(self, path):
    self.update_state(state=states.PENDING)
    return compute_properties(pd.read_csv(path))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file_obj = request.files.get('file')
    file_name = file_obj.filename

    path = os.path.join(UPLOADS, file_name)
    file_obj.read(0)

    try:
        file_obj.save(path)
    except IOError:
        print('I/O Error')

    file_obj.close()
    file_task = read_csv_task.apply_async(args=[path])
    return make_response(jsonify({'task_id': file_task.task_id}))


@app.route('/task/<task_id>', methods=['GET'])
def check_task_status(task_id):
    task = read_csv_task.AsyncResult(task_id)
    state = task.state

    response = {'state': state}

    if state == states.SUCCESS:
        response['result'] = task.get()
    elif state == states.FAILURE:
        try:
            response['error'] = task.info.get('error')
        except (Exception,) as e:
            response['error'] = str(e)

    return make_response(jsonify(response))


def compute_properties(df):
    return {'num_rows': len(df), 'num_columns': len(df.columns), 'column_data': get_column_data(df)}


def get_column_data(df):
    result = []

    for c in df:
        info = {}
        col = df[c]

        info['name'] = c
        info['num_null'] = col.isnull().sum()

        # print(f'col.dtypes: {col.dtypes}')
        if col.dtypes == 'int64':
            info['mean'] = np.mean(col)
            info['median'] = np.median(col)
            info['stddev'] = np.std(col)
            info['min'] = col.min()
            info['max'] = col.max()
        else:
            unique_values = col.unique().tolist()
            print(len(unique_values), len(df))

            if len(unique_values) < len(df):
                info['unique_values'] = unique_values
            else:
                info['unique_values'] = True

        result.append(info)
    return result


if __name__ == '__main__':
    app.run(port=8889, debug=True)
