from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core import catalogue
from core.sitemaps import sitemap
from core.redirects import LEGACY_REDIRECTS, CATEGORY_LEGACY, category_redirect
from django.views.generic import RedirectView
from core.views import home, robots
from enquiries.views import submit, token

urlpatterns = [path('', home, name='home'), path('admin/', admin.site.urls),
               path('enquiry/', submit, name='enquiry'), path('enquiry/token/', token, name='enquiry-token'),
               path('robots.txt', robots)]
urlpatterns += [
    path('products/', catalogue.products, name='products'),
    path('products/<slug:category_slug>/', catalogue.products, name='product-category'),
    path('products/<slug:category_slug>/<slug:slug>/', catalogue.product_detail, name='product-detail'),
    path('projects/', catalogue.projects, name='projects'),
    path('projects/<slug:slug>/', catalogue.project_detail, name='project-detail'),
    path('solutions/', catalogue.solutions, name='solutions'),
    path('solutions/<slug:slug>/', catalogue.solutions, name='solution-detail'),
    path('resources/', catalogue.resources, name='resources'),
    path('resources/<slug:slug>/download/', catalogue.download, name='resource-download'),
    path('contact/', catalogue.contact, name='contact'),
    path('sitemap.xml', sitemap, name='sitemap'),
]
urlpatterns += [path(old.lstrip('/'), RedirectView.as_view(url=new, permanent=True)) for old, new in LEGACY_REDIRECTS.items()]
urlpatterns += [path('en/Real/'+legacy+'.html', category_redirect, {'legacy':legacy}) for legacy in CATEGORY_LEGACY]
urlpatterns += [path('<slug:slug>/', catalogue.content_page, name='content-page')]
handler500 = 'core.views.server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'core.views.not_found'
admin.site.site_header = 'NCCT · Content & enquiries'
admin.site.site_title = 'NCCT'
admin.site.index_title = 'Website administration'
