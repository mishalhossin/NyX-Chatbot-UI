import re
from bs4 import BeautifulSoup
from datetime import datetime
import requests

def search(prompt):
    try:
        url_match = re.search(r'(https?://\S+)', prompt)
        if url_match:
            url = url_match.group(0)
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            
            soup = BeautifulSoup(html_content, "html.parser")
            main_content_p = soup.find_all("p")
            main_content_a = soup.find_all("a")
            main_content_article = soup.find_all("article")
            main_content_div = soup.find_all("div", class_=re.compile("main-content"))
            main_content_main = soup.find_all("main")
            title_meta_tag = soup.find("title")
            
            if title_meta_tag:
                title = f"{title_meta_tag.get_text()}"
            else:
                title = "No title found in the meta tag."

            text = ""
            
            for tag in main_content_p:
                text += tag.get_text() + " "

            for tag in main_content_a:
                text += tag.get_text() + " "

            for tag in main_content_article:
                text += tag.get_text() + " "

            for tag in main_content_div:
                text += tag.get_text() + " "

            for tag in main_content_main:
                text += tag.get_text() + " "

            text = text[:8000]

            if not text.strip():
                return "No main content found on the website."
            elif text == "":
                return "No main content found on the website."
            
            response = {}
            response["content"] = f"Title: {title}\n\nMain Content:\n{text}"
            response["url"] = url
            return response
        else:
            search_query = prompt

        if search_query is not None and len(search_query) > 300:
            return None

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blob = f"Search results for: '{search_query}' at {current_time}:\n"
        
        if search_query is None:
            return None
        elif search_query is not None:
            try:
                response = requests.get('https://ddg-api.awam.repl.co/api/search', params={'query': search_query, 'maxNumResults': 5})
                response.raise_for_status()
                search = response.json()
            except Exception as e:
                print(f"An error occurred during the search request: {e}")
                return

            for index, result in enumerate(search):
                try:
                    blob += f'[{index}] "Title : {result["Title"]} \nSnippet : {result["Snippet"]}"\nURL: {result["Link"]}\n\n\n'
                except Exception as e:
                    blob += f'Search error: {e}\n'
            
            blob += f"\n\nSearch Query : {search_query}\n\nSearch results allow you to have real-time information and the ability to browse the internet. As the Search results were generated by the system rather than the user, please send a response and if you want to provide links, provide only one URL in a bullet point. Also, the current time is {current_time}"
            content = {}
            content["content"] = blob
            content["query"] = search_query
            return content
        else:
            return None
    except Exception as e:
        return f"Error while searching / scraping websites on the internet: {e}"
