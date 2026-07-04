from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import mail
from models.user import ensure_indexes
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}})

    mail.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    ensure_indexes()

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
