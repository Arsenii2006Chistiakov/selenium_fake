from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Quotes Scraper API",
    description="An API that scrapes quotes from quotes.toscrape.com",
    version="1.0.0"
)

class Quote(BaseModel):
    quote: str
    author: str
    tags: List[str]

class ScrapingResponse(BaseModel):
    success: bool
    message: str
    quotes: Optional[List[Quote]] = None
    total_quotes: Optional[int] = None

class QuotesScraper:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        
        # Additional options for Railway deployment
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            self.chrome_options.binary_location = os.environ.get('CHROME_BINARY_PATH', '/usr/bin/google-chrome')
        
        # Initialize the driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "http://quotes.toscrape.com"
        self.quotes_data = []

    def wait_and_find_element(self, by, value):
        """Wait for and return an element"""
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        )

    def wait_and_find_elements(self, by, value):
        """Wait for and return multiple elements"""
        return self.wait.until(
            EC.presence_of_all_elements_located((by, value))
        )

    def extract_quote_data(self, quote_element):
        """Extract data from a single quote element"""
        try:
            quote_text = quote_element.find_element(By.CLASS_NAME, "text").text
            author = quote_element.find_element(By.CLASS_NAME, "author").text
            tags = [tag.text for tag in quote_element.find_elements(By.CLASS_NAME, "tag")]
            
            return Quote(
                quote=quote_text,
                author=author,
                tags=tags
            )
        except NoSuchElementException as e:
            logger.error(f"Error extracting quote data: {e}")
            return None

    def scrape_page(self):
        """Scrape all quotes from the current page"""
        try:
            quotes = self.wait_and_find_elements(By.CLASS_NAME, "quote")
            for quote in quotes:
                quote_data = self.extract_quote_data(quote)
                if quote_data:
                    self.quotes_data.append(quote_data)
            return True
        except TimeoutException:
            logger.error("Timeout while waiting for quotes on the page")
            return False

    def has_next_page(self):
        """Check if there is a next page"""
        try:
            next_button = self.driver.find_element(By.CLASS_NAME, "next")
            return bool(next_button)
        except NoSuchElementException:
            return False

    def go_to_next_page(self):
        """Navigate to the next page"""
        try:
            next_button = self.driver.find_element(By.CLASS_NAME, "next")
            next_button.find_element(By.TAG_NAME, "a").click()
            time.sleep(1)  # Small delay to let the page load
            return True
        except NoSuchElementException:
            return False

    def scrape_all_quotes(self):
        """Main method to scrape all quotes from all pages"""
        try:
            logger.info("Starting the scraping process...")
            self.driver.get(self.base_url)
            
            while True:
                if not self.scrape_page():
                    break
                
                logger.info(f"Scraped {len(self.quotes_data)} quotes so far...")
                
                if not self.has_next_page():
                    break
                    
                if not self.go_to_next_page():
                    break
            
            return self.quotes_data
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e
        finally:
            self.driver.quit()

@app.get("/", response_model=dict)
async def root():
    """Root endpoint that returns API information"""
    return {
        "name": "Quotes Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "GET - Scrape all quotes from quotes.toscrape.com",
            "/": "GET - This information"
        }
    }

@app.get("/scrape", response_model=ScrapingResponse)
async def scrape_quotes():
    """Endpoint to trigger the scraping process"""
    try:
        scraper = QuotesScraper()
        quotes = scraper.scrape_all_quotes()
        
        return ScrapingResponse(
            success=True,
            message="Scraping completed successfully",
            quotes=quotes,
            total_quotes=len(quotes)
        )
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during scraping: {str(e)}"
        )

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
