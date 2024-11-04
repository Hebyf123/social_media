
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls')),
    path('chat/', include('usersmodel.urls')),  
    path('rosetta/', include('rosetta.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),  
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)