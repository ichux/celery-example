from server import celery, app

if __name__ == '__main__':
    with app.app_context():
        # '-c = concurrency'
        argv = ['celery', 'worker', '-l', 'info', '-c', '5', '-n', 'uploads.%h']
        celery.start(argv)
