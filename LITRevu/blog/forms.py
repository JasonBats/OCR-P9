from django import forms
import authentication.models as auth_models
from . import models


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['author', 'book']
        widgets = {
            'book': forms.HiddenInput(),
            'author': forms.HiddenInput(),
        }


class CreateBookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['title', 'author', 'date', 'book_cover']


class CreateReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ['review_title', 'rating', 'book', 'ticket', 'review_text']
        widgets = {
            'review_text': forms.Textarea(),
        }


class EditBookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['title', 'author', 'date', 'book_cover']
