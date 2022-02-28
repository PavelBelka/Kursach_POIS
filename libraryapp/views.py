from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from .permissions import IsReaderOrAdmin, IsOwnerProfileOrReadOnly
from .serializers import BookSerializer, BookInstanceSerializer, UserProfileSerializer, GenreSerializer, \
    AuthorSerializer, BookInstanceAdminSerializer, UserCreateSerializer, UserSerializer
from .models import Book, BookInstance, UserProfile, Genre, Author


class AuthorListCreateView(ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsReaderOrAdmin,]


class AuthorDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.filter()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsReaderOrAdmin, ]


class GenreListCreateView(ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class GenreDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.filter()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class BooksView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsReaderOrAdmin]

    def create(self, request, *args, **kwargs):
        data = request.data
        security = BookInstance.objects.get(id_security=data['id_instance']['id_security'])
        book = Book.objects.create(title=data['title'], isbn=data['isbn'], status=data['status'], id_instance=security)
        book.save()
        for author in data['authors']:
            auth = Author.objects.get(first_name=author['first_name'], last_name=author['last_name'])
            book.authors.add(auth)
        for genre in data['genre']:
            gen = Genre.objects.get(name=genre['name'])
            book.genre.add(gen)
        serializer=self.get_serializer(book)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.filter()
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def update(self, request, *args, **kwargs):
        data = request.data
        book = Book.objects.get(id=self.kwargs['pk'])
        book.title = data['title']
        book.isbn = data['isbn']
        book.status = data['status']
        book.save()
        book.authors.clear()
        book.genre.clear()
        for author in data['authors']:
            auth = Author.objects.get(first_name=author['first_name'], last_name=author['last_name'])
            book.authors.add(auth)
        for genre in data['genre']:
            gen = Genre.objects.get(name=genre['name'])
            book.genre.add(gen)
        serializer = self.get_serializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookInstanceDetailView(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id_security'
    queryset = BookInstance.objects.filter()
    serializer_class = BookInstanceSerializer
    permission_classes = [IsAuthenticated, IsReaderOrAdmin]


class BookInstanceListCreateView(ListCreateAPIView):
    queryset = BookInstance.objects.all()
    serializer_class = BookInstanceAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class UserProfileListCreateView(ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, ]


    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

