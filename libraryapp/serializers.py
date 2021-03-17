from rest_framework import serializers

from .models import Book, Author, Genre, BookInstance, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class BookInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = ('id_security', 'text')


class BookInstanceToBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = ('id_security',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')


class AuthorToBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'birthday')


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorToBookSerializer(read_only=True, many=True)
    genre = GenreSerializer(read_only=True, many=True)
    id_inst = BookInstanceToBookSerializer(read_only=True, many=False)

    class Meta:
        model = Book
        fields = ('id', 'title', 'authors', 'isbn', 'genre', 'status', 'id_inst')