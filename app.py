import os
from flask import Flask, render_template, send_from_directory
from database.db import init_db, get_all_teachers, seed_default_data
from api.routes import api_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Initialize DB
    init_db()
    
    # Seed default data if database is empty
    teachers = get_all_teachers()
    if not teachers:
        seed_default_data()
        print("[SlotSync] Initialized demo college dataset.")

    # Register Blueprints
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return {"status": "ok", "app": "SlotSync Timetable Generator"}

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"[SlotSync] Server running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
