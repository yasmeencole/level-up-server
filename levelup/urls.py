from django.conf.urls import include
from django.urls import path
from levelupapi.views import register_user, login_user

# this parses the urls
# the register_user and login_user functions are imported into the module. Then they are used to map a route to that view.
urlpatterns = [
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
]