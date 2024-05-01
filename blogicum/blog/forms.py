from django import forms
from django.core.mail import send_mail
from blog.models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'location', 'category', 'pub_date')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}
            )
        }

    def clean(self):
        super().clean()
        send_mail(
            subject='Тема письма',
            message='Текст сообщения',
            from_email='blogicum@example.com',
            recipient_list=['to@example.com'],
            fail_silently=True,
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
