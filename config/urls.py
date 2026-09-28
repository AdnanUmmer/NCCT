from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core.views import home, robots
from enquiries.views import submit, token

urlpatterns = [path('', home, name='home'), path('admin/', admin.site.urls),
               path('enquiry/', submit, name='enquiry'), path('enquiry/token/', token, name='enquiry-token'),
               path('robots.txt', robots)]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'core.views.not_found'
admin.site.site_header = 'NCCT · Content & enquiries'
admin.site.site_title = 'NCCT DXB'
admin.site.index_title = 'Homepage administration'
