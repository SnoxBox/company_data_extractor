# Company data extactor
This is a Flask-based web application that provides an API for processing a list of domains and extracting company information. It utilizes Celery for asynchronous task processing, allowing it to handle large volumes of domains efficiently.

## Features

- **Asynchronous Processing**: Domains are processed in batches using Celery tasks, ensuring that the Flask application remains responsive.
- **Progress Tracking**: The API provides endpoints to check the status of ongoing domain processing tasks.
- **Comprehensive Data Extraction**: For each domain, the system attempts to retrieve the company name from various sources, including the website's title, meta tags, and fallback to the domain name.
- **Error Handling and Resilience**: The system is designed to handle errors gracefully, with appropriate fallbacks and error reporting.
- **Scalability**: The use of Celery and Redis allows the system to scale to handle large volumes of domains.

## Installation
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Redis server (Celery broker):
   ```bash
   redis-server
   ```
4. Start the Celery worker:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```
5. Run the Flask application:
   ```bash
   python app.py
   ```

## Docker Compose
Alternatively, you can use Docker Compose to set up and run the application. Follow these steps:

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. The Flask application will be available at `http://localhost:5500`.

## Usage

### Import Companies
To start processing a list of domains, send a POST request to the `/api/companies/import` endpoint:

```json
{
  "domains": ["google.com", "microsoft.com", "apple.com"]
}
```

This will return a `task_id` that you can use to check the status of the processing task.

### Check Processing Status
To check the status of a processing task, send a GET request to the `/api/companies/import/status/{task_id}` endpoint, where `{task_id}` is the ID returned by the import request.

The response will provide information about the current state of the task, including any errors and the processed results.

## Contributing
Contributions are welcome! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).