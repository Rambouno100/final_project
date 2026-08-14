from django.urls import path
from . import views

urlpatterns = [
    path('almacenes/', views.AlmacenView.as_view()),
    path('almacenes/<int:pk>/', views.AlmacenDetalleView.as_view()),
    path('almacenes/<int:almacen_id>/stock/', views.AlmacenStockView.as_view()),
    path('stock/', views.StockView.as_view()),
    path('stock/<int:pk>/', views.StockDetalleView.as_view()),
]
