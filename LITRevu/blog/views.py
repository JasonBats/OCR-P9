from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication import models as auth_models
from django.views.decorators.http import require_http_methods
from .utils import block_unblock_method, stop_following_me_method, follow_unfollow_method

from . import forms, models
import datetime


@login_required
def home(request):
    """
    Displays items regarding relations to other users (blocked, followed etc.),
     and their types (review or tickets) after the homepage rules.
    :param request:
    :return: Sorted feed
    """
    user = request.user
    user_followers = user.followers.all()
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    feed = []
    blocked_by = []
    for blocking_user in user.blocked_by.all():
        blocked_by.append(blocking_user)
    for ticket in tickets:
        ticket_details = (ticket, 'ticket')
        if ticket.author in user_followers or ticket.author == user:
            feed.append(ticket_details)
    for review in reviews:
        review_details = (review, 'review')
        if review.author not in user.blocked_by.all():
            if review.author in user_followers or review.author == user:
                feed.append(review_details)
            if review.ticket:
                if review.ticket.author == user and review_details not in feed:
                    feed.append(review_details)
    sorted_feed = sorted(feed, key=lambda item: item[0].date, reverse=True)
    return render(request, 'blog/home.html',
                  context={'feed': sorted_feed,
                           'user_followers': user_followers,
                           'user': user,
                           }
                  )


@login_required
def posts(request):
    """
    Displays items regarding relations to other users (blocked, followed etc.),
     and their types (review or tickets) after the posts page rules.
    :param request:
    :return: Sorted feed
    """
    current_user = request.user
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    feed = []
    blocked_by = []
    for blocking_user in current_user.blocked_by.all():
        blocked_by.append(blocking_user)
    for ticket in tickets:
        if ticket.author != current_user and ticket.author not in blocked_by:
            ticket_details = (ticket, 'ticket')
            feed.append(ticket_details)
    for review in reviews:
        if review.author != current_user and review.author not in blocked_by:
            review_details = (review, 'review')
            feed.append(review_details)
    sorted_feed = sorted(feed, key=lambda item: item[0].date, reverse=True)
    return render(request, 'blog/home.html',
                  context={'feed': sorted_feed,
                           'user': current_user,
                           }
                  )


@login_required
def create_ticket(request):
    """
    Displays the book creation form to create a ticket. Book information are
    informed by the user and ticket information are automatically created.
    :param request:
    :return: Ticket creation view
    """
    form = forms.CreateBookForm(initial={'submitted_by': request.user})
    if request.method == 'POST':
        form = forms.CreateBookForm(request.POST, request.FILES)
        if form.is_valid():
            now = datetime.datetime.now()
            book_instance = form.save(commit=False)
            book_instance.submitted_by = request.user
            book_instance.save()
            ticket_instance = models.Ticket.objects.create(
                author=request.user,
                book=book_instance,
                date=now
            )
            models.Ticket.objects.filter(id=ticket_instance.id).update(
                date=datetime.datetime.now()
            )
            return render(request, 'blog/ticket_confirmation.html',
                          context={'book': book_instance}
                          )

    return render(request, 'blog/create_ticket.html',
                  context={'form': form}
                  )


@login_required
def create_review(request):
    """
    Displays the review creation form. Book information are selected among
     the existing books or created with an optional book form.
    :param request:
    :return: Review creation view
    """
    review_form = forms.CreateReviewForm()
    book_form = forms.CreateBookOptionalForm(initial={
        'submitted_by': request.user
    })
    if request.method == 'POST':
        review_form = forms.CreateReviewForm(request.POST)
        book_form = forms.CreateBookOptionalForm(
            request.POST,
            request.FILES,
            initial={
                'submitted_by': request.user
            }
        )
        if review_form.is_valid():
            if request.POST['book']:
                review_instance = models.Review.objects.create(
                    author=request.user,
                    date=datetime.datetime.now(),
                    review_title=review_form.cleaned_data['review_title'],
                    rating=review_form.cleaned_data['rating'],
                    book=review_form.cleaned_data['book'],
                    ticket=review_form.cleaned_data['ticket'],
                    review_text=review_form.cleaned_data['review_text'],
                )
                models.Review.objects.filter(id=review_instance.id).update(
                    date=datetime.datetime.now()
                )
            elif book_form.is_valid():
                book_instance = book_form.save()
                review_instance = review_form.save(commit=False)
                review_instance.author = request.user
                review_instance.date = datetime.datetime.now()
                review_instance.book = book_instance
                review_instance.save()
                models.Review.objects.filter(id=review_instance.id).update(
                    date=datetime.datetime.now()
                )

            return redirect('home')

    return render(request, 'blog/create_review.html',
                  context={'review_form': review_form,
                           'book_form': book_form}
                  )


@login_required
def create_review_answer_ticket(request, book_id, ticket_id):
    """
    Displays the review creation form where a book, and a ticket are instantiated.
    :param request:
    :param book_id:Int
        Id of the reviewed book
    :param ticket_id:Int
        Id of the answered ticket
    :retun: Review creation view.
    """
    book = models.Book.objects.get(id=book_id)
    ticket = models.Ticket.objects.get(id=ticket_id)
    review_form = forms.CreateReviewFormAnswerTicket()
    review_form.book = book
    if request.method == 'POST':
        review_form = forms.CreateReviewFormAnswerTicket(request.POST)
        review_form.book = book_id
        if review_form.is_valid():
            review_instance = models.Review.objects.create(
                author=request.user,
                date=datetime.datetime.now(),
                review_title=review_form.cleaned_data['review_title'],
                rating=review_form.cleaned_data['rating'],
                book=book,
                ticket=ticket,
                review_text=review_form.cleaned_data['review_text'],
            )
            models.Review.objects.filter(id=review_instance.id).update(
                date=datetime.datetime.now()
            )
            return redirect('home')
    return render(request, 'blog/create_review_answer_ticket.html',
                  context={'review_form': review_form,
                           'book': book,
                           'ticket': ticket}
                  )


@login_required
def book_details(request, book_id):
    """
    Displays book details, used in various pages (i.e., ticket details
    or review details views)
    :param request:
    :param book_id:Int
        Id of detailed book to display.
    :return: View of book details.
    """
    book = models.Book.objects.get(id=book_id)
    return render(request, 'blog/book_details.html',
                  context={'book': book}
                  )


@login_required
def item_details(request, item_id, item_type):
    """
    Displays the details of the item, whether it is a ticket or a review.
    :param request:
    :param item_id:
    :param item_type:str
        'ticket' or 'review', for templating purposes.
    :return: A detailed page of the item.
    """
    reviews_to_display = []
    if item_type == 'ticket':
        item = models.Ticket.objects.get(id=item_id)
        details_type = 'ticket'
        reviews_to_display = models.Review.objects.all().filter(ticket_id=item_id)
    elif item_type == 'review':
        item = models.Review.objects.get(id=item_id)
        details_type = 'review'
    book = item.book
    return render(request, 'blog/item_details.html',
                  context={'item': item,
                           'book': book,
                           'details_type': details_type,
                           'reviews_to_display': reviews_to_display}
                  )


@login_required
def relations(request):
    """
    Displays the main page to manage the relations between users.
    Displays a search bar where all users can be reached, and all the existing
    foreignkeys between current user and others (blocking / blocked_by,
    and followed by / followed).
    Those relations can be modified in this view.
    :param request:
    :return: Relations page view.
    """
    current_user = request.user
    users = auth_models.User.objects.all()
    public_users = []
    search_form = forms.SearchUserForm()
    for user in users:
        if not user.is_staff:
            public_users.append(user)
    if not current_user.is_staff:
        public_users.remove(current_user)
    sorted_users = sorted(public_users, key=lambda u: u.username)
    followed_users = request.user.followers.all()
    followed_by = request.user.followed_by.all()
    blocked_users = request.user.blocking.all()
    blocked_by = request.user.blocked_by.all()
    return render(request,
                  'blog/relations.html',
                  context={'sorted_users': sorted_users,
                           'followed_users': followed_users,
                           'current_user': current_user,
                           'followed_by': followed_by,
                           'blocked_users': blocked_users,
                           'blocked_by': blocked_by,
                           'search_form': search_form,
                           })


@login_required
def follow_unfollow(request):
    follow_unfollow_method(request)
    return redirect('relations')


def stop_following_me(request):
    stop_following_me_method(request)
    return redirect('relations')


@login_required
@require_http_methods(["POST"])
def block_unblock(request):
    block_unblock_method(request)
    return redirect('relations')


@login_required
def edit_ticket(request, ticket_id, book_id):
    """
    Edit an existing ticket using the ticket form instantiated.
    :param request:
    :param ticket_id:Int.
    :param book_id:Int.
    :return: Edit ticket view page.
    """
    ticket = models.Ticket.objects.get(id=ticket_id)
    book = models.Book.objects.get(id=book_id)
    if request.method == 'POST':
        form = forms.EditBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            models.Ticket.objects.filter(id=ticket_id).update(
                date=datetime.datetime.now()
            )
            return redirect('home')
    else:
        form = forms.EditBookForm(instance=book)
    return render(request, 'blog/edit_ticket.html',
                  context={'form': form,
                           'book': book,
                           'ticket': ticket}
                  )


@login_required
def edit_review(request, review_id, book_id):
    """
    Edit an existing ticket using the review form instantiated.
    :param request:
    :param review_id:Int.
    :param book_id:Int.
    :return: Edit review view page.
    """
    current_user = request.user
    review = models.Review.objects.get(id=review_id)
    book = models.Book.objects.get(id=book_id)
    review_form = forms.EditReviewForm(instance=review)
    if request.method == 'POST':
        book_form = forms.CreateBookOptionalForm(request.POST,
                                                 request.FILES,
                                                 instance=book
                                                 )
        review_form = forms.EditReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review_form.save()
            models.Review.objects.filter(id=review_id).update(
                date=datetime.datetime.now()
            )
        if request.POST['book']:
            if book_form.is_valid():
                book_form.save()
                return redirect('home')
            else:
                for field, errors in book_form.errors.items():
                    print(f"Field '{field}': {', '.join(errors)}")

        return redirect('home')

    else:
        book_form = forms.CreateBookOptionalForm(instance=book)
    return render(request, 'blog/edit_review.html',
                  context={'book_form': book_form,
                           'review_form': review_form,
                           'book': book,
                           'review': review,
                           'current_user': current_user}
                  )


@login_required
def delete_item(request, item_id, item_type):
    """
    A quick form displayed as a button to delete an item, whether it is a
    ticket or a review.
    :param request:
    :param item_id:Int.
    :param item_type:Str.
        'ticket' or 'review' to filter objects of the right type.
    :return: Delete form.
    """
    if item_type == 'ticket':
        item = models.Ticket.objects.get(id=item_id)
    elif item_type == 'review':
        item = models.Review.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('home')

    return render(request, 'blog/delete_ticket.html',
                  context={'item': item})


@login_required
def just_book_form(request):
    """
    Isolated book creation form for where it is optional
    (review creation page).
    :param request:
    :return: Isolated book form.
    """
    form = forms.CreateBookOptionalForm(initial={'submitted_by': request.user})
    return render(request, 'blog/isolated_book_form.html',
                  context={'form': form}
                  )
