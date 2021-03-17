from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerProfileOrReadOnly
from .serializers import BookSerializer, BookInstanceSerializer, UserProfileSerializer
from .models import Book, BookInstance, UserProfile


class BooksView(ListCreateAPIView):
        queryset = Book.objects.all()
        serializer_class = BookSerializer
        permission_classes = [IsAuthenticated]


class BookInstanceView(APIView):
    def get(self, request):
        bookinstances = BookInstance.objects.all()
        serializer = BookInstanceSerializer(bookinstances, many=True)
        return Response(serializer.data)


class UserProfileListCreateView(ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]
