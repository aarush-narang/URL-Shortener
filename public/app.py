from flask import Flask, render_template
from routes import account_routes, main_routes, url_shorten_routes
import os
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

csrf = CSRFProtect()
csrf.init_app(app)

app.register_blueprint(account_routes.account_router, url_prefix='/')
app.register_blueprint(main_routes.main_router, url_prefix='/')
app.register_blueprint(url_shorten_routes.url_shorten_router, url_prefix='/')

@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(host=os.getenv('DOMAIN'), port=os.getenv('PORT'), ssl_context=('../cert.pem', '../key.pem'), debug=True) # certificates for https