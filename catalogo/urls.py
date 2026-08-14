from django.urls import path
from . import views

urlpatterns = [
    path('categorias/', views.CategoriaView.as_view()),
    path('categorias/<int:pk>/', views.CategoriaDetalleView.as_view()),
    path('categorias/<int:categoria_id>/productos/', views.CategoriaProductosView.as_view()),
    path('productos/', views.ProductoView.as_view()),
    path('productos/<int:pk>/', views.ProductoDetalleView.as_view()),
]
