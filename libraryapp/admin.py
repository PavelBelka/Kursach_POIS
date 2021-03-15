from django.contrib import admin
from .models import Author, Book, BookInstance, Genre

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookInstance)
admin.site.register(Genre)