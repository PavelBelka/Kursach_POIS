from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Author, Genre, BookInstance, Book
from datetime import date

class UserModelAndProfileTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')

    def test_it_has_information_fields(self):
        database_user = User.objects.get(username='mario')
        user_profile = User.objects.get(username='mario').profile
        self.assertEqual(database_user.username, 'mario')
        self.assertEqual(database_user.email, 'mario@mail.li')
        self.assertEqual(user_profile.location, None)
        self.assertEqual(user_profile.phone, None)
        self.assertEqual(user_profile.is_reader, True)


class AuthorModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = Author.objects.create(first_name='test', last_name='testovich', birthday='2022-02-27')
        cls.author_2 = Author.objects.create(first_name='yank', last_name='terebonkovich', birthday='2020-01-02')

    def test_it_has_information_fields(self):
        database_author_1 = Author.objects.get(first_name='test')
        database_author_2 = Author.objects.get(first_name='yank')
        self.assertEqual(database_author_1.first_name, self.author_1.first_name)
        self.assertEqual(database_author_1.last_name, self.author_1.last_name)
        self.assertEqual(database_author_1.birthday, date(2022, 2, 27))
        self.assertEqual(database_author_2.first_name, self.author_2.first_name)
        self.assertEqual(database_author_2.last_name, self.author_2.last_name)
        self.assertEqual(database_author_2.birthday, date(2020, 1, 2))


class GenreModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.genre = Genre.objects.create(name='test')

    def test_it_has_information_fields(self):
        database_genre = Genre.objects.get(name='test')
        self.assertEqual(database_genre.name, self.genre.name)


class BookInstanceModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.bookinstance = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c42', text='testtest')

    def test_it_has_information_fields(self):
        database_bookinstance = BookInstance.objects.get(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c42')
        self.assertEqual(database_bookinstance.text, self.bookinstance.text)


class BookModelTestCase(TestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name='yank', last_name='testovich', birthday='2022-02-27')
        self.genre = Genre.objects.create(name='test_genre')
        self.bookinstance = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c42', text='testtest')
        self.book = Book(title='test', isbn="978-5-7932-0842-3", status='a', id_instance=self.bookinstance)
        self.book.save()
        self.book.authors.add(self.author)
        self.book.genre.add(self.genre)

    def test_it_has_information_fields(self):
        database_book = Book.objects.get(title='test')
        self.assertEqual(database_book.title, self.book.title)
        self.assertEqual(database_book.authors.get(pk=self.author.pk).first_name, self.author.first_name)
        self.assertEqual(database_book.isbn, self.book.isbn)
        self.assertEqual(database_book.genre.get(pk=self.genre.pk).name, self.genre.name)
        self.assertEqual(database_book.id_instance.text, self.bookinstance.text)
        self.assertEqual(database_book.status, self.book.status)


class DRFUserAuthenticationAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url_register = reverse('register')
        cls.url_login = reverse('jwt-create')
        cls.url_refresh = reverse('jwt-refresh')
        cls.url_verify = reverse('jwt-verify')
        cls.update_first_name = 'mario'
        cls.update_last_name = 'mario'
        cls.update_location = 'mushroom kingdom'
        cls.update_phone = '88005553555'
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')

    def test_create_user(self):
        create_user_dict = {
            'username': 'Test',
            'email': 'test@test.ru',
            'password': 'Fw190dMe262',
        }
        response = self.client.post(self.url_register, create_user_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sign_up(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response = self.client.post(self.url_login, user_login_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_token(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        token = response_login.data['access']
        response_verify = self.client.post(self.url_verify, {'token':token}, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertEqual(response_verify.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        refresh_token = response_login.data['refresh']
        response_refresh = self.client.post(self.url_refresh, {'refresh':refresh_token}, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response_refresh.data['access'], access_token)

    def test_profile(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get('/api/profile', data={'format': 'json'})
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], self.user.username)
        self.assertEqual(profile_response.data['email'], self.user.email)

    def test_update_profile(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get('/api/profile', data={'format': 'json'})
        profile_update_response = self.client.put('/api/profile', {'id': profile_response.data['id'],
                                                                   'username': profile_response.data['username'],
                                                                   'first_name': self.update_first_name,
                                                                   'last_name': self.update_last_name,
                                                                   'email': profile_response.data['email'],
                                                                   'location': self.update_location,
                                                                   'phone': self.update_phone,
                                                                   'is_reader': 'true'}, format='json')
        self.assertEqual(profile_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_update_response.data['first_name'], self.update_first_name)
        self.assertEqual(profile_update_response.data['last_name'], self.update_last_name)
        self.assertEqual(profile_update_response.data['location'], self.update_location)
        self.assertEqual(profile_update_response.data['phone'], self.update_phone)

    def test_delete_profile(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_delete_response = self.client.delete('/api/profile')
        response_check_login = self.client.post(self.url_login, user_login_dict, format='json')
        self.assertEqual(profile_delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response_check_login.status_code, status.HTTP_401_UNAUTHORIZED)


class DRFGenreAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url_genre = '/api/genre'
        cls.url_genre_1 = '/api/genre/4'
        cls.url_login = reverse('jwt-create')
        cls.update_genre = 'update_genre'
        cls.add_genre = 'add_test'
        cls.superuser = User.objects.create_superuser(username='wario', email='wario@mail.li', password='i-keep-cheating')
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')
        cls.genre_1 = Genre.objects.create(name='test_1')
        cls.genre_2 = Genre.objects.create(name='test_2')

    def test_get_add_update_delete_genre_user_does_not_have_access(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_get_genre_response = self.client.get(self.url_genre)
        add_genre_response = self.client.post(self.url_genre, {'name': self.add_genre}, format='json')
        get_genre_1_response = self.client.get(self.url_genre_1)
        update_genre_1_response = self.client.put(self.url_genre_1, {'name': self.update_genre}, format='json')
        delete_genre_1_response = self.client.delete(self.url_genre_1)
        self.assertEqual(list_get_genre_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(add_genre_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(get_genre_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_genre_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_genre_1_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_genre(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_genre_response = self.client.get(self.url_genre)
        self.assertEqual(list_genre_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_genre_response.data[0]['name'], self.genre_1.name)
        self.assertEqual(list_genre_response.data[1]['name'], self.genre_2.name)

    def test_add_genre(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        add_genre_response = self.client.post(self.url_genre, {'name': self.add_genre}, format='json')
        self.assertEqual(add_genre_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_genre_response.data['name'], self.add_genre)

    def test_get_genre_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        get_genre_response = self.client.get(self.url_genre_1)
        self.assertEqual(get_genre_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_genre_response.data['name'], self.genre_1.name)

    def test_update_genre_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        update_genre_response = self.client.put(self.url_genre_1, {'name': self.update_genre}, format='json')
        self.assertEqual(update_genre_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_genre_response.data['name'], self.update_genre)

    def test_delete_genre_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        delete_genre_1_response = self.client.delete(self.url_genre_1)
        get_genre_response = self.client.get(self.url_genre_1)
        self.assertEqual(delete_genre_1_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(get_genre_response.status_code, status.HTTP_404_NOT_FOUND)


class DRFAuthorsAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url_author = '/api/authors'
        cls.url_author_1 = '/api/authors/4'
        cls.url_login = reverse('jwt-create')
        cls.update_author = {'first_name':'update_test', 'last_name':'update_test', 'birthday':'1979-06-12'}
        cls.add_author = {'first_name':'add_test', 'last_name':'add_test', 'birthday':'1979-06-12'}
        cls.superuser = User.objects.create_superuser(username='wario', email='wario@mail.li', password='i-keep-cheating')
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')
        cls.author_1 = Author.objects.create(first_name='test', last_name='testovich', birthday='2022-02-27')
        cls.author_2 = Author.objects.create(first_name='yank', last_name='terebonkovich', birthday='2020-01-02')

    def test_get_add_update_delete_author_user_does_not_have_access(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_get_author_response = self.client.get(self.url_author)
        add_author_response = self.client.post(self.url_author, self.add_author, format='json')
        get_author_1_response = self.client.get(self.url_author_1)
        update_author_1_response = self.client.put(self.url_author_1, self.update_author, format='json')
        delete_author_1_response = self.client.delete(self.url_author_1)
        self.assertNotEqual(list_get_author_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(add_author_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(get_author_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_author_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_author_1_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authors(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_authors_response = self.client.get(self.url_author)
        self.assertEqual(list_authors_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_authors_response.data[0]['first_name'], self.author_1.first_name)
        self.assertEqual(list_authors_response.data[1]['first_name'], self.author_2.first_name)

    def test_add_author(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        add_author_response = self.client.post(self.url_author, self.add_author, format='json')
        self.assertEqual(add_author_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_author_response.data['first_name'], self.add_author['first_name'])

    def test_get_author_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        get_author_response = self.client.get(self.url_author_1)
        self.assertEqual(get_author_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_author_response.data['first_name'], self.author_1.first_name)

    def test_update_author_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        update_author_response = self.client.put(self.url_author_1, self.update_author, format='json')
        self.assertEqual(update_author_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_author_response.data['first_name'], self.update_author['first_name'])

    def test_delete_author_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        delete_author_1_response = self.client.delete(self.url_author_1)
        get_author_response = self.client.get(self.url_author_1)
        self.assertEqual(delete_author_1_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(get_author_response.status_code, status.HTTP_404_NOT_FOUND)


class DRFBookTextAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url_bookinstance = '/api/bookinstances'
        cls.url_bookinstance_1 = '/api/bookinstances/35f0a699-ba20-46d7-9c86-a75e8cdf7c42'
        cls.url_login = reverse('jwt-create')
        cls.update_bookinstance = {'id_security': '35f0a699-ba20-46d7-9c86-a75e8cdf7c42', 'text': 'update_test1test1'}
        cls.add_bookinstance = {'id_security':'35f0a699-ba20-46d7-5c36-a75e5cdf7c48', 'text':'add_testtest'}
        cls.superuser = User.objects.create_superuser(username='wario', email='wario@mail.li', password='i-keep-cheating')
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')
        cls.bookinstance_1 = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c42', text='test1test1')
        cls.bookinstance_2 = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e5cdf7c48', text='test2test2')

    def test_get_add_update_delete_book_text_user_does_not_have_access(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_get_bookinstance_response = self.client.get(self.url_bookinstance)
        add_bookinstance_response = self.client.post(self.url_bookinstance, self.add_bookinstance, format='json')
        get_bookinstance_1_response = self.client.get(self.url_bookinstance_1)
        update_bookinstance_1_response = self.client.put(self.url_bookinstance_1, self.update_bookinstance, format='json')
        delete_bookinstance_1_response = self.client.delete(self.url_bookinstance_1)
        self.assertEqual(list_get_bookinstance_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(add_bookinstance_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(get_bookinstance_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_bookinstance_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_bookinstance_1_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_BookText(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_bookinstance_response = self.client.get(self.url_bookinstance)
        self.assertEqual(list_bookinstance_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_bookinstance_response.data[0]['id_security'], self.bookinstance_1.id_security)
        self.assertEqual(list_bookinstance_response.data[1]['id_security'], self.bookinstance_2.id_security)

    def test_add_BookText(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        add_bookinstance_response = self.client.post(self.url_bookinstance, self.add_bookinstance, format='json')
        self.assertEqual(add_bookinstance_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_bookinstance_response.data['id_security'], self.add_bookinstance['id_security'])

    def test_get_BookText_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        get_bookinstance_response = self.client.get(self.url_bookinstance_1)
        self.assertEqual(get_bookinstance_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_bookinstance_response.data['id_security'], self.bookinstance_1.id_security)

    def test_update_BookText_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        update_bookinstance_response = self.client.put(self.url_bookinstance_1, self.update_bookinstance, format='json')
        self.assertEqual(update_bookinstance_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_bookinstance_response.data['id_security'], self.update_bookinstance['id_security'])

    def test_delete_BookText_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        delete_bookinstance_1_response = self.client.delete(self.url_bookinstance_1)
        get_bookinstance_response = self.client.get(self.url_bookinstance_1)
        self.assertEqual(delete_bookinstance_1_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(get_bookinstance_response.status_code, status.HTTP_404_NOT_FOUND)


class DRFBookAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)
        cls.url_book = '/api/books'
        cls.url_book_1 = '/api/books/2'
        cls.url_login = reverse('jwt-create')
        cls.update_book = {"title": "Тест",
                                 "authors": [{"first_name": "test", "last_name": "testovich"}], "isbn": "978-5-7932-0842-3",
                                 "genre": [{"name": "test_genre_1"}], "status": "a",
                                 "id_instance": {"id_security":"35f0a699-ba20-46d7-9c86-a75e8cdf7c45"}}
        cls.add_book = {"title": "Программирование на языке Python",
                                 "authors": [{"first_name": "test", "last_name": "testovich"}], "isbn": "978-5-7932-0842-7",
                                 "genre": [{"name": "test_genre_1"}], "status": "n_a",
                                 "id_instance": {"id_security":"35f0a699-ba20-56d7-9c86-a7578cdf5905"}}
        cls.superuser = User.objects.create_superuser(username='wario', email='wario@mail.li', password='i-keep-cheating')
        cls.user = User.objects.create_user(username='mario', email='mario@mail.li', password='i-keep-jumping')
        cls.author_1 = Author.objects.create(first_name='test', last_name='testovich', birthday='2022-02-27')
        cls.author_2 = Author.objects.create(first_name='yank', last_name='terebonkovich', birthday='2020-01-02')
        cls.genre_1 = Genre.objects.create(name='test_genre_1')
        cls.genre_2 = Genre.objects.create(name='test_genre_2')
        cls.bookinstance_1 = BookInstance.objects.create(id_security='35f0a699-ba20-56d7-9c86-a7578cdf5905',
                                                         text='test1test1')
        cls.bookinstance_2 = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c45',
                                                          text='test2test2')
        cls.bookinstance_3 = BookInstance.objects.create(id_security='35f0a699-ba20-46d7-9c86-a75e8cdf7c46',
                                                         text='test3test3')
        cls.book_1 = Book(title='test_1', isbn="978-5-7932-0842-3", status='a', id_instance=cls.bookinstance_2)
        cls.book_2 = Book(title='test_2', isbn="978-5-7932-0452-2", status='a', id_instance=cls.bookinstance_3)
        cls.book_1.save()
        cls.book_2.save()
        cls.book_1.authors.add(cls.author_1)
        cls.book_1.authors.add(cls.author_2)
        cls.book_1.genre.add(cls.genre_1)
        cls.book_1.genre.add(cls.genre_2)

    def test_get_add_update_delete_book_user_does_not_have_access(self):
        user_login_dict = {
            'username': 'mario',
            'password': 'i-keep-jumping',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_get_book_response = self.client.get(self.url_book)
        add_book_response = self.client.post(self.url_book, self.add_book, format='json')
        get_book_1_response = self.client.get(self.url_book_1)
        update_book_1_response = self.client.put(self.url_book_1, self.update_book, format='json')
        delete_book_1_response = self.client.delete(self.url_book_1)
        self.assertNotEqual(list_get_book_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(add_book_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(get_book_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_book_1_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_book_1_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_Book(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_book_response = self.client.get(self.url_book)
        self.assertEqual(list_book_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_book_response.data[0]['title'], self.book_1.title)
        self.assertEqual(list_book_response.data[1]['title'], self.book_2.title)

    def test_add_Book(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        add_book_response = self.client.post(self.url_book, self.add_book, format='json')
        self.assertEqual(add_book_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(add_book_response.data['title'], self.add_book['title'])

    def test_get_Book_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        get_book_response = self.client.get(self.url_book_1)
        self.assertEqual(get_book_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_book_response.data['title'], self.book_1.title)

    def test_update_Book_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        update_book_response = self.client.put(self.url_book_1, self.update_book, format='json')
        self.assertEqual(update_book_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_book_response.data['title'], self.update_book['title'])

    def test_delete_Book_1(self):
        user_login_dict = {
            'username': 'wario',
            'password': 'i-keep-cheating',
        }
        response_login = self.client.post(self.url_login, user_login_dict, format='json')
        access_token = response_login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        delete_book_1_response = self.client.delete(self.url_book_1)
        get_book_response = self.client.get(self.url_book_1)
        self.assertEqual(delete_book_1_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(get_book_response.status_code, status.HTTP_404_NOT_FOUND)