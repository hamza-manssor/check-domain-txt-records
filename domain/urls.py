from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.upload_text_file, name='upload_text_file'),
    path('search/', views.search_domains, name='search_domains'),
]
