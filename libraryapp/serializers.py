from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Book, Author, Genre, BookInstance, UserProfile


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(style={"input_type": "password"}, write_only=True ,required=True, min_length=8)


    class Meta:
        model = User
        fields = ('username', 'email', 'password')


    def create(self, validated_data):
        try:
            user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        except IntegrityError:
            self.fail("cannot_create_user")
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('location', 'phone', 'date_joined', 'is_reader',)


class UserSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='profile.location')
    phone = serializers.CharField(source='profile.phone')
    date_joined = serializers.DateTimeField(source='profile.date_joined')
    is_reader = serializers.BooleanField(source='profile.is_reader')

    class Meta:
        model = User
        fields = ('id','username', 'first_name', 'last_name', 'email', 'location', 'phone', 'date_joined', 'is_reader')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        UserProfile.objects.update_or_create(user=instance, defaults=profile_data)
        user = super(UserSerializer, self).update(instance, validated_data)
        return user


class BookInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = ('id_security', 'text')


class BookInstanceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = ('id', 'id_security')


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
    authors = AuthorToBookSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    id_inst = BookInstanceToBookSerializer(many=False, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'authors', 'isbn', 'genre', 'status', 'id_inst')

