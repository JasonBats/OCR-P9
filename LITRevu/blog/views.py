from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import authentication.models as auth_models
from . import forms, models
import datetime


@login_required
def home(request):
    user = request.user
    user_followers = user.followers.all()
    print(user_followers)
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    feed = []
    for ticket in tickets:
        ticket_details = (ticket, 'ticket')
        if ticket.author in user_followers or ticket.author == user:
            feed.append(ticket_details)
    for review in reviews:
        review_details = (review, 'review')
        if review.author in user_followers or review.author == user:
            feed.append(review_details)
        if review.ticket:
            if review.ticket.author == user and review_details not in feed:
                feed.append(review_details)  # TODO : Ca en fait du if ici...
    sorted_feed = sorted(feed, key=lambda item: item[0].date, reverse=True)
    return render(request, 'blog/home.html',
                  context={'feed': sorted_feed,
                           'user_followers': user_followers,
                           'user': user,
                           }
                  )


def posts(request):
    user = request.user
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    feed = []
    for ticket in tickets:
        if ticket.author != user:
            ticket_details = (ticket, 'ticket')
            feed.append(ticket_details)
    for review in reviews:
        if review.author != user:
            review_details = (review, 'review')
            feed.append(review_details)
    sorted_feed = sorted(feed, key=lambda item: item[0].date, reverse=True)
    return render(request, 'blog/home.html',
                  context={'feed': sorted_feed,
                           'user': user,
                           }
                  )


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
            models.Ticket.objects.filter(id=ticket_instance.id).update(
                date=datetime.datetime.now()
            )
            return render(request, 'blog/ticket_confirmation.html',
                          context={'book': book_instance}
                          )

    return render(request, 'blog/create_ticket.html',
                  context={'form': form}
                  )


def create_review(request):
    review_form = forms.CreateReviewForm()
    book_form = forms.CreateBookForm()
    if request.method == 'POST':
        review_form = forms.CreateReviewForm(request.POST)
        book_form = forms.CreateBookForm(request.POST, request.FILES)
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
            # else:
            #     messages.error(request, 'formulaires pas valides')
            return render(request, 'blog/create_review.html',
                          context={'review_form': review_form,
                                   'book_form': book_form})
    return render(request, 'blog/create_review.html',
                  context={'review_form': review_form,
                           'book_form': book_form}
                  )


def create_review_answer_ticket(request, book_id, ticket_id):
    book = models.Book.objects.get(id=book_id)
    ticket = models.Ticket.objects.get(id=ticket_id)
    review_form = forms.CreateReviewFormAnswerTicket()
    review_form.book = book
    if request.method == 'POST':
        review_form = forms.CreateReviewFormAnswerTicket(request.POST)
        review_form.book = book_id
        if review_form.is_valid():
            print('form is valid oui')
            review_instance = models.Review.objects.create(
                author=request.user,
                date=datetime.datetime.now(),
                review_title=review_form.cleaned_data['review_title'],
                rating=review_form.cleaned_data['rating'],
                book=book,
                ticket=review_form.cleaned_data['ticket'],
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


def explore_db(request):
    books = models.Book.objects.all()
    tickets = models.Ticket.objects.all()
    reviews = models.Review.objects.all()
    return render(request, 'blog/explore_db.html',
                  context={'books': books,
                           'tickets': tickets,
                           'reviews': reviews}
                  )


def book_details(request, book_id):
    book = models.Book.objects.get(id=book_id)
    return render(request, 'blog/book_details.html',
                  context={'book': book}
                  )


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
        print(reviews_to_display)
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


def relations(request):
    current_user = request.user
    users = auth_models.User.objects.all()
    public_users = []
    for user in users:
        if not user.is_staff:
            public_users.append(user)
    public_users.remove(current_user)
    sorted_users = sorted(public_users, key=lambda u: u.username)
    followed_users = request.user.followers.all()
    followed_by = request.user.followed_by.all()
    return render(request,
                  'blog/relations.html',
                  context={'sorted_users': sorted_users,
                           'followed_users': followed_users,
                           'current_user': current_user,
                           'followed_by': followed_by})


def manage_users_relations(request):
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


def edit_ticket(request, ticket_id, book_id):
    ticket = models.Ticket.objects.get(id=ticket_id)
    book = models.Book.objects.get(id=book_id)
    form = forms.EditBookForm(instance=book)
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
        print('passé par else:')
    return render(request, 'blog/edit_ticket.html',
                  context={'form': form,
                           'book': book,
                           'ticket': ticket}
                  )


def edit_review(request, review_id, book_id):
    current_user = request.user
    review = models.Review.objects.get(id=review_id)
    book = models.Book.objects.get(id=book_id)
    book_form = forms.CreateBookOptionalForm(instance=book)
    review_form = forms.EditReviewForm(instance=review)
    if request.method == 'POST':
        book_form = forms.CreateBookOptionalForm(request.POST,
                                                 request.FILES,
                                                 instance=book
                                                 )
        review_form = forms.EditReviewForm(request.POST, instance=review)
        if book_form.is_valid() and review_form.is_valid():
            book_form.save()
            review_form.save()
            models.Review.objects.filter(id=review_id).update(
                date=datetime.datetime.now()
            )
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


def delete_item(request, item_id, item_type):
    print(item_id, item_type)
    if item_type == 'ticket':
        item = models.Ticket.objects.get(id=item_id)
    elif item_type == 'review':
        item = models.Review.objects.get(id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('home')

    return render(request, 'blog/delete_ticket.html',
                  context={'item': item})


def just_book_form(request):
    form = forms.CreateBookOptionalForm()
    return render(request, 'blog/isolated_book_form.html',
                  context={'form': form}
                  )

# TODO : Validation W3C html / css ? Comment faire

# DONE : Image par défaut, resize image, fix préremplissage modification de ticket, fix des heures UTC+2,
# DONE : Refactor lien modifier une review | Fix titre et url des feed_item | Ne pas pouvoir s'auto-follow + fix page posts avec les posts de request.user
# DONE : Ne pas pouvoir modifier un livre qu'on n'a pas posté (ajout champ "submitted_by" à la classe Book
# DONE : View pour répondre directement à un ticket avec formulaire prérempli et immuable
# DONE : Ajouter liste des reviews associées à un ticket
# DONE : Afficher dans le feed les réponses à mes tickets par des users que je ne follow pas
