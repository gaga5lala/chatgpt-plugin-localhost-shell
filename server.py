from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/ls')
def list_files():
    result = subprocess.run(['ls', '-al'], capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    app.run()
