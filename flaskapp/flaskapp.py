"""Dispatching logic to multiple blueprints."""

from flask_migrate import Migrate

from apis import blueprint as api
from user_account.views import user_account_pages

from setup import app, db, mail, login_manager

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(user_account_pages, url_prefix='/home')

db.init_app(app)
migrate = Migrate(app, db)
mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "user_account_pages.login"

if __name__ == '__main__':
    app.run()
