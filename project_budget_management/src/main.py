from flask import Flask
from dashboard import create_dashboard

app = Flask(__name__)
create_dashboard(app)

if __name__ == '__main__':
    app.run(debug=True)
