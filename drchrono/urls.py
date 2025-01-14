from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin

from rest_framework.routers import DefaultRouter

import views

router = DefaultRouter()
router.register(r'doctors', views.DoctorViewSet, basename='doctors')
router.register(r'appointments', views.AppointmentViewSet, basename='appointments')

admin.autodiscover()

urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include((router.urls, 'api'))),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
