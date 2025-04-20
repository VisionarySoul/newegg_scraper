# Newegg Product Scraper

A robust Python scraper for collecting product information from Newegg's deals section. The scraper uses API endpoints and includes anti-blocking measures.

## Features

- API-based scraping of Newegg deals
- Anti-blocking measures (rotating user agents, random delays)
- Retry mechanism for failed requests
- Detailed logging
- Output in both CSV and JSON formats
- Rate limiting and request throttling
- Error handling and recovery
- Docker containerization with volume mounting

## Requirements

- Python 3.11+
- Required packages:
  - httpx
  - fake-useragent
- Docker and Docker Compose (for containerized deployment)

## Installation

### Method 1: Direct Installation

1. Clone the repository or download the files
2. Install the required packages:
```bash
pip install httpx fake-useragent
```

### Method 2: Using Docker

1. Make sure Docker and Docker Compose are installed
2. Build and run using Docker Compose:
```bash
docker-compose up --build
```

## Usage

### Running Directly

```bash
python api_scrape.py
```

### Using Docker

```bash
docker-compose up
```

## Configuration

You can modify these variables in `api_scrape.py`:

- `max_pages`: Maximum number of pages to scrape (default: 50)
- `min_products`: Minimum number of products to collect (default: 500)
- Random delay settings in `get_random_delay()`:
  - Base delay: 2-5 seconds
  - Extended delay (10% chance): Additional 2-5 seconds
  - 403 error delay: 5-10 seconds

## Output

The scraper generates two types of output files with timestamps in the `scraped_data` directory:

1. CSV file: `scraped_data/newegg_products_YYYYMMDD_HHMMSS.csv`
2. JSON file: `scraped_data/newegg_products_YYYYMMDD_HHMMSS.json`

### Data Fields

- number: Product counter
- title: Product name
- description: Product description
- bullet_description: Detailed bullet-point description
- price: Product price
- rating: Product rating
- seller: Seller name
- product_number: Newegg product number

## Project Structure

```
newegg-scraper/
├── api_scrape.py         # Main scraper script
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker service configuration
├── requirements.txt     # Python dependencies
├── scraped_data/        # Output directory for scraped data
└── README.md           # Project documentation
```

## Anti-Blocking Measures

- Rotating User Agents
- Random delays between requests
- Retry mechanism for failed requests
- Custom headers
- Session management
- Rate limiting

## Error Handling

- Automatic retries for failed requests (max 3 attempts)
- Extended delays after 403 errors
- Detailed logging of errors and operations
- Graceful shutdown on critical errors

## Logging

The scraper includes detailed logging with timestamps and log levels:
- INFO: General operation information
- WARNING: Non-critical issues
- ERROR: Critical problems

## Docker Support

The project includes Docker configuration for containerized running:

- `Dockerfile`: Container configuration
- `docker-compose.yml`: Service orchestration
- Resource limits:
  - Memory limit: 512MB
  - Memory reservation: 256MB
- Volume mounting:
  - `./scraped_data:/app/scraped_data`: Maps the output directory

## Files

- `api_scrape.py`: Main scraper script
- `Dockerfile`: Docker container configuration
- `docker-compose.yml`: Docker service configuration
- `requirements.txt`: Python dependencies

## Best Practices

1. Always check Newegg's robots.txt and terms of service
2. Use reasonable delays between requests
3. Monitor the logs for any issues
4. Regularly check for updates to the API endpoint

## Troubleshooting

1. If you get HTTP 403 errors:
   - The script will automatically retry with longer delays
   - Check if your IP has been temporarily blocked

2. If you get ModuleNotFoundError:
   - Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. For Docker issues:
   - Ensure Docker is running
   - Try rebuilding the container:
   ```bash
   docker-compose build --no-cache
   ```
   - Check if the `scraped_data` directory exists and has proper permissions