from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms, models
import datetime


@login_required
def home(request):
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    feed = []
    for ticket in tickets:
        ticket_details = (ticket, 'ticket')
        feed.append(ticket_details)
    for review in reviews:
        review_details = (review, 'review')
        feed.append(review_details)
    sorted_feed = sorted(feed, key=lambda item: item[0].date, reverse=True)
    return render(request, 'blog/home.html', context={'feed': sorted_feed})


def create_ticket(request):
    form = forms.CreateBookForm()
    if request.method == 'POST':
        form = forms.CreateBookForm(request.POST, request.FILES)
        if form.is_valid():
            now = datetime.datetime.now()
            book_instance = form.save()
            ticket_instance = models.Ticket.objects.create(
                author=request.user,
                book=book_instance,
                date=now
            )
            return render(request, 'blog/ticket_confirmation.html', context={'book': book_instance})
    else:
        form1 = forms.CreateBookForm()

    return render(request, 'blog/create_ticket.html', context={'form': form})


def create_review(request):
    review_form = forms.CreateReviewForm()
    if request.method == 'POST':
        review_form = forms.CreateReviewForm(request.POST)
        if review_form.is_valid():
            review_instance = models.Review.objects.create(
                author=request.user,
                date=datetime.datetime.now(),
                title=review_form.cleaned_data['title'],
                rating=review_form.cleaned_data['rating'],
                book=review_form.cleaned_data['book'],
                ticket=review_form.cleaned_data['ticket'],
                review_text=review_form.cleaned_data['review_text'],
            )
            review_instance.save()
            return render(request, 'blog/review_confirmation.html', context={'review': review_instance})
    return render(request, 'blog/create_review.html', context={'review_form': review_form})


def explore_db(request):
    books = models.Book.objects.all()
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    return render(request, 'blog/explore_db.html', context={'books': books, 'tickets': tickets, 'reviews': reviews})


def book_details(request, book_id):
    book = models.Book.objects.get(id=book_id)
    return render(request, 'blog/book_details.html', context={'book': book})


def item_details(request, item_id, item_type):  # item_type pour savoir si il faut taper Ticket.objects.all() ou autre chose. Arrive de home.html
    if item_type == 'ticket':
        item = models.Ticket.objects.get(id=item_id)
        details_type = 'ticket'
    elif item_type == 'review':
        item = models.Review.objects.get(id=item_id)
        details_type = 'review'
    book = item.book
    return render(request, 'blog/item_details.html', context={'item': item, 'book': book, 'details_type': details_type})
