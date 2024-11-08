import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urlparse
import re
import asyncio
from typing import List, Dict
from db import get_db_connection

class AsyncCompanyExtractor:
    def __init__(self, batch_size=50):
        self.batch_size = batch_size

    async def fetch_company_info(self, domain: str, session: aiohttp.ClientSession) -> Dict:
        """Asynchronously fetch company and website information."""
        try:
            # Clean the domain
            domain = domain.lower().strip().replace('http://', '').replace('https://', '').split('/')[0]
            
            # Make a GET request to the domain with a short timeout
            async with session.get(f'https://{domain}', timeout=10, allow_redirects=True) as response:
                if response.status == 200:
                    # Get the page content and parse it with BeautifulSoup
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    # Try to extract the company name from the page
                    app_name = soup.find('meta', {'name': 'application-name'})
                    og_site_name = soup.find('meta', {'property': 'og:site_name'})
                    
                    # Try to get the website URL and description
                    og_site_url = soup.find('meta', {'property': 'og:url'})
                    link_site_url = soup.find('link', {'rel': 'canonical'})
                    og_description = soup.find('meta', {'property': 'og:description'})
                    app_description = soup.find('meta', {'name': 'description'})
                    
                    # Try to get social media tags
                    twitter_site = soup.find('meta', {'name': 'twitter:site'})
                    twitter_creator = soup.find('meta', {'name': 'twitter:creator'})
                    
                    # Extract the company name
                    if (app_name and app_name.get('content')):
                        name = app_name.get('content')
                    elif (og_site_name and og_site_name.get('content')):
                        og_name = og_site_name.get('content')

                        # Extract the base domain name from the URL
                        parsed_url = urlparse(url)
                        domain_name = parsed_url.netloc.split('.')[0].lower()
                        
                        # Clean the og_site_name content
                        name = clean_company_name(og_name, domain_name)
                    else:
                        name = domain.replace('www.', '').split('.')[0].capitalize()
                    
                    # Url is either og_url or link_url if available
                    url = og_site_url.get('content') if og_site_url else link_site_url.get('href') if link_site_url else None

                    # Twitter is either twitter_site or twitter_creator if available
                    twitter = twitter_site.get('content') if twitter_site else twitter_creator.get('content') if twitter_creator else None

                    # Description is either og_description or app_description if available
                    description = og_description.get('content') if og_description else app_description.get('content') if app_description else None
                    
                    # Return the extracted information
                    return {
                        'domain': domain,
                        'name': name,
                        'url': url,
                        'description': description,
                        'twitter': twitter,
                        'status': 'success'
                    }
                
            # If the request failed, use the domain name as a fallback
            return {
                'domain': domain,
                'name': domain.split('.')[0].title(),
                'url': None,
                'description': None,
                'twitter': None,
                'status': 'fallback'
            }
        
        except Exception:
            # If any exception occurs, use the domain name as a fallback
            return {
                'domain': domain,
                'name': domain.split('.')[0].title(),
                'url': None,
                'description': None,
                'twitter': None,
                'status': 'error'
            }

    async def process_batch(self, domains: List[str]) -> List[Dict]:
        """Process a batch of domains concurrently."""
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=50, ssl=False),
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            tasks = [self.fetch_company_info(domain, session) for domain in domains]
            return await asyncio.gather(*tasks)

def clean_company_name(og_content, domain_name):
    # Clean the og_content by trying to match the base domain name and remove extra stuff
    if domain_name in og_content.lower():
        # Return only the part before a dash or extra descriptors
        match = re.match(r'^[^-\(]*', og_content)  # Match text before a dash or parentheses
        if match:
            return match.group(0).strip()  # Strip any leading/trailing spaces
    return og_content.strip()

def get_company_from_db(domain: str):
    """Get a company from the database by domain."""
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM company_info WHERE domain LIKE %s", ('%' + domain + '%',))
        result = cursor.fetchone()
    connection.close()
    return result

def save_results_to_db(results: List[Dict]):
    """Save batch results to the MariaDB database, checking if each company already exists."""
    for result in results:
        # Check if the domain already exists in the database
        existing_company = get_company_from_db(result['domain'])
        
        if existing_company:
            continue # Skip this entry if it already exists

        # Insert the new company record if it doesn't already exist
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO company_info (domain, name, url, description, twitter, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                result['domain'],
                result['name'],
                result['url'],
                result['description'],
                result['twitter'],
                result['status']
            ))
        connection.commit()
        connection.close()