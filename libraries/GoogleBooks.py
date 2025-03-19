import requests
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(path)
from classes import book


API_KEY = "AIzaSyDHIFBhhb6fnzBS0-GcXap4bh5IIbF-KnI"
BASE_URL = "https://www.googleapis.com/books/v1/volumes"


def search_books(query, max_results=5):
    params = {
        'q': query,
        'key': API_KEY,
        'maxResults': max_results
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        books = data.get("items", [])  # Extract book list


        results = []

        for item in books:
            volume_info = item.get("volumeInfo", {})
            book_result= book.book(volume_info.get("title", ["Unknown Title"]), volume_info.get("authors", ["Unknown author"]),volume_info.get("description", "No description available"))

            results.append(book_result)

        return results  # Join results with spacing
    else:
        return f"Error {response.status_code}: {response.text}"


if __name__ == "__main__":
    #books_info = search_books("East of Eden") #Pass in book name
    #print(books_info[0].title)

