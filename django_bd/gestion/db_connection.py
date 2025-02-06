import os
import sys
import django
from pathlib import Path
from django.conf import settings
from decouple import config

# Configuración especial para PyInstaller
if getattr(sys, 'frozen', False):
    # Si es ejecutable, usa sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_bd.settings'
else:
    # Si es entorno de desarrollo
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Ajusta según tu estructura

# Cargar variables de entorno
ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
    config._load(ENV_PATH)

# Configuración manual de Django para ejecutables
if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': config('DB_NAME'),
                'USER': config('DB_USER'),
                'PASSWORD': config('DB_PASSWORD'),
                'HOST': config('DB_HOST'),
                'PORT': config('DB_PORT', '3306'),
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                }
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'facturacion'
        ],
        TIME_ZONE = 'America/Guayaquil',
        USE_TZ = True
    )
    django.setup()

from facturacion.models import Cliente, Proveedor, Categoria,Producto,Factura,DetalleFactura,Empresa,AdminPassword

def ObtenerClientes():
    return [f"{cliente.cedula} - {cliente.nombre} {cliente.apellido}" for cliente in Cliente.objects.all()]

def ObtenerCategorias():
    return [f"{categoria.nombre} - {categoria.descripcion}" for categoria in Categoria.objects.all()]

def ObtenerProveedores():
    return [f"{proveedor.ruc} - {proveedor.nombre}" for proveedor in Proveedor.objects.all()]
def generar_factura(cedula, productos_comprados, direccion_entrega=None):
    """
    Genera una factura para el cliente con los productos comprados.

    :param cedula: Número de cédula del cliente
    :param productos_comprados: Lista de tuplas (producto_codigo, cantidad)
    :param direccion_entrega: Dirección opcional de entrega
    :return: Factura generada o mensaje de error
    """
    # Verificar si el cliente existe
    try:
        cliente = Cliente.objects.get(cedula=cedula)
    except Cliente.DoesNotExist:
        return "El cliente no existe en la base de datos."

    # Crear la factura
    factura = Factura(cliente=cliente, direccion_entrega=direccion_entrega)
    factura.save()

    # Variables para calcular el total
    total = 0

    # Procesar los productos comprados
    for producto_codigo, cantidad in productos_comprados:
        try:
            producto = Producto.objects.get(codigo=producto_codigo)
            if producto.stock < cantidad:
                return f"El producto {producto.nombre} no tiene suficiente stock."
            
            # Crear detalle de factura
            precio_total = producto.precio * cantidad
            detalle = DetalleFactura(
                factura=factura,
                producto=producto,
                cantidad=cantidad,
                precio_total=precio_total,
            )
            detalle.save()

            # Actualizar el stock del producto
            producto.stock -= cantidad
            producto.save()

            # Incrementar el total de la factura
            total += precio_total
        except Producto.DoesNotExist:
            return f"El producto con código {producto_codigo} no existe."

    # Actualizar el total de la factura
    factura.total = total
    factura.save()

    return factura