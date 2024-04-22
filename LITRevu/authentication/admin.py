from django.contrib import admin
from authentication.models import User
from blog.models import Book, Review, Ticket

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Ticket)
