from flask import Flask, redirect, render_template
from routes import router
import threading, time

app = Flask(__name__)
app.register_blueprint(router, url_prefix='/')

@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html')

StartTime=time.time()
def action() :
    print('action ! -> time : {:.1f}s'.format(time.time()-StartTime))
    

if __name__ == '__main__':
    app.run(debug=True)
