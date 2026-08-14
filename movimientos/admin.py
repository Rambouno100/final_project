from django.contrib import admin

from .models import DetalleMovimiento, Movimiento


class DetalleMovimientoInline(admin.TabularInline):
    model = DetalleMovimiento
    extra = 1


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'estado', 'almacen_origen', 'almacen_destino', 'creado_en')
    list_filter = ('tipo', 'estado')
    search_fields = ('numero',)
    inlines = [DetalleMovimientoInline]
