from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from almacenes.models import Almacen
from catalogo.models import Categoria, Producto

PRODUCTOS = [
    ('FER001', 'Cemento gris 42.5 kg', 'Ferreteria', 'UNIDAD', 20, '29.90'),
    ('FER002', 'Fierro corrugado 1/2"', 'Ferreteria', 'UNIDAD', 50, '38.50'),
    ('ELE001', 'Cable THW 14 AWG', 'Electricos', 'METRO', 100, '2.40'),
    ('ELE002', 'Interruptor simple', 'Electricos', 'UNIDAD', 30, '8.90'),
    ('LIM001', 'Detergente industrial', 'Limpieza', 'LITRO', 15, '18.00'),
    ('SEG001', 'Casco de seguridad', 'Seguridad', 'UNIDAD', 25, '32.00'),
]

ALMACENES = [
    ('ALM01', 'Almacen central', 'Av. Argentina 1234, Callao'),
    ('ALM02', 'Almacen de obra', 'Jr. Union 456, Lima'),
]


class Command(BaseCommand):
    help = 'Carga categorias, productos y almacenes de ejemplo para la demo.'

    def handle(self, *args, **options):
        for codigo, nombre, direccion in ALMACENES:
            Almacen.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'direccion': direccion}
            )

        for codigo, nombre, categoria, unidad, minimo, precio in PRODUCTOS:
            objeto_categoria, _ = Categoria.objects.get_or_create(nombre=categoria)
            Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'categoria': objeto_categoria,
                    'unidad': unidad,
                    'stock_minimo': minimo,
                    'precio': precio,
                }
            )

        if not get_user_model().objects.filter(username='almacenero').exists():
            get_user_model().objects.create_user(
                username='almacenero',
                email='almacenero@demo.com',
                password='Almacen2026',
                first_name='Luis',
                last_name='Quispe',
                dni='70123456',
                area='ALMACEN',
            )

        self.stdout.write(self.style.SUCCESS(
            'Datos de ejemplo cargados. Usuario: almacenero / Almacen2026'
        ))
