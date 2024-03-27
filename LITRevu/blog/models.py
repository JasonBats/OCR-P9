from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime


class Book(models.Model):
    current_year = datetime.date.today().year
    title = models.CharField(max_length=255, blank=False, verbose_name='Titre')
    author = models.CharField(max_length=100, blank=False, verbose_name='Auteur')
    date = models.IntegerField(verbose_name='Date de publication', validators=[MinValueValidator(0), MaxValueValidator(current_year)])
    book_cover = models.ImageField(verbose_name='Couverture')

    def __str__(self):
        return f'Titre du livre : {self.title}'


class Ticket(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date de publication')
    book = models.ForeignKey(Book, null=True, on_delete=models.SET_NULL, blank=False, verbose_name='Livre')

    def __str__(self):
        return f'Demande de critique à propos de : {self.book.title}'


class Review(models.Model):

    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date de publication')
    title = models.CharField(max_length=64, blank=False, verbose_name='Titre de la critique')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Note')
    book = models.ForeignKey(Book, null=False, on_delete=models.PROTECT, blank=False)
    ticket = models.ForeignKey(Ticket, null=True, blank=True, on_delete=models.SET_NULL)
    review_text = models.CharField(max_length=1000, blank=False, verbose_name='Votre critique')

    def __str__(self):
        return f'Critique de : {self.book.title}'

