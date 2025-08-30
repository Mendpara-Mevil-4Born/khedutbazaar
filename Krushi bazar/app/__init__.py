# Flask app initialization
from flask import Flask, render_template
from .config import Config
from .scraping.api import scraping_bp
from .data.api import data_bp
from .yard.api import yard_bp
from .automated_api import automated_bp
from .scheduler_api import scheduler_bp

from API.app.addtofavorite import addtofavorite_bp
from API.app.alerts import alerts_bp
from API.app.banner import banner_bp
from API.app.commodity_stats import commodity_stats_bp
from API.app.districtlist import districtlist_bp
from API.app.getAllFavorite import getAllFavorite_bp
from API.app.getCommodityBasedOnmarket import getCommodityBasedOnmarket_bp
from API.app.getcrop_data import getcrop_data_bp
from API.app.login import login_bp
from API.app.marketlist import marketlist_bp
from API.app.send_alert_notification import send_alert_notification_bp
from API.app.statelist import statelist_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(scraping_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(yard_bp)
    app.register_blueprint(automated_bp)
    app.register_blueprint(scheduler_bp)
    app.register_blueprint(addtofavorite_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(banner_bp)
    app.register_blueprint(commodity_stats_bp)
    app.register_blueprint(districtlist_bp)
    app.register_blueprint(getAllFavorite_bp)
    app.register_blueprint(getCommodityBasedOnmarket_bp)
    app.register_blueprint(getcrop_data_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(marketlist_bp)
    app.register_blueprint(send_alert_notification_bp)
    app.register_blueprint(statelist_bp)

    # Auto-start scheduler when app starts
    with app.app_context():
        try:
            from .scheduler import scheduler
            # Start scheduler automatically
            success = scheduler.start_scheduler()
            if success:
                print("[INFO]  Scheduler auto-started successfully")
                print(f"[INFO]  Will run daily at {scheduler.get_scheduler_status()['schedule_time']}")
                print(f"[INFO]   Scheduled states: {scheduler.get_scheduler_status()['scheduled_states']}")
            else:
                print("[WARNING]   Scheduler auto-start failed (may be disabled in config)")
        except Exception as e:
            print(f"[ERROR]  Failed to auto-start scheduler: {e}")

    # Home, about, contact, and API docs routes
    @app.route('/')
    def home():
        from .data.database import Database
        db = Database()
        try:
            stats = db.get_stats()
        except:
            stats = {'states': 0, 'districts': 0, 'markets': 0}
        return render_template('index.html', title='Khedut Bazaar', stats=stats)

    @app.route('/about')
    def about():
        return render_template('about.html', title='About - Khedut Bazaar')

    @app.route('/contact')
    def contact():
        return render_template('contact.html', title='Contact - Khedut Bazaar')

    @app.route('/api-docs')
    def api_docs():
        return render_template('api_docs.html', title='API Documentation - Khedut Bazaar')

    return app