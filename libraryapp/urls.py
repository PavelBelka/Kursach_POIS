from django.urls import path

from .views import BooksView, BookInstanceDetailView, UserProfileListCreateView, UserProfileDetailView, GenreListCreateView, \
    GenreDetailView, AuthorListCreateView, AuthorDetailView, BookDetailView, BookInstanceListCreateView

app_name = 'libraryapp'

urlpatterns = [
    path('books', BooksView.as_view()),
    path("books/<int:pk>",BookDetailView.as_view()),

    path('bookinstances', BookInstanceListCreateView.as_view()),
    path("bookinstances/<id_security>", BookInstanceDetailView.as_view()),

    path("all-profiles", UserProfileListCreateView.as_view(), name="all-profiles"),
    path("profile", UserProfileDetailView.as_view(), name="profile"),

    path('genre', GenreListCreateView.as_view()),
    path("genre/<int:pk>", GenreDetailView.as_view()),

    path('authors', AuthorListCreateView.as_view()),
    path("authors/<int:pk>", AuthorDetailView.as_view())
]
