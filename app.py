from flask import Flask, render_template
from routes import router
import os

app = Flask(__name__)
app.register_blueprint(router, url_prefix='/')

@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(host=os.getenv('DOMAIN'), port=os.getenv('PORT'), debug=True)
