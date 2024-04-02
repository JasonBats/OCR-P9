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
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', blog.views.home, name='home'),
    path('posts/', blog.views.posts, name='posts'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('create_ticket/', blog.views.create_ticket, name='create_ticket'),
    path('explore_db/', blog.views.explore_db, name='explore_db'),
    path('blog/books/<int:book_id>/', blog.views.book_details, name='book_details'),
    path('blog/item_details/<str:item_type>/<int:item_id>/', blog.views.item_details, name='item_details'),
    path('create_review/', blog.views.create_review, name='create_review'),
    path('relations/', blog.views.relations, name='relations'),
    path('manage_relations', blog.views.manage_users_relations, name='manage_relations'),
    path('edit_ticket/<int:book_id>/', blog.views.edit_ticket, name='edit_ticket'),
    path('delete_item/<str:item_type>/<int:item_id>/', blog.views.delete_item, name='delete_item'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
