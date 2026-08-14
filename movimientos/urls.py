from django.urls import path
from . import views

urlpatterns = [
    path('movimientos/', views.MovimientoView.as_view()),
    path('movimientos/resumen/', views.MovimientoResumenView.as_view()),
    path('movimientos/<int:pk>/', views.MovimientoDetalleView.as_view()),
    path('movimientos/<int:pk>/estado/', views.MovimientoEstadoView.as_view()),
]
