from flask import Flask
import os
from dotenv import load_dotenv
from pprint import pprint
app = Flask(__name__)


load_dotenv()
VERBWIRE_API_KEY = os.getenv("VERBWIRE_API_KEY")
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
