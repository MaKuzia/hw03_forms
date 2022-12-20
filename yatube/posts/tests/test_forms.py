from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Group, Post
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='AuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostCreateFormTest.user_author)

    def test_post_create_edit(self):
        '''создаётся новая запись в БД, происходит изменение поста в БД'''

        posts_count = Post.objects.count()
        new_post = {
            'group': PostCreateFormTest.group,
            'author': PostCreateFormTest.user_author,
            'text': 'Тестовый пост (*^▽^*)'
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=new_post,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': new_post['author'].username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTest.group,
                author=PostCreateFormTest.user_author,
                text='Тестовый пост (*^▽^*)'
            ).exists()
        )
        edit_post = Post.objects.get(pk=1)
        edit_post = {
            'text': 'Измененный пост (*^▽^*)'
        }
        edit_post.save()
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': new_post.pk}),
            data=edit_post,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': new_post.pk}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTest.group,
                author=PostCreateFormTest.user_author,
                text='Измененный пост (*^▽^*)'
            ).exists()
        )
