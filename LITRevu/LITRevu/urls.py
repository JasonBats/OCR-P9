from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
import blog.views
import authentication.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('logout/',
         LogoutView.as_view(next_page='login'),
         name='logout'),
    path('home/',
         blog.views.home,
         name='home'),
    path('posts/',
         blog.views.posts,
         name='posts'),
    path('signup/',
         authentication.views.signup_page,
         name='signup'),
    path('create_ticket/',
         blog.views.create_ticket,
         name='create_ticket'),
    path('blog/books/<int:book_id>/',
         blog.views.book_details,
         name='book_details'),
    path('blog/item_details/<str:item_type>/<int:item_id>/',
         blog.views.item_details,
         name='item_details'),
    path('create_review/',
         blog.views.create_review,
         name='create_review'),
    path('relations/',
         blog.views.relations,
         name='relations'),
    path('follow_unfollow/',
         blog.views.follow_unfollow,
         name='follow_unfollow'),
    path('block_unblock/',
         blog.views.block_unblock,
         name='block_unblock'),
    path('stop_following_me/',
         blog.views.stop_following_me,
         name='stop_following_me'),
    path('edit_ticket/<int:ticket_id>/<int:book_id>/',
         blog.views.edit_ticket,
         name='edit_ticket'),
    path('edit_review/<int:review_id>/<int:book_id>/',
         blog.views.edit_review,
         name='edit_review'),
    path('delete_item/<str:item_type>/<int:item_id>/',
         blog.views.delete_item,
         name='delete_item'),
    path('just_book_form/',
         blog.views.just_book_form,
         name="just_book_form"),
    path('create_review_answer_ticket/<int:book_id>/<int:ticket_id>/',
         blog.views.create_review_answer_ticket,
         name='create_review_answer_ticket'),
    path('search_users/',
         blog.views.search_user_filter,
         name='search_users')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
