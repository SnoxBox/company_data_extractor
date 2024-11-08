from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from celery import Celery
from config import Config
from db import get_db_connection
from utils import save_results_to_db, AsyncCompanyExtractor
from datetime import datetime
from math import ceil
from typing import List, Dict
import asyncio

# Flask app configuration
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

app_host: str = 'localhost'
app_port: int = 5500

# Initialize Celery
celery = Celery(
    app.name,
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)
celery.conf.update(app.config)

@celery.task(bind=True)
def process_domains_task(self, domains: List[str], batch_size: int = 50) -> Dict:
    """Celery task to process domains."""
    num_of_domains = len(domains)

    # Automatically determine the optimal batch size
    optimal_batch_size = min(500, num_of_domains) # Use the minimum of 500 (a reasonable maximum) and the total number of domains
    num_batches = ceil(num_of_domains / optimal_batch_size) # Calculate the number of batches needed
    actual_batch_size = max(ceil(num_of_domains / num_batches), 1) # Calculate the actual batch size, ensuring it's not less than 1

    extractor = AsyncCompanyExtractor(batch_size=actual_batch_size)
    results = []

    # Process each batch
    for i in range(num_batches):
        batch = domains[i * actual_batch_size:(i + 1) * actual_batch_size] # Extract the current batch of domains

        # Process the current batch
        batch_results = asyncio.run(extractor.process_batch(batch))
        results.extend(batch_results)

        # Add domains from this batch to the processed set
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i,
                'total': num_batches,
                'total domains': num_of_domains,
                'status': f'Processing batch {i + 1} of {num_batches}'
            }
        )

        save_results_to_db(batch_results)
    
    # Calculate statistics
    success_count = sum(1 for r in results if r['status'] == 'success')
    fallback_count = sum(1 for r in results if r['status'] == 'fallback')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    return {
        'task_id': self.request.id,
        'status': 'completed',
        'results': results,
        'stats': {
            'total': len(domains),
            'success': success_count,
            'fallback': fallback_count,
            'errors': error_count
        },
        'timestamp': datetime.now().isoformat()
    }


@app.route('/api/companies/import', methods=['POST', 'OPTIONS'])
def import_companies():
    """API endpoint to start domain processing."""
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    # Handle POST requests
    try:
        data = request.get_json()
        
        if not data or 'domains' not in data:
            return jsonify({'error': 'No domains provided'}), 400
            
        domains = data['domains']

        # Start Celery task
        task = process_domains_task.delay(domains)
        
        return jsonify({
            'task_id': task.id,
            'status': 'processing',
            'status_url': f'http://localhost:5500/api/companies/import/status/{task.id}',
            'total_domains': len(domains),
        })
    except Exception as e:
        print(f'Error processing domains: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/import/status/<task_id>')
def get_task_status(task_id):
    """Check the status of a processing task."""
    try:
        task = process_domains_task.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task not found or pending...'
            }
        elif task.state == 'FAILURE':
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'status': 'Task completed',
                'result': task.get()
            }
        else:
            response = {
                'state': task.state,
                'status': task.info.get('status', '')
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/search', methods=['GET'])
def search_company():
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Check if the domain already exists in the database
        cursor.execute("""
            SELECT * FROM company_info
            WHERE name LIKE %s OR domain LIKE %s
        """, ('%' + query + '%', '%' + query + '%'))
        result = cursor.fetchone()
    connection.close()

    # Check if a company was found
    if result:
        res = {
            result.get('name'): {
                "domain": result.get('domain'),
                "description": result.get('description'),
                "twitter": result.get('twitter'),
                "url": result.get('url'),
                "status": result.get('status'),
                "founded": result.get('founded'),
                "employee_range": result.get('employee_range'),
                "location": result.get('location')
            }
        }

        return res
    else:
        return None # No matching company found
    
# Add a simple health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host=app_host, port=app_port)