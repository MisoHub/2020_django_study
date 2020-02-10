from django.test import TestCase, Client
from blog.models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User

from bs4 import BeautifulSoup
# Create your tests here.

def create_category(name="Jazz", description=''):
    category, iscreated = Category.objects.get_or_create(
        name=name,
        description=description
    )
    return category

def create_post(title, content, author, category=None):
    return Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category
    )


class TestModel(TestCase):
    def setUp(self):
        # self.client = Client() ## -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='test')

    def test_category(self):
        category = create_category()
        post_000 = create_post(
            title ='The first tet post',
            content = 'first post content',
            author = self.author_000,
            category = category
        )
        self.assertEqual(category.post_set.count(),1)

    def test_post(self):
        category = create_category('Jazz')
        post_000 = create_post(
            title ='The first tet post',
            content = 'first post content',
            author = self.author_000,
            category = category
        )


class TestView(TestCase):

    def setUp(self):
        # self.client = Client() ## -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='test')

    # method should not be named 'test*'
    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

    def check_side_categories(self, soup):
        category_card = soup.body.find('div', id='category-card')
        self.assertIn('No Category(1)', category_card.text)
        self.assertIn('Jazz(1)', category_card.text)



    def test_post_list_without_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup.title)
        self.assertEqual(soup.title.text, 'Blog')

        # check post_list navbar
        self.check_navbar(soup=soup)

        self.assertEqual(Post.objects.count(),0)
        self.assertIn('No pages', soup.body.text)

    def test_post_list_with_post(self):
        post_000 = create_post(
            title ='The first tet post',
            content = 'first post content',
            author = self.author_000,
        )

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category()
        )

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertGreater(Post.objects.count(),0)
        self.assertIn(post_000.title, soup.body.text)

        post_000_read_more_btn = soup.body.find('button', id='read-more-post-{}'.format(post_000.pk))
        self.assertIn(post_000.get_absolute_url(), post_000_read_more_btn['onclick'],)

        # check post list navbar
        self.check_navbar(soup=soup)

        # check post list side categories
        self.check_side_categories(soup=soup)

        # check post list categories
        main_div = soup.body.find('div', id='main_div')
        self.assertIn('No Category', main_div.text)
        self.assertIn('Jazz', main_div.text)



    def test_detail_post(self):

        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category()
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertIn(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, '{} - Blog'.format(post_000.title))

        post_000_main_div = soup.body.find('div', id='main_div')
        self.assertIn(post_000.title, post_000_main_div.text)

        # check detail page navbar
        self.check_navbar(soup=soup)

        # check detail page categories
        self.check_side_categories(soup=soup)




