from django.urls import path
from . import views

urlpatterns = [
    path('auth/registro/', views.RegistroView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
    path('auth/refresh/', views.RefreshView.as_view()),
    path('usuarios/', views.UsuarioListView.as_view()),
    path('usuarios/<int:pk>/', views.UsuarioDetalleView.as_view()),
]
