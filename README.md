# REST-API-example
A simple example of implementing the REST API concept in Python using the fast API library

# What is realized

An algorithm with two methods is written:

1. A method accepting files (image or video) that returns UUID, size and mime type
2. A method that accepts the generated UUID and works depending on the parameters as follows:
  - If length and width are passed, it makes a thumbnail of the image and a thumbnail of the first frame for the video
  - If no parameters are passed, it returns the original image or the first frame

# How to run 

The instructions are for GNU/Linux, but you can also do this on macOS / Windows if you wish. 

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip3 install fastapi`
4. `sudo apt-get install ffmpeg`
5. `fastapi dev main.py`

## Examples of get-requests with curl

- `curl -X "http:127.0.0.1:8000/api/files/" -F file=@<file_name>`
- `curl -X PUT "http:127.0.0.1:8000/api/files/<UUID>" --output <file_name>`
- `curl -X PUT "http://127.0.0.1:8000/api/files/<UUID>?length=<some_value>&width=<some_value>" --output <file_name>`
