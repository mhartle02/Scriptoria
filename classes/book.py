class Book:
    def __init__(self, title, authors, description, page_count, cover_image):
        self.title = title
        self.authors = authors
        self.description = description
        self.page_count = page_count
        self.cover_image = cover_image

    def __str__(self):
        return f"Title: {self.title}\nAuthors: {', '.join(self.authors)}\nDescription: {self.description}\n"
