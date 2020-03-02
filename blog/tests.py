from django.test import TestCase, Client
from blog.models import Post, Category, Tag, Comment
from django.utils import timezone
from django.contrib.auth.models import User

from bs4 import BeautifulSoup


# Create your tests here.
def create_category(name="Jazz", description=''):
    category, iscreated = Category.objects.get_or_create(
        name=name,
        description=description,
    )
    category.slug = name.lower().replace(' ', '-').replace('/', '')
    category.save()
    return category


def create_tag(name='blue_note', description=''):
    tag, iscreated = Tag.objects.get_or_create(
        name=name,
        description=description,
    )
    tag.slug = name.lower().replace(' ', '-').replace('/', '')
    tag.save()
    return tag


def create_post(title, content, author, category=None):
    return Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category
    )


def create_comment(post, text='', author=None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username='guest',
            password='password'
        )
    comment = Comment.objects.create(
        post=post,
        text=text,
        author=author,
    )

    return comment


class TestModel(TestCase):
    def setUp(self):
        # self.client = Client() ## -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='test')

    def test_create_category(self):
        category_000 = create_category()
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
            category=category_000,
        )
        self.assertEqual(category_000.post_set.count(), 1)

    def test_create_tag(self):
        tag_000 = create_tag()
        tag_001 = create_tag('emc')

        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
        )

        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2)
        self.assertEqual(tag_001.post_set.count(), 2)
        self.assertEqual(tag_001.post_set.first(), post_000)
        self.assertEqual(tag_001.post_set.last(), post_001)


    def test_create_comment(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        comment_000 = create_comment(post_000,'my first test comment!')
        comment_001 = create_comment(post_000,'my second test comment!')

        self.assertEqual(Comment.objects.count(),2)
        self.assertEqual(post_000.comment_set.count(),2)


class TestView(TestCase):

    def setUp(self):
        # self.client = Client() ## -- can be skipped
        self.author_000 = User.objects.create_user(username='smith', password='smith')
        self.author_001 = User.objects.create_user(username='charlie', password='charlie')

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

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('No pages', soup.body.text)

    def test_post_list_with_post(self):
        tag_bluenote = create_tag('blue_note')
        tag_emc = create_tag('emc')
        post_000 = create_post(
            title='The first tet post',
            content='first post content',
            author=self.author_000,
        )

        post_000.tags.add(tag_emc)
        post_000.tags.add(tag_bluenote)
        post_000.save()

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category()
        )
        post_001.tags.add(tag_emc)
        post_001.save()

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertGreater(Post.objects.count(), 0)
        self.assertIn(post_000.title, soup.body.text)

        post_000_read_more_btn = soup.body.find('button', id='read-more-post-{}'.format(post_000.pk))
        self.assertIn(post_000.get_absolute_url(), post_000_read_more_btn['onclick'], )

        # check post list navbar
        self.check_navbar(soup=soup)

        # check post list side categories
        self.check_side_categories(soup=soup)

        # check post list categories
        main_div = soup.body.find('div', id='main-div')
        self.assertIn('No Category', main_div.text)
        self.assertIn('Jazz', main_div.text)

        # check post list tag
        post_000_card = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#{}'.format(tag_emc), post_000_card.text)
        self.assertIn('#{}'.format(tag_bluenote), post_000_card.text)

        # check post list tag
        post_001_card = main_div.find('div', id='post-card-{}'.format(post_001.pk))
        self.assertIn('#{}'.format(tag_emc), post_001_card.text)

    def test_detail_post(self):
        tag_bluenote = create_tag('blue_note')
        tag_emc = create_tag('emc')

        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        post_000.tags.add(tag_emc)
        post_000.tags.add(tag_bluenote)
        post_000.save()

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

        post_000_main_div = soup.body.find('div', id='main-div')
        self.assertIn(post_000.title, post_000_main_div.text)

        # check detail page navbar
        self.check_navbar(soup=soup)

        # check detail page categories
        self.check_side_categories(soup=soup)

        # test comment
        comment_000 = create_comment(post_000,'my first test comment!',author=self.author_000)
        comment_001 = create_comment(post_000,'my second test comment!', author=self.author_001)

        response = self.client.get(post_000_url) # --refresh
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        comment_div = soup.body.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comment_div.text)
        self.assertIn(comment_000.text, comment_div.text)
        self.assertIn(comment_001.author.username, comment_div.text)
        self.assertIn(comment_001.text, comment_div.text)

        # check post list tag
        self.assertIn('#{}'.format(tag_emc), post_000_main_div.text)
        self.assertIn('#{}'.format(tag_bluenote), post_000_main_div.text)

        # edit button check
        post_000_main_div_btn = post_000_main_div.find('button')
        # self.assertNotIn('EDIT', post_000_main_div.text)

        # login test
        login_success = self.client.login(username='smith', password='smith')
        self.assertTrue(login_success)

        response = self.client.get(post_000_url) # --refresh
        soup = BeautifulSoup(response.content, 'html.parser')
        post_000_main_div = soup.body.find('div', id='main-div')

        self.assertIn('EDIT', post_000_main_div.text)

        # comment
        comment_div = post_000_main_div.find('div',id='comment-list')
        comment_000_div = comment_div.find('div',id='comment-id-{}'.format(comment_000.pk))
        self.assertIn('edit',comment_000_div.text)
        self.assertIn('delete',comment_000_div.text)

        comment_001_div = comment_div.find('div',id='comment-id-{}'.format(comment_001.pk))
        self.assertNotIn('edit',comment_001_div.text)
        self.assertNotIn('delete',comment_001_div.text)

    def test_post_list_by_category(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )
        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category(name='Jazz'),
        )

        response = self.client.get(post_001.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(soup.title.text, 'Blog - {}'.format(category_jazz.name))

        main_div = soup.find('div', id='main-div')

        self.assertNotIn('No Category', main_div.text)
        self.assertIn(post_001.category.name, main_div.text)

    def test_post_list_no_category(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category(name='Jazz'),
        )

        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertIn('No Category', main_div.text)
        self.assertNotIn(post_001.category.name, main_div.text)

    def test_post_list_with_tag(self):
        tag_bluenote = create_tag('blue_note')
        tag_emc = create_tag('emc')
        post_000 = create_post(
            title='The first tet post',
            content='first post content',
            author=self.author_000,
        )

        post_000.tags.add(tag_bluenote)
        post_000.save()

        post_001 = create_post(
            title='The second test post',
            content='second post content',
            author=self.author_000,
            category=create_category()
        )
        post_001.tags.add(tag_emc)
        post_001.save()

        response = self.client.get(tag_bluenote.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertIn('#{}'.format(tag_bluenote), main_div.text)
        self.assertNotIn('#{}'.format(tag_emc), main_div.text)

    def test_post_update(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )
        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')
        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('Created', main_div.text)
        self.assertNotIn('Author', main_div.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        side_div = soup.find('div', id='side-div')
        self.assertNotIn('New Post', side_div.text)

        login_success = self.client.login(username='smith', password='smith')
        self.assertTrue(login_success)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        side_div = soup.find('div', id='side-div')
        self.assertIn('New Post', side_div.text)

    def test_new_comment(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment',
            {'text':' my-test-comment'},
            follow=True,
            )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(post_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn('my-test-comment', main_div.text)


    def test_delete_comment(self):
        post_000 = create_post(
            title='The first test post',
            content='first post content',
            author=self.author_000,
        )

        comment00 = create_comment(post_000,'test comment1',self.author_000)
        comment01 = create_comment(post_000,'test comment2',self.author_001)

        self.assertEqual(Comment.objects.count(), 2)

        login_success = self.client.login(username=self.author_000.username, password=self.author_000.username)
        self.assertTrue(login_success)

        ## delete login user comment
        response = self.client.get('/blog/delete_comment/{}'.format(comment00.pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

        ## delete other user comment
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/delete_commnet/{}'.format(comment01.pk), follow=True)
            self.assertEqual(Comment.objects.count(), 1)

        response = self.client.get(post_000.get_absolute_url())

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(comment01.text, main_div.text)



