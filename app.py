import config
from api_routes import register_routes
from blueprints.main_bp import main_bp
from commands import init_command
from extensions import db, cors, jwt_manager, redis_client
from flask import Flask
from flask_migrate import Migrate
from models.result import Result

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
cors.init_app(app)
jwt_manager.init_app(app)
redis_client.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp, url_prefix='')
register_routes(app)
init_command(app)


@app.errorhandler(Exception)
def handle_global_error(e):
    print(e)
    return Result.error(str(e))  # TODO: remove str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
