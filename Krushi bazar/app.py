# Entry point to run the Flask app
from app import create_app

if __name__ == "__main__":
    app = create_app()
    print(f"Starting Khedut Bazaar server on port {app.config['PORT']}")
    print(f"Live link: http://khedut-bazaar-py.4born.com/")
    print(f"Health check: http://{app.config['HOST']}:{app.config['PORT']}/api/database/health")
    print(f"API endpoints:")
    print(f"  - States: http://{app.config['HOST']}:{app.config['PORT']}/api/database/states")
    print(f"  - Districts: http://{app.config['HOST']}:{app.config['PORT']}/api/database/states/district")
    print(f"  - Markets: http://{app.config['HOST']}:{app.config['PORT']}/api/database/states/district/markets")
    print(f"  - Stats: http://{app.config['HOST']}:{app.config['PORT']}/api/database/stats")
    print(f"Scraping endpoints:")
    print(f"  - States: http://{app.config['HOST']}:{app.config['PORT']}/scrape/states")
    print(f"  - Districts: http://{app.config['HOST']}:{app.config['PORT']}/scrape/districts")
    print(f"  - Markets: http://{app.config['HOST']}:{app.config['PORT']}/scrape/markets")
    print(f"  - Markets by State: http://{app.config['HOST']}:{app.config['PORT']}/scrape/markets/<state_id>")
    print(f"  - Yard Data: http://{app.config['HOST']}:{app.config['PORT']}/scrape/yard?state_id=<state_id>&district_id=<district_id>[&market_id=<market_id>]")
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=False)