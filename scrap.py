import requests
from bs4 import BeautifulSoup

def search_topic(topic):
    # Replace 'YOUR_API_KEY' with your actual API key
    api_key = 'YOUR_API_KEY'

    # Replace 'YOUR_SEARCH_ENGINE_ID' with your actual search engine ID
    search_engine_id = 'YOUR_SEARCH_ENGINE_ID'
    query = f'{topic}'
    # Base URL for Google Custom Search API
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}&num=5'
    results=[]
    try:
        response = requests.get(url)
        data = response.json()
        items = data['items']
        
        for item in items:
            url = item['link']
            results.append([extract_content(url),url])
            
    except Exception as e:
        print("An error occurred:", e)

    return results

def extract_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract content based on your specific requirements
        # For example, to extract all paragraphs, you can do:
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])
        return content,url  
        
    except Exception as e:
        print("An error occurred while extracting content from", url, ":", e)

# def main():
#     topic = input("Enter a topic: ")
#     search_topic(topic)

# if __name__ == "__main__":
#     main()