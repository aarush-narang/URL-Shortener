from flask import Flask, render_template
from routes import router
import os
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='VDRjuh9aEMa8LvLaz5GhtZVqYVybdyF7VGPQU2Ev'
)

csrf = CSRFProtect()
csrf.init_app(app)

app.register_blueprint(router, url_prefix='/')

@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(host=os.getenv('DOMAIN'), port=os.getenv('PORT'), ssl_context=('cert.pem', 'key.pem')) # certificates for https
