from flask import Flask, request
from markdown import markdown

app = Flask(__name__)

host = '0.0.0.0'
port = 8888

@app.route('/convert', methods=['POST'])
def convert():
    text = request.form['text']
    html = markdown(text)
    print(request.method)
    return html

if __name__ == '__main__':
    app.run(debug=True)
