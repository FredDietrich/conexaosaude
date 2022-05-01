from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    #path('forgot', views.forgotPassword, name='forgotPassword'),
    path('twofactor', views.twoFactor, name='twoFactor'),
    path('register', views.register, name='register'),
    path('newcode', views.newcode, name='newcode'),
    path('logout', views.logout, name='logout'),
    path('user', views.user, name='user'),
    path('bloodpressure', views.bloodpressure, name='bloodpressure'),
    path('glucose', views.glucose, name='glucose'),
    path('weight', views.weight, name='weight'),
    path('vaccines', views.vaccines, name='vaccines'),
    path('changevaccinestatus', views.changevaccinestatus, name='changevaccinestatus')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
