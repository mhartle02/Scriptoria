class book:
    def __init__(self, title, authors, description):
        self.title = title
        self.authors = authors
        self.description = description

    def __str__(self):
        return f"Title: {self.title}\nAuthors: {', '.join(self.authors)}\nDescription: {self.description}\n"
