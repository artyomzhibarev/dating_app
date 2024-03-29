from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('api/clients/create/', views.CreateUser.as_view()),
    path('api/clients/<int:pk>/match', views.CreateMatch.as_view()),
    path('api/list/', views.UserList.as_view()),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
