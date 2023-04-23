from django.http import JsonResponse
from django.views import  View
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

baseUrl = "http://localhost:8000"

class GoogleCalendarInitView(View):

    def get(self, request, *args, **kwargs):
        # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = InstalledAppFlow.from_client_secrets_file(
            os.path.join(os.getcwd(), 'client_secret.json'),
            scopes=['https://www.googleapis.com/auth/calendar.events']
        )
        flow.redirect_uri = baseUrl+'/rest/v1/calendar/redirect'

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )

        print(authorization_url)
        request.session['state'] = state

        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):

    def get(self, request, *args, **kwargs):

        state = request.GET.get('state')
        print(state)
        flow = InstalledAppFlow.from_client_secrets_file(
            './client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            state=state
        )
        flow.redirect_uri = baseUrl + '/rest/v1/calendar/redirect'

        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes
        }

        service = build('calendar', 'v3', credentials=Credentials(**credentials))

        timeMin = '2022-01-01T00:00:00-07:00'

        events_result = service.events().list(calendarId='primary', timeMin=timeMin,
                                              maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        return JsonResponse({'status': 'success',
                             'message': 'Events have been fetched.',
                             'data': events
                             })

