from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class userProfileTestCase(APITestCase):
    profile_list_url=reverse("libraryapp:all-profiles")
    def setUp(self):
        self.user=self.client.post('users/',data={'username':'mario', 'email': 'mario@mail.li', 'password':'i-keep-jumping'})
        response=self.client.post('jwt/create/',data={'username':'mario','password':'i-keep-jumping'})
        self.token = response.body["access"]
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+self.token)

    # retrieve a list of all user profiles while the request user is authenticated
    def test_userprofile_list_authenticated(self):
        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # retrieve a list of all user profiles while the request user is unauthenticated
    def test_userprofile_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    # check to retrieve the profile details of the authenticated user
    def test_userprofile_detail_retrieve(self):
        response=self.client.get(reverse('profile',kwargs={'pk':1}))
        # print(response.data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)


    # populate the user profile that was automatically created using the signals
    def test_userprofile_profile(self):
        profile_data={'location':'nintendo world','is_reader':'True',}
        response=self.client.put(reverse('profile',kwargs={'pk':1}),data=profile_data)
        print(response.data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
