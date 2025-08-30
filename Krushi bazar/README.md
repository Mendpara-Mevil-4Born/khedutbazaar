# Khedut Bazaar API

A comprehensive agricultural marketplace API that scrapes and provides commodity price data from Agriplus.in. The system manages states, districts, markets, and commodity prices with automatic data synchronization.

## 🌐 Live Server
- **Production URL**: https://khedut-bazaar-py.4born.com/
- **Local Development**: http://localhost:1136

## 📊 Current Statistics
- **States**: 36
- **Districts**: 708  
- **Markets**: 4840
- **Commodities**: 1068+

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- Required packages (see requirements.txt)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd khedut_bazaar

# Install dependencies
pip install -r requirements.txt

# Configure database in app/config.py
# Run the application
python app.py
```

## 📚 API Documentation

### Base URLs
- **Local**: `http://localhost:1136`
- **Production**: `https://khedut-bazaar-py.4born.com`

### Health Check
```bash
# Local
curl -X GET http://localhost:1136/api/database/health

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Khedut Bazaar API",
  "version": "1.0.0",
  "timestamp": "2025-08-05T12:24:19.123456",
  "endpoints": {
    "states": "/api/database/states",
    "districts": "/api/database/states/district",
    "markets": "/api/database/states/district/markets",
    "stats": "/api/database/stats",
    "search": "/api/database/search",
    "yard": "/api/database/yard"
  }
}
```

### Database Statistics
```bash
# Local
curl -X GET http://localhost:1136/api/database/stats

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/stats
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "states": 36,
    "districts": 708,
    "markets": 4840,
    "commodities": 1068
  },
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Get All States
```bash
# Local
curl -X GET http://localhost:1136/api/database/states

# Production
curl -X GET https://khedut-bazaar-py.4born.com/api/database/states
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 11,
      "name": "Gujarat"
    },
    {
      "id": 12,
      "name": "Maharashtra"
    }
  ],
  "count": 36,
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Get Districts by State
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

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 162,
      "name": "Vadodara(Baroda)"
    },
    {
      "id": 163,
      "name": "Ahmedabad"
    }
  ],
  "count": 33,
  "state_id": 11,
  "state_name": "Gujarat",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Get Markets by State and District
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

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1234,
      "name": "Padra"
    },
    {
      "id": 1235,
      "name": "Savli"
    }
  ],
  "count": 15,
  "state_id": 11,
  "state_name": "Gujarat",
  "district_id": 162,
  "district_name": "Vadodara(Baroda)",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Search Locations
```bash
# Local
curl -X GET "http://localhost:1136/api/database/search?q=vadodara"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/api/database/search?q=vadodara"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "states": [],
    "districts": [
      {
        "id": 162,
        "name": "Vadodara(Baroda)",
        "state_id": 11,
        "state_name": "Gujarat"
      }
    ],
    "markets": [
      {
        "id": 1234,
        "name": "Padra",
        "district_id": 162,
        "state_id": 11,
        "district_name": "Vadodara(Baroda)",
        "state_name": "Gujarat"
      }
    ]
  },
  "query": "vadodara",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Get Commodity Prices (Yard Data)
```bash
# Get all commodity prices
curl -X GET "http://localhost:1136/api/database/yard"

# Get prices for specific state
curl -X GET "http://localhost:1136/api/database/yard?state_id=11"

# Get prices for specific state and district
curl -X GET "http://localhost:1136/api/database/yard?state_id=11&district_id=162"

# Get prices for specific market
curl -X GET "http://localhost:1136/api/database/yard?state_id=11&district_id=162&market_id=1234"

# Production URLs
curl -X GET "https://khedut-bazaar-py.4born.com/api/database/yard?state_id=11&district_id=162"
```

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 25 commodity price records",
  "data": [
    {
      "id": 1,
      "state_name": "Gujarat",
      "district_name": "Vadodara(Baroda)",
      "market_name": "Padra",
      "commodity": "Bhindi(Ladies Finger)",
      "variety": "Other",
      "min_price": 1750,
      "max_price": 2750,
      "modal_price": 2250,
      "price_date": "5 Aug",
      "state_id": 11,
      "district_id": 162,
      "market_id": 1234,
      "last_updated": "2025-08-05T12:24:19.123456",
      "created_at": "2025-08-05T10:00:00.000000"
    }
  ],
  "count": 25,
  "state_id": 11,
  "district_id": 162,
  "market_id": null,
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

## 🔄 Scraping Endpoints

### Scrape States Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/states

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/states
```

### Scrape Districts Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/districts

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/districts
```

### Scrape Markets Data
```bash
# Local
curl -X GET http://localhost:1136/scrape/markets

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/markets
```

### Scrape Markets for Specific State
```bash
# Local
curl -X GET http://localhost:1136/scrape/markets/11

# Production
curl -X GET https://khedut-bazaar-py.4born.com/scrape/markets/11
```

### Scrape Yard Data (Commodity Prices)

#### Scrape District-Level Data
```bash
# Local
curl -X GET "http://localhost:1136/scrape/yard?state_id=11&district_id=162"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/scrape/yard?state_id=11&district_id=162"
```

#### Scrape Market-Level Data
```bash
# Local
curl -X GET "http://localhost:1136/scrape/yard?state_id=11&district_id=162&market_id=1234"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/scrape/yard?state_id=11&district_id=162&market_id=1234"
```

## 🤖 Automated Scraping Endpoints

### Automated District Scraping
```bash
# Local
curl -X GET "http://localhost:1136/automated/scrape/district/162"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/scrape/district/162"
```

### Automated State Scraping
```bash
# Local
curl -X GET "http://localhost:1136/automated/scrape/state/11"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/scrape/state/11"
```

### Get Automated Scraping Status
```bash
# Local
curl -X GET "http://localhost:1136/automated/status"

# Production
curl -X GET "https://khedut-bazaar-py.4born.com/automated/status"
```

### Bulk Scraping
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

**Scraping Response:**
```json
{
  "status": "success",
  "message": "Scraped data for 1 locations successfully",
  "successful_locations": [
    "Gujarat/Vadodara(Baroda)"
  ],
  "failed_locations": [],
  "stats": {
    "commodities": 1068,
    "districts": 708,
    "markets": 4840,
    "states": 36
  },
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

## ⏰ Automated Scheduler (NEW!)

### Scheduler Management
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

### Schedule Management
```bash
# Add state to schedule (automatically gets all districts for this state)
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

**Scheduler Status Response:**
```json
{
  "status": "success",
  "data": {
    "is_running": true,
    "enabled": true,
    "schedule_time": "21:00",
    "scheduled_states": [11, 12],
    "next_run": "Today at 21:00"
  },
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### Configuration File
The scheduler uses a JSON configuration file (`scraping_config.json`) that is automatically created:
```json
{
  "enabled": true,
  "schedule_time": "21:00",
  "states_to_scrape": [11, 12],
  "delay_between_requests": 3,
  "max_retries": 3,
  "log_file": "scraping_scheduler.log",
  "description": "Only add state IDs here. The system will automatically get all districts for each state and scrape commodity data."
}
```

**Note**: Only add state IDs to the configuration. The system will automatically fetch all districts for each state from the database and scrape commodity data for all districts.

## 🗄️ Database Schema

### States Table
```sql
CREATE TABLE states (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Districts Table
```sql
CREATE TABLE districts (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states (id)
);
```

### Markets Table
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

### Commodity Prices Table
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

## 🔧 Features

### ✅ URL Formation Fix
- Handles special characters in location names
- Example: "Vadodara(Baroda)" → "vadodara-baroda"
- Works for all scraping operations

### ✅ Database Structure
- Uses IDs instead of names for better performance
- Proper foreign key relationships
- Automatic data migration support

### ✅ Last Updated Tracking
- Tracks when data was last modified
- Only updates changed values
- Maintains data integrity

### ✅ Automated Scheduler
- **Auto-starts** when the Flask application starts
- Runs scraping tasks automatically at 9 PM daily
- **Simplified configuration**: Only need to provide state IDs
- **Automatic district discovery**: Gets all districts for each state from database
- **Commodity data scraping**: Scrapes commodity prices for all districts automatically
- Thread-safe operation with proper error handling

### ✅ Error Handling
- Comprehensive error responses
- Proper HTTP status codes
- Detailed logging

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Missing required parameters: state_id, district_id",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "State with ID 999 not found",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Database connection failed",
  "timestamp": "2025-08-05T12:24:19.123456"
}
```

## 📝 Notes

- All timestamps are in ISO 8601 format
- IDs must be integers
- Scraping endpoints may take time to complete
- Data is automatically deduplicated based on unique constraints
- The system handles URL normalization for special characters
- Foreign key constraints ensure data integrity

## 🔗 Links

- **Live Website**: https://khedut-bazaar-py.4born.com/
- **Source Data**: https://agriplus.in/prices/all
- **API Health**: https://khedut-bazaar-py.4born.com/api/database/health

---

© 2025 Khedut Bazaar. All rights reserved.
