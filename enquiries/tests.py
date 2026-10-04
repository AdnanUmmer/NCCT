import time
import uuid
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.db import OperationalError
from django.test import TestCase, Client, override_settings
from .models import Enquiry, RateWindow
from .security import issue_token

class EnquiryTests(TestCase):
    def payload(self, **changes):
        value = {'name':'Test Architect','company_name':'QA Studio','email':'architect@example.test','phone':'+971 50 123 4567',
                 'project_type':'Commercial','message':'Testing the local enquiry workflow.','consent':'on','website':'',
                 'token':signing.dumps({'id':str(uuid.uuid4()),'started':time.time()-10},salt='enquiry')}
        value.update(changes)
        return value

    def post(self, data=None):
        return self.client.post('/enquiry/', data or self.payload(), HTTP_ACCEPT='application/json')

    def test_success_persists_consent_and_normalises(self):
        response = self.post(self.payload(email='ARCHITECT@example.test'))
        self.assertEqual(response.status_code,200)
        e=Enquiry.objects.get();self.assertTrue(e.consent);self.assertEqual(e.phone,'+971501234567');self.assertEqual(e.email,'architect@example.test');self.assertEqual(e.source_page,'/')

    def test_csrf_rejects_missing_and_accepts_valid(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/enquiry/',self.payload(),HTTP_ACCEPT='application/json').status_code,403)
        client.get('/')
        data=self.payload();data['csrfmiddlewaretoken']=client.cookies['csrftoken'].value
        self.assertEqual(client.post('/enquiry/',data,HTTP_ACCEPT='application/json').status_code,200)

    def test_required_and_email_phone_validation(self):
        for changes,field in [({'name':''},'name'),({'company_name':''},'company_name'),({'email':'bad'},'email'),({'phone':'abc123'},'phone'),({'phone':'123'},'phone'),({'consent':''},'consent')]:
            with self.subTest(field=field):
                r=self.post(self.payload(**changes));self.assertEqual(r.status_code,400);self.assertIn(field,r.json()['errors'])
        self.assertFalse(Enquiry.objects.exists())

    def test_rejects_unknown_project_type_and_long_message(self):
        self.assertIn('project_type',self.post(self.payload(project_type='Invented')).json()['errors'])
        self.assertIn('message',self.post(self.payload(message='x'*4001)).json()['errors'])

    def test_honeypot(self):
        self.assertEqual(self.post(self.payload(website='spam')).status_code,400)
        self.assertFalse(Enquiry.objects.exists())

    def test_signed_minimum_time(self):
        self.assertEqual(self.post(self.payload(token=issue_token())).status_code,400)
        self.assertFalse(Enquiry.objects.exists())

    def test_tampered_and_expired_token(self):
        self.assertEqual(self.post(self.payload(token='tampered')).status_code,400)
        with patch('django.core.signing.time.time',return_value=time.time()-7200):
            expired=signing.dumps({'id':str(uuid.uuid4()),'started':time.time()-7200},salt='enquiry')
        self.assertEqual(self.post(self.payload(token=expired)).status_code,400)

    def test_replay_and_duplicate_content(self):
        data=self.payload()
        self.assertEqual(self.post(data).status_code,200)
        self.assertEqual(self.post(data).status_code,200)
        self.assertEqual(self.post(self.payload()).status_code,200)
        self.assertEqual(Enquiry.objects.count(),1)

    @override_settings(ENQUIRY_RATE_LIMIT=2)
    def test_rate_limit_is_database_backed(self):
        self.post();self.post()
        response=self.post();self.assertEqual(response.status_code,429);self.assertEqual(response['Retry-After'],'600')
        self.assertEqual(RateWindow.objects.get().count,2)

    def test_does_not_trust_forwarded_ip(self):
        self.client.post('/enquiry/',self.payload(),HTTP_X_FORWARDED_FOR='1.2.3.4')
        self.client.post('/enquiry/',self.payload(),HTTP_X_FORWARDED_FOR='8.8.8.8')
        self.assertEqual(RateWindow.objects.count(),1)

    def test_html_is_stripped(self):
        self.post(self.payload(name='<b>Architect</b>',message='<img src=x onerror=alert(1)>Requirements'))
        self.assertEqual(Enquiry.objects.get().name,'Architect');self.assertEqual(Enquiry.objects.get().message,'Requirements')

    def test_plain_html_fallback(self):
        self.assertRedirects(self.client.post('/enquiry/',self.payload()),'/?enquiry=sent#contact')
        response=self.client.post('/enquiry/',self.payload(email='bad'))
        self.assertEqual(response.status_code,400);self.assertContains(response,'Enter a valid email address',status_code=400)

    def test_storage_failure_is_retryable(self):
        with patch('enquiries.views.rate_allowed',side_effect=OperationalError('test outage')):
            self.assertEqual(self.post().status_code,503)

    def test_token_endpoint_and_methods(self):
        r=self.client.get('/enquiry/token/');self.assertIn('token',r.json());self.assertIn('no-store',r['Cache-Control'])
        self.assertEqual(self.client.get('/enquiry/').status_code,405)
        self.assertEqual(self.client.post('/enquiry/token/').status_code,405)

    def test_admin_requires_authentication_and_supports_status(self):
        self.post()
        self.assertEqual(self.client.get('/admin/enquiries/enquiry/').status_code,302)
        user=get_user_model().objects.create_superuser('qa','qa@example.test','temporary-test-password')
        self.client.force_login(user)
        self.assertContains(self.client.get('/admin/enquiries/enquiry/'),'QA Studio')
        e=Enquiry.objects.get()
        self.assertEqual(self.client.post(f'/admin/enquiries/enquiry/{e.pk}/change/',{'status':'contacted','_save':'Save'}).status_code,302)
        e.refresh_from_db();self.assertEqual(e.status,'contacted')


    @override_settings(EMAIL_HOST='smtp.example.test', ENQUIRY_NOTIFICATION_EMAIL='team@example.test')
    def test_email_failure_does_not_lose_enquiry(self):
        with patch('enquiries.notifications.send_mail', side_effect=RuntimeError('SMTP unavailable')):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 1)
