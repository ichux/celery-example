import mimetypes

import requests


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def load_file(file_location="/Users/ichux/PycharmProjects/gcore/Mar-2017.csv"):
    file_bytes = open(file_location, 'rb').read()

    payload = '------DataBoundary\r\n'
    payload += 'Content-Disposition: form-data; name="file"; filename="Mar-2017.csv"\r\n'
    payload += f'Content-Type: {get_content_type(filename=file_location)}\r\n\r\n'
    payload += f'{file_bytes}\r\n'
    payload += '------DataBoundary--'

    headers = {
        'content-type': "multipart/form-data; boundary=----DataBoundary",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0",
        'accept': "*/*", 'accept-language': "en-GB,en;q=0.5",
        'accept-encoding': "gzip, deflate", 'connection': "keep-alive"
    }

    response = requests.post("http://localhost:8889/upload", data=payload, headers=headers)
    return response.json().get("task_id")


def ask_status(task_id):
    response = requests.get(f"http://localhost:8889/task/{task_id}")
    print(response.json())


if __name__ == '__main__':
    print(load_file())
    print(ask_status("02d764ad-c465-4220-b7eb-218995b3ce07"))
