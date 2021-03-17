from django.urls import path, include

from .views import BooksView, BookInstanceView, UserProfileListCreateView, UserProfileDetailView

app_name = 'libraryapp'

urlpatterns = [
    path('books/', BooksView.as_view()),
    path('bookinstances/', BookInstanceView.as_view()),
    path("all-profiles", UserProfileListCreateView.as_view(), name="all-profiles"),
    path("profile/<int:pk>", UserProfileDetailView.as_view(), name="profile"),
]
