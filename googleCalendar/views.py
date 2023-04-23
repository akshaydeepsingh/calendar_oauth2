from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from .config.app_config import metadata
from .config.resp import api_response
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']
REDIRECT_URL = 'http://127.0.0.1:8000/rest/v1/calendar/redirect/'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = os.environ['CLIENT_SECRETS_FILE']


@api_view(['GET'])
def GoogleCalendarInitView(request):
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = REDIRECT_URL

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true'
    )
    # Store the state so the callback can verify auth server response
    request.session['state'] = state
    return Response( api_response('success', 200, 'authorization_url generated', {"authorization_url": authorization_url} , metadata, request.build_absolute_uri()))
   


@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    state = request.session['state']
    # Verify authorization server response
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URL
    # Use the authorization server's response to fetch the tokens.
    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)
    # Store the credentials in the session.
    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    if 'credentials' not in request.session:
        return redirect('rest/v1/calendar/init/')
    else:
        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])
    # The Discovery API provides a list of Google APIs and a machine-readable "Discovery Document" for each API
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    # Returns the calendars on the user's calendar list
    calendar_list = service.calendarList().list().execute()
    user_email = calendar_list['items'][0]['id']
    # Getting all events of a user 
    events  = service.events().list(calendarId=user_email).execute()
    event_lists = []
    if 'items' not in events:
        return Response(api_response('error', 400, 'data not found', [] , metadata, REDIRECT_URL))
    for event in events['items']:
        event_lists.append(event)
    if not event_lists:
       return Response(api_response('error', 400, 'events not found', [] , metadata, REDIRECT_URL))
    else:
        return Response(api_response('success', 200, 'Data retrieved successfully', {'event_lists': event_lists} , metadata, REDIRECT_URL))
       
        