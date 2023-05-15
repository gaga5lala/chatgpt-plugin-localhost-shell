from flask import Flask, request
import subprocess
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
work_dir = os.path.expanduser('~')  # initial working directory

# Load the blacklist from a file
with open('blacklist.txt', 'r') as f:
    blacklist = [line.strip() for line in f]


def is_blacklisted(command):
    return any(blacklisted in command.split() for blacklisted in blacklist)


cors = CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})

@app.route('/openapi.yaml')
def openapi_yaml():
    return send_from_directory(app.static_folder, 'openapi.yaml')

@app.route('/logo.png')
def logo_png():
    return send_from_directory(app.static_folder, 'logo.png')

@app.route('/.well-known/ai-plugin.json')
def manifest_json():
    return send_from_directory(app.static_folder, '.well-known/ai-plugin.json')

@app.route('/execute', methods=['POST'])
def execute():
    global work_dir
    command = request.json['command']

    if is_blacklisted(command):
        return {"error": "This command is blacklisted."}, 400

    if command.startswith('cd '):
        path = command.split(' ', 1)[1]
        path = os.path.expanduser(path)  # Expand ~ to the actual home directory path
        new_work_dir = os.path.join(work_dir, path) if not path.startswith('/') else path
        if os.path.exists(new_work_dir) and os.path.isdir(new_work_dir):
            work_dir = new_work_dir
            output = ''
            error = ''
            exit_code = 0
        else:
            output = ''
            error = f"No such file or directory: {new_work_dir}"
            exit_code = 1
    else:
        result = subprocess.run(command, shell=True, cwd=work_dir, capture_output=True, text=True)
        output = result.stdout
        error = result.stderr
        exit_code = result.returncode

    with open('log.txt', 'a') as f:
        f.write(f"Command: {command}\nOutput: {output}\nError: {error}\nExit code: {exit_code}\n")

    return {"output": output, "error": error, "exit_code": exit_code}, 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
