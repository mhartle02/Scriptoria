import requests

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

        formatted_results = []
        for book in books:
            volume_info = book.get("volumeInfo", {})
            title = volume_info.get("title", "No title available")
            authors = volume_info.get("authors", ["Unknown author"])
            description = volume_info.get("description", "No description available")

            formatted_results.append(f"Title: {title}\nAuthor: {', '.join(authors)}\nDescription: {volume_info.get('description')}")

        return "\n\n".join(formatted_results)  # Join results with spacing
    else:
        return f"Error {response.status_code}: {response.text}"


if __name__ == "__main__":
    books_info = search_books("East of Eden") #Pass in book name
    print(books_info)
