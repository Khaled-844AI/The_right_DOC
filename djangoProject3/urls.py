
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('no9-admin/', admin.site.urls),
    path('', include('The_right_DOC.urls')),
]
admin.site.index_title = 'The right DOC'
admin.site.site_header = 'The right DOC Admin'