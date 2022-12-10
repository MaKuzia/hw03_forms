from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ('text', 'group')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['cols'] = 92
        self.fields['text'].widget.attrs['rows'] = 10

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.isdigit() or data.isspace():
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data
