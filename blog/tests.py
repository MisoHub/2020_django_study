from django.test import TestCase, Client
from blog.models import Post
from django.utils import timezone
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
# Create your tests here.

class TestView(TestCase):


    def setUp(self):
        # self.client = Client() ## -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='test')

    def createPost(self, title, content, author):
        return Post.objects.create(
            title=title,
            content=content,
            created=timezone.now(),
            author=author,
        )

    def test_page_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup.title)
        self.assertEqual(soup.title.text, 'Blog')

        # check post_list navbar
        self.test_page_navbar(soup=soup)

        self.assertEqual(Post.objects.count(),0)
        self.assertIn('No pages', soup.body.text)

        post_000 = self.createPost(
            title ='The first tet post',
            content = 'first post content',
            author = self.author_000,
        )

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertGreater(Post.objects.count(),0)
        self.assertIn(post_000.title, soup.body.text)

    def test_detail_post(self):

        post_000 = self.createPost(
            title='The first tet post',
            content='first post content',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertIn(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, '{} - Blog'.format(post_000.title))

        # check detail page navbar
        self.test_page_navbar(soup=soup)


