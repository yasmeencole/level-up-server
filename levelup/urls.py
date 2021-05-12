from django.urls import path
from django.conf.urls import include
from levelupapi.views import register_user, login_user
from rest_framework import routers
from django.contrib import admin
from levelupapi.views import GameTypeView
from levelupapi.views.game import GameView
from levelupapi.views import EventView
from levelupapi.views import ProfileView


# this parses the urls
# the register_user and login_user functions are imported into the module. Then they are used to map a route to that view.
router = routers.DefaultRouter(trailing_slash=False)
# /gametypes?label=blue
router.register(r'gametypes', GameTypeView, 'gametype')
router.register(r'games', GameView, 'game')
router.register(r'events', EventView, 'event')
router.register(r'profile', ProfileView, 'profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework'))
]