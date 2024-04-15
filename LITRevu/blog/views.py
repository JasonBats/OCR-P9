from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import authentication.models as auth_models
from . import forms, models
import datetime


@login_required
def home(request):
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
    review_form = forms.CreateReviewForm()
    book_form = forms.CreateBookOptionalForm(initial={
        'submitted_by': request.user
    })
    if request.method == 'POST':
        review_form = forms.CreateReviewForm(request.POST)
        book_form = forms.CreateBookOptionalForm(request.POST,
                                                 request.FILES,
                                                 initial={
                                                     'submitted_by': request.user})
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
    book = models.Book.objects.get(id=book_id)
    return render(request, 'blog/book_details.html',
                  context={'book': book}
                  )


@login_required
def item_details(request, item_id, item_type):
    reviews_to_display = []
    if item_type == 'ticket':
        item = models.Ticket.objects.get(id=item_id)
        details_type = 'ticket'
        reviews_to_display = []
        associated_reviews = models.Review.objects.all()
        for review in associated_reviews:
            if review.ticket_id == item_id:
                reviews_to_display.append(review)
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
    if request.method == 'POST':
        user = request.user
        followers = []
        for other_member in user.followers.all():
            followers.append(other_member)
        user_to_verify = request.POST.get('user_to_verify')
        user_to_verify = auth_models.User.objects.get(pk=user_to_verify)
        if user_to_verify not in followers:
            user.followers.add(user_to_verify)
        else:
            user.followers.remove(user_to_verify)

    return redirect('relations')


def stop_following_me(request):
    if request.method == 'POST':
        user = request.user
        followed_by = []
        for other_member in user.followed_by.all():
            followed_by.append(other_member)
        user_to_verify = request.POST.get('user_to_verify')
        user_to_verify = auth_models.User.objects.get(pk=user_to_verify)
        user_to_verify.followers.remove(user)

    return redirect('relations')


@login_required
def block_unblock(request):
    if request.method == 'POST':
        user = request.user
        blocking = []
        for other_member in user.blocking.all():
            blocking.append(other_member)
        user_to_verify = request.POST.get('user_to_verify')
        user_to_verify = auth_models.User.objects.get(pk=user_to_verify)
        if user_to_verify not in blocking:
            user.blocking.add(user_to_verify)
            if user in user_to_verify.followers.all():
                user_to_verify.followers.remove(user)
            if user_to_verify in user.followers.all():
                user.followers.remove(user_to_verify)
        else:
            user.blocking.remove(user_to_verify)

    return redirect('relations')


@login_required
def edit_ticket(request, ticket_id, book_id):
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
    form = forms.CreateBookOptionalForm(initial={'submitted_by': request.user})
    return render(request, 'blog/isolated_book_form.html',
                  context={'form': form}
                  )


def search_user_filter(request):
    current_user = request.user
    search_query = request.GET.get('search', '')
    all_users = auth_models.User.objects.all().exclude(
        username__icontains=current_user.username,
        ).filter(is_staff__exact=0)
    print(all_users)
    found_users = all_users.filter(username__icontains=search_query)
    serialized_users = list(found_users.values())
    return JsonResponse({'users': serialized_users})

# TODO : Validation W3C html / css
