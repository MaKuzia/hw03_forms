from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='AuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(1, 12, 1):
            Post.objects.create(
                group=cls.group,
                author=cls.user_author,
                text=f'Тестовый пост_{i} (*^▽^*)'
            )
        cls.post = Post.objects.get(pk=1)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsPagesTests.post.author)
        self.just_user = User.objects.create_user(username='JustUser')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.just_user)

    def test_pages_uses_correct_template(self):
        """ В view-функциях используются правильные html-шаблоны"""

        id_post = PostsPagesTests.post.pk
        templatets_pages_name = {
            reverse('posts:index'): 'posts/index.html',

            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group.slug}):
            'posts/group_list.html',

            reverse('posts:profile', kwargs={'username': 'AuthUser'}):
            'posts/profile.html',

            reverse('posts:post_detail', kwargs={'post_id': id_post}):
            'posts/post_detail.html',

            reverse('posts:post_create'): 'posts/create_post.html',

            reverse('posts:post_edit', kwargs={'post_id': id_post}):
            'posts/create_post.html',
        }
        for reverse_name, templates in templatets_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, templates)

    def test_post_detail_pages_show_correct_context(self):
        """соответствует ли ожиданиям словарь context,
            передаваемый в шаблон при вызове конкретного поста (post_detail)"""

        response = (self.authorized_user.get(reverse('posts:post_detail',
                    kwargs={'post_id': PostsPagesTests.post.pk})))
        self.assertEqual(response.context.get('post').group.title,
                         PostsPagesTests.post.group.title)
        self.assertEqual(response.context.get('post').author.username,
                         PostsPagesTests.post.author.username)  # get_username
        self.assertEqual(response.context.get('post').text,
                         PostsPagesTests.post.text)

    def test_post_create_show_correct_context(self):
        """шаблон post_create сформирован с правильным контекстом
            при создании/редактировании поста"""

        url_with_forms = (
            reverse('posts:post_create'),
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsPagesTests.post.pk})
        )
        for space_name in url_with_forms:
            with self.subTest(space_name=space_name):
                response = self.authorized_author.get(space_name)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        """ Тестирование паджинатора (на 1-ой странице 10 постов)
         + содержимое постов на странице соответствует ожиданиям
            - на главной странице сайта,
            - на странице выбранной группы,
            - в профайле пользователя"""

        new_post = Post.objects.create(
            group=PostsPagesTests.group,
            author=PostsPagesTests.user_author,
            text='New post (☆▽☆)'
        )
        paginator_difrent_page = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.user_author.username})
        )
        for space_name in paginator_difrent_page:
            with self.subTest(space_name=space_name):
                response = self.authorized_user.get(space_name)
                self.assertIn(new_post, response.context['page_obj'])
                self.assertEqual(len(response.context['page_obj']), 10)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.group.title, 'Тестовая группа')
                self.assertEqual(first_object.text, 'New post (☆▽☆)')
                self.assertEqual(first_object.group.slug, 'test-slug')

    def test_second_page_contains_one_record(self):
        paginator_difrent_pafe = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostsPagesTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostsPagesTests.user_author.username})
        )
        for space_name in paginator_difrent_pafe:
            with self.subTest(space_name=space_name):
                response = self.authorized_user.get(space_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)
