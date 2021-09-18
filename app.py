from dotenv import load_dotenv
load_dotenv()
from flask import Flask, redirect
from routes import router

app = Flask(__name__)
app.register_blueprint(router, url_prefix='/')

@app.errorhandler(404)
def pagenotfound(e):
    return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)
