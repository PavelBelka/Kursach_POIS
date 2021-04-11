from django.urls import path
from django.views.decorators.cache import cache_page, cache_control, never_cache

from .views import BooksView, BookInstanceDetailView, UserProfileListCreateView, UserProfileDetailView, GenreListCreateView, \
    GenreDetailView, AuthorListCreateView, AuthorDetailView, BookDetailView, BookInstanceListCreateView

app_name = 'libraryapp'

urlpatterns = [
    path('books', cache_control(public=True, must_revalidate=True)(cache_page(60*60*24)(BooksView.as_view()))),
    path("books/<int:pk>", never_cache(BookDetailView.as_view())),

    path('bookinstances', never_cache(BookInstanceListCreateView.as_view())),
    path("bookinstances/<id_security>", cache_control(private=True)(cache_page(60*60*24*15)(BookInstanceDetailView.as_view()))),

    path("all-profiles", never_cache(UserProfileListCreateView.as_view()), name="all-profiles"),
    path("profile", never_cache(UserProfileDetailView.as_view()), name="profile"),

    path('genre', never_cache(GenreListCreateView.as_view())),
    path("genre/<int:pk>", never_cache(GenreDetailView.as_view())),

    path('authors', cache_page(60*60*24*15)(AuthorListCreateView.as_view())),
    path("authors/<int:pk>", never_cache(AuthorDetailView.as_view()))
]
