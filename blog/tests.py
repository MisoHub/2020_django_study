from django.test import TestCase, Client
from blog.models import Post
from django.utils import timezone
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        # self.client = Client() -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='test')

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup.title)
        self.assertEqual(soup.title.text, 'Blog')

        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog',navbar.text)
        self.assertIn('About Me', navbar.text)

        self.assertEqual(Post.objects.count(),0)
        self.assertIn('No pages', soup.body.text)

        post_000 = Post.objects.create(
            title ='The first test post',
            content = 'first post content',
            created = timezone.now(),
            author = self.author_000,
        )

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertGreater(Post.objects.count(),0)
        self.assertIn(post_000.title, soup.body.text)



def test_detail_post(self):
    self.client