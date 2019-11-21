import json

from datetime import date

from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from drchrono.endpoints import (
    DoctorEndpoint,
    PatientEndpoint,
    AppointmentEndpoint
)

class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def __init__(self):
        self.access_token = self.get_token()
        return super(DoctorWelcome, self).__init__()

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get_doctor(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        api = DoctorEndpoint(self.access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_patients(self):
        return PatientEndpoint(self.access_token).list()

    def get_appointments(self):
        return AppointmentEndpoint(self.access_token).list(date=date.today())

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        #doctor_details = self.make_api_request()
        kwargs['doctor'] = json.dumps(self.get_doctor())
        kwargs['appointments'] = json.dumps(list(self.get_appointments()))
        kwargs['patients'] = json.dumps(list(self.get_patients()))
        kwargs['access_token'] = self.access_token
        return kwargs


class DoctorViewSet(ViewSet):
    """
    ViewSet to wrap the DoctorEndpoint
    """
    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def list(self, request):
        doctors = list(DoctorEndpoint(self.get_token()).list())
        return Response(doctors)

    def retrieve(self, request, pk=None):
        doctor = DoctorEndpoint(self.get_token()).fetch(pk)
        return Response(doctor)


class PatientViewSet(ViewSet):
    """
    ViewSet to wrap the PatientEndpoint
    """
    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def list(self, request):
        patients = list(PatientEndpoint(self.get_token()).list())
        return Response(patients)

    def retrieve(self, request, pk=None):
        patient = PatientEndpoint(self.get_token()).fetch(pk)
        return Response(patient)


class AppointmentViewSet(ViewSet):
    """
    ViewSet to wrap the AppointmentEndpoint
    """
    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    @property
    def client(self):
        return AppointmentEndpoint(self.get_token())

    def list(self, request):
        """
        Only get todays appointments by default
        """
        todays_appointments = self.client.list(date=date.today())
        return Response(list(todays_appointments))

    def retrieve(self, request, pk):
        appointment = self.client.fetch(pk)
        return Response(appointment)

    def update(self, request, pk):
        appointment = self.client.update(pk, request.data)
        return Response(appointment)
