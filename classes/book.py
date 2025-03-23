class Book:
    def __init__(self, title, authors, description, page_count, cover_image, average_rating):
        self.title = title
        self.authors = ", ".join(authors)
        self.description = description
        self.page_count = page_count
        self.cover_image = cover_image
        self.average_rating = average_rating

        #More debugging for author comma issue
        #print(f"Processed Authors: {self.authors}")

    def __str__(self):
        return f"Title: {self.title}\nAuthors: {self.authors}\nDescription: {self.description}\n"
