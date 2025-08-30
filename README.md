# Khedut Bazaar - Complete Project Documentation

A comprehensive agricultural marketplace system that provides commodity price data from Agriplus.in. The project consists of three main components: a production API server, language translation utilities, and scraping logic modules.

## 📁 Project Structure Overview

```
KhedutBazaar/
├── Krushi bazar/                    # Production API Server
├── language translate logic/         # Language Translation Utilities  
└── scrapeing-logics/                # Scraping Logic & Development
```

---

## 🚀 Krushi bazar/ - Production API Server

**Purpose**: Main production Flask API server with automated scraping, scheduling, and comprehensive API endpoints.

### 📊 Current Statistics
- **States**: 36
- **Districts**: 708  
- **Markets**: 4840
- **Commodities**: 1068+

### 🌐 Live Server
- **Production URL**: https://khedut-bazaar-py.4born.com/
- **Local Development**: http://localhost:1136

### 📁 Folder Structure
```
Krushi bazar/
├── app/
│   ├── __init__.py                  # Flask app initialization
│   ├── config.py                    # Configuration settings
│   ├── automated_api.py             # Automated scraping API endpoints
│   ├── automated_scraper.py         # Automated scraping logic
│   ├── scheduler.py                 # Automated scheduler (runs daily at 9 PM)
│   ├── scheduler_api.py             # Scheduler management API
│   ├── data/                        # Database operations
│   ├── scraping/                    # Web scraping modules
│   ├── yard/                        # Commodity price data
│   ├── static/                      # CSS and static files
│   └── templates/                   # HTML templates
├── API/
│   ├── db_connect.py                # Database connection
│   └── app/                         # Additional API modules
│       ├── addtofavorite.py         # Add to favorites functionality
│       ├── alerts.py                # Alert system
│       ├── banner.py                # Banner management
│       ├── commodity_stats.py       # Commodity statistics
│       ├── districtlist.py          # District listing API
│       ├── getAllFavorite.py        # Get all favorites
│       ├── getCommodityBasedOnmarket.py # Market-based commodity data
│       ├── getcrop_data.py          # Crop data retrieval
│       ├── login.py                 # User authentication
│       ├── marketlist.py            # Market listing API
│       ├── send_alert_notification.py # Alert notifications
│       └── statelist.py             # State listing API
├── app.py                           # Main application entry point
├── requirements.txt                 # Python dependencies
├── scraping_config.json             # Scheduler configuration
└── README.md                        # Detailed API documentation
```

### 🛠️ Installation & Setup

```bash
# Clone and setup
cd "Krushi bazar"
pip install -r requirements.txt

# Configure database in app/config.py
# Run the application
python app.py
```

### 📡 API Endpoints

#### Health Check
```bash
# Local
curl -X GET http://localhost:1136/api/database/health

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/health
```

#### Database Statistics
```bash
# Local
curl -X GET http://localhost:1136/api/database/stats

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/stats
```

#### Get All States
```bash
# Local
curl -X GET http://localhost:1136/api/database/states

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/states
```

#### Get Districts by State
```bash
# Local
curl -X POST http://localhost:1136/api/database/states/district \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11}'

# Production
curl -X POST https://khedut-bazaar-py.4born.com/api/database/states/district \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11}'
```

#### Get Markets by State and District
```bash
# Local
curl -X POST http://localhost:1136/api/database/states/district/markets \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11, "district_id": 162}'

# Production
curl -X POST https://khedut-bazaar-py.4born.com/api/database/states/district/markets \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11, "district_id": 162}'
```

#### Search Locations
```bash
# Local
curl -X GET "http://localhost:1136/api/database/search?q=vadodara"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/api/database/search?q=vadodara"
```

#### Get Commodity Prices (Yard Data)
```bash
# Get all commodity prices
curl -X GET "http://localhost:1136/api/database/yard"

# Get prices for specific state
curl -X GET "http://localhost:1136/api/database/yard?state_id=11"

# Get prices for specific state and district
curl -X GET "http://localhost:1136/api/database/yard?state_id=11&district_id=162"

# Get prices for specific market
curl -X GET "http://localhost:1136/api/database/yard?state_id=11&district_id=162&market_id=1234"
```

### 🔄 Scraping Endpoints

#### Scrape States Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/states

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/states
```

#### Scrape Districts Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/districts

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/districts
```

#### Scrape Markets Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/markets

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/markets
```

#### Scrape Markets for Specific State
```bash
# Local
curl -X GET http://localhost:1136/scrape/markets/11

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/markets/11
```

#### Scrape Yard Data (Commodity Prices)
```bash
# District-level data
curl -X GET "http://localhost:1136/scrape/yard?state_id=11&district_id=162"

# Market-level data
curl -X GET "http://localhost:1136/scrape/yard?state_id=11&district_id=162&market_id=1234"
```

### 🤖 Automated Scraping Endpoints

#### Automated District Scraping
```bash
# Local
curl -X GET "http://localhost:1136/automated/scrape/district/162"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/scrape/district/162"
```

#### Automated State Scraping
```bash
# Local
curl -X GET "http://localhost:1136/automated/scrape/state/11"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/scrape/state/11"
```

#### Get Automated Scraping Status
```bash
# Local
curl -X GET "http://localhost:1136/automated/status"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/status"
```

#### Bulk Scraping
```bash
# Local
curl -X POST "http://localhost:1136/automated/scrape/bulk" \
  -H "Content-Type: application/json" \
  -d '{"district_ids": [162, 163, 164]}'

# Production
curl -X POST "https://khedut-bazaar-py.4born.com/automated/scrape/bulk" \
  -H "Content-Type: application/json" \
  -d '{"district_ids": [162, 163, 164]}'
```

### ⏰ Automated Scheduler

#### Scheduler Management
```bash
# Start the scheduler (runs daily at 9 PM)
curl -X POST "http://localhost:1136/scheduler/start"

# Stop the scheduler
curl -X POST "http://localhost:1136/scheduler/stop"

# Get scheduler status
curl -X GET "http://localhost:1136/scheduler/status"

# Run scheduled scraping immediately
curl -X POST "http://localhost:1136/scheduler/run-now"
```

#### Schedule Management
```bash
# Add state to schedule
curl -X POST "http://localhost:1136/scheduler/add-state" \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11}'

# Remove state from schedule
curl -X POST "http://localhost:1136/scheduler/remove-state" \
  -H "Content-Type: application/json" \
  -d '{"state_id": 11}'

# Get scheduled items
curl -X GET "http://localhost:1136/scheduler/scheduled-items"
```

### 🗄️ Database Schema

#### States Table
```sql
CREATE TABLE states (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Districts Table
```sql
CREATE TABLE districts (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states (id)
);
```

#### Markets Table
```sql
CREATE TABLE markets (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district_id INT NOT NULL,
    state_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts (id),
    FOREIGN KEY (state_id) REFERENCES states (id)
);
```

#### Commodity Prices Table
```sql
CREATE TABLE commodity_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state_id INT NOT NULL,
    district_id INT NOT NULL,
    market_id INT NOT NULL,
    commodity VARCHAR(100) NOT NULL,
    variety VARCHAR(100) NOT NULL,
    min_price INT NOT NULL,
    max_price INT NOT NULL,
    modal_price INT NOT NULL,
    price_date VARCHAR(50) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states (id),
    FOREIGN KEY (district_id) REFERENCES districts (id),
    FOREIGN KEY (market_id) REFERENCES markets (id),
    UNIQUE KEY unique_price (state_id, district_id, market_id, commodity, variety, price_date)
);
```

---

## 🌐 language translate logic/ - Language Translation Utilities

**Purpose**: Provides language translation capabilities for the Khedut Bazaar API data, supporting multiple languages including Hindi and Gujarati.

### 📁 Folder Structure
```
language translate logic/
├── google-translater.py             # Async Google Translate implementation
├── python module-translator.py      # Deep Translator module implementation
└── translated_markets_async.json    # Translated market data output
```

### 🔧 Translation Methods

#### 1. Google Translate (Async)
```python
# google-translater.py
# Uses Google Translate unofficial API with async processing
# Supports multiple languages: Hindi (hi), Gujarati (gu), etc.

# Usage:
python google-translater.py
```

**Features:**
- Async processing for better performance
- Handles multiple fields (market_name, district_name, state_name)
- Error handling and fallback to original text
- Outputs to JSON file

#### 2. Deep Translator Module
```python
# python module-translator.py
# Uses deep_translator library for translation

# Usage:
python "python module-translator.py"
```

**Features:**
- Stream processing for large datasets
- Real-time translation output
- Error handling for individual items
- Supports multiple target languages

### 📡 API Integration

#### Fetch and Translate Market Data
```bash
# The translation scripts fetch data from:
curl -X POST https://khedut-bazaar.4born.com/API/marketlist.php \
  -H "Content-Type: application/json" \
  -d '{"userid": "1", "stateid": 11}'
```

#### Translation Configuration
```python
# Supported languages:
target_lang = "hi"  # Hindi
target_lang = "gu"  # Gujarati
target_lang = "mr"  # Marathi
target_lang = "bn"  # Bengali
# ... and more
```

### 📊 Output Format
```json
{
  "market_name": "Translated Market Name",
  "district_name": "Translated District Name", 
  "state_name": "Translated State Name",
  "original_data": "..."
}
```

---

## 🔍 scrapeing-logics/ - Scraping Logic & Development

**Purpose**: Development and testing environment for web scraping logic, database operations, and API development. This folder contains the foundational scraping logic that was later integrated into the production server.

### 📁 Folder Structure
```
scrapeing-logics/
├── app.py                           # Main Flask application
├── api.py                           # API blueprint and endpoints
├── database.py                      # Database operations
├── scraper.py                       # Basic scraper implementation
├── corrected_scraper.py             # Corrected scraper with improvements
├── dynamic_scraper.py               # Dynamic web scraping
├── db_config.py                     # Database configuration
├── check_db.py                      # Database health checks
├── create_khedut_bazaar_structure.py # Database structure creation
├── config.txt                       # Database configuration file
├── requirements.txt                 # Python dependencies
├── curl_commands.md                 # Complete curl command reference
├── README.md                        # Detailed documentation
├── scraping/                        # HTML files for scraping
│   ├── main.html                    # States data
│   ├── after_state.html             # Districts data
│   └── after_market.html            # Markets data
└── templates/                       # HTML templates
    ├── index.html                   # Home page
    ├── about.html                   # About page
    ├── contact.html                 # Contact page
    └── api_docs.html                # API documentation
```

### 🛠️ Installation & Setup

```bash
# Clone and setup
cd scrapeing-logics
pip install -r requirements.txt

# Configure database in config.txt
# Create MySQL database
mysql -u root -p -e "CREATE DATABASE khedutbazaar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run the application
python app.py
```

### 📡 API Endpoints

#### Health Check
```bash
curl http://localhost:1136/api/health
```

#### Database Statistics
```bash
curl http://localhost:1136/api/stats
```

#### Get All States
```bash
curl http://localhost:1136/api/states
```

#### Get Districts by State
```bash
curl http://localhost:1136/api/states/11/districts
```

#### Get Markets by State and District
```bash
curl http://localhost:1136/api/states/11/districts/1/markets
```

#### Get Markets by District Only
```bash
curl http://localhost:1136/api/districts/1/markets
```

#### Search Locations
```bash
curl "http://localhost:1136/api/search?q=gujarat"
```

### 🔄 Scraping Endpoints

#### Scrape States Only
```bash
curl http://localhost:1136/scrape/states
```

#### Scrape Districts Only
```bash
curl http://localhost:1136/scrape/districts
```

#### Scrape Markets Only
```bash
curl http://localhost:1136/scrape/markets
```

#### Scrape Markets by State
```bash
curl http://localhost:1136/scrape/markets/11
```

#### Scrape All Data (Legacy)
```bash
curl http://localhost:1136/scrape
```

### 🗄️ Database Configuration

#### config.txt Format
```
db:-khedutbazaar
user:-root  
password:-SorathiyaRooT@123
host:-localhost
```

#### Database Schema
```sql
-- States Table
CREATE TABLE states (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Districts Table
CREATE TABLE districts (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE,
    UNIQUE KEY unique_district_state (name, state_id)
);

-- Markets Table
CREATE TABLE markets (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district_id INT NOT NULL,
    state_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE CASCADE,
    FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE,
    UNIQUE KEY unique_market_district (name, district_id)
);
```

### 🔄 Complete Workflow Examples

#### 1. Initial Setup and Data Population
```bash
# 1. Start the server
python app.py

# 2. Check health
curl http://localhost:1136/api/health

# 3. Scrape states first
curl http://localhost:1136/scrape/states

# 4. Scrape districts
curl http://localhost:1136/scrape/districts

# 5. Scrape markets
curl http://localhost:1136/scrape/markets

# 6. Check final statistics
curl http://localhost:1136/api/stats
```

#### 2. Update Specific Data Types
```bash
# Update only states
curl http://localhost:1136/scrape/states

# Update only districts
curl http://localhost:1136/scrape/districts

# Update only markets
curl http://localhost:1136/scrape/markets
```

### 🛡️ Error Handling

The system includes comprehensive error handling:
- Database connection errors
- Missing HTML files
- API endpoint validation
- Proper HTTP status codes
- Detailed logging

---

## 🔗 Key Differences Between Components

| Feature | Krushi bazar | scrapeing-logics | language translate logic |
|---------|-------------|------------------|-------------------------|
| **Purpose** | Production API Server | Development/Testing | Language Translation |
| **Database** | MySQL with advanced features | MySQL basic setup | No database |
| **Scraping** | Automated + Scheduled | Manual + Selective | N/A |
| **API Endpoints** | Comprehensive (20+ endpoints) | Basic (8 endpoints) | Translation utilities |
| **Scheduler** | Built-in automated scheduler | Manual scraping only | N/A |
| **Commodity Data** | Full commodity price tracking | Location data only | N/A |
| **Production Ready** | ✅ Yes | ❌ Development only | ✅ Translation ready |

---

## 🚀 Quick Start Guide

### 1. Production Setup (Recommended)
```bash
cd "Krushi bazar"
pip install -r requirements.txt
python app.py
```

### 2. Development Setup
```bash
cd scrapeing-logics
pip install -r requirements.txt
python app.py
```

### 3. Translation Setup
```bash
cd "language translate logic"
python google-translater.py
```

---

## 📞 Support & Links

- **Live Website**: https://khedut-bazaar-py.4born.com/
- **Source Data**: https://agriplus.in/prices/all
- **API Health**: https://khedut-bazaar-py.4born.com/api/database/health
- **Production API**: https://khedut-bazaar-py.4born.com/api/database/states

---

## 📝 License

This project is licensed under the MIT License.

---

© 2025 Khedut Bazaar. All rights reserved.
#   k h e d u t b a z a a r  
 