import requests


def load_file(file_location="/Users/ichux/PycharmProjects/gcore/Mar-2017.csv"):
    file_bytes = open(file_location, 'rb').read()

    url = "http://localhost:8889/upload"
    payload = "------DataBoundary\r\n"
    payload += "Content-Disposition: form-data; name=\"file\"; filename=\"Mar-2017.csv\"\r\n"
    payload += "Content-Type: text/csv\r\n\r\n"
    payload += '%s\r\n' % file_bytes
    payload += "------DataBoundary--"

    headers = {
        'content-type': "multipart/form-data; boundary=----DataBoundary",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) Gecko/20100101 Firefox/46.0",
        'accept': "*/*",
        'accept-language': "en-GB,en;q=0.5",
        'accept-encoding': "gzip, deflate",
        'connection': "keep-alive"
    }

    # print(repr(payload))
    response = requests.post(url, data=payload, headers=headers)
    return response.json().get("task_id")


def ask_status(task_id):
    response = requests.get(f"http://localhost:8889/task/{task_id}")
    print(response.json())


if __name__ == '__main__':
    # print(load_file())
    print(ask_status("10b5c2e7-f874-4928-8768-8cd7c41c2951"))
