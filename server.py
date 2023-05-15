from flask import Flask, request
import subprocess
import os

app = Flask(__name__)
work_dir = os.path.expanduser('~')  # initial working directory

# Load the blacklist from a file
with open('blacklist.txt', 'r') as f:
    blacklist = [line.strip() for line in f]


def is_blacklisted(command):
    return any(blacklisted in command.split() for blacklisted in blacklist)


@app.route('/execute', methods=['POST'])
def execute():
    global work_dir
    command = request.json['command']

    if is_blacklisted(command):
        return {"error": "This command is blacklisted."}, 400

    if command.startswith('cd '):
        path = command.split(' ', 1)[1]
        if path.startswith('/'):
            work_dir = path
        else:
            work_dir = os.path.join(work_dir, path)
        output = ''
        error = ''
    else:
        result = subprocess.run(command, shell=True, cwd=work_dir, capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

    with open('log.txt', 'a') as f:
        f.write(f"Command: {command}\nOutput: {output}\nError: {error}\n")

    return {"output": output, "error": error}, 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)