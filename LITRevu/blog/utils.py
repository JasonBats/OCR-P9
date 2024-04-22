import authentication.models as auth_models
from django.http import JsonResponse


def follow_unfollow_method(request):
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


def stop_following_me_method(request):
    if request.method == 'POST':
        user = request.user
        followed_by = []
        for other_member in user.followed_by.all():
            followed_by.append(other_member)
        user_to_verify = request.POST.get('user_to_verify')
        user_to_verify = auth_models.User.objects.get(pk=user_to_verify)
        user_to_verify.followers.remove(user)


def block_unblock_method(request):
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


def search_user_method(request):
    current_user = request.user
    search_query = request.GET.get('search', '')
    all_users = auth_models.User.objects.all().exclude(
        username__icontains=current_user.username).filter(is_staff__exact=0)
    all_users = all_users.exclude(id__in=current_user.blocked_by.all())
    found_users = all_users.filter(username__icontains=search_query)
    serialized_users = list(found_users.values())
    return JsonResponse({'users': serialized_users})
