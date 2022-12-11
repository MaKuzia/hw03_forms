from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        lables = {
            'text': 'Пост',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Содержание поста',
            'group': 'Укажите группу (по желанию (‾◡◝))',
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите текст 🐱‍💻'
        )
        self.fields['group'].empty_label = (
            '(‾◡◝)'
        )

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'блин' in data.lower():
            raise forms.ValidationError('Вы имели в виду "блинчик" 🥞?')
        return data
