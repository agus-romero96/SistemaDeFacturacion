from django.db import models
from django.contrib.auth.hashers import make_password
from decimal import Decimal
import configparser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from facturacion.validadores import validacion_numeros, Validacion_letras  # Importar validadores personalizados


class AdminPassword(models.Model):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    cedula = models.CharField(
        max_length=10,
        primary_key=True,
        validators=[validacion_numeros],  # Validar que solo contenga números
    )
    nombre = models.CharField(
        max_length=30,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    apellido = models.CharField(
        max_length=30,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[validacion_numeros],  # Validar que solo contenga números
    )
    direccion = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        if len(self.cedula) != 10:
            raise ValidationError("La cédula debe tener 10 dígitos numéricos.")
        if self.telefono and len(self.telefono) != 10:
            raise ValidationError("El teléfono debe tener 10 dígitos numéricos.")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Herencia(models.Model):
    ruc = models.CharField(
        max_length=13,
        primary_key=True,
        validators=[validacion_numeros],  # Validar que solo contenga números
    )
    nombre = models.CharField(
        max_length=200,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[validacion_numeros],  # Validar que solo contenga números
    )
    direccion = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if len(self.ruc) != 13:
            raise ValidationError("El RUC debe tener 13 dígitos numéricos.")

    def __str__(self):
        return f"{self.ruc} {self.nombre}"


class Proveedor(Herencia):
    pass


class Empresa(Herencia):
    pass


class Producto(models.Model):
    codigo = models.CharField(
        max_length=10,
        primary_key=True,
        validators=[validacion_numeros],  # Validar que solo contenga números
    )
    nombre = models.CharField(
        max_length=100,
        validators=[Validacion_letras],  # Validar que solo contenga letras
    )
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.precio <= 0:
            raise ValidationError("El precio debe ser un valor positivo.")
        if self.stock < 0:
            raise ValidationError("El stock no puede ser un valor negativo.")

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def clean(self):
        super().clean()
        if self.subtotal < 0:
            raise ValidationError("El subtotal no puede ser un valor negativo.")
        if self.iva < 0:
            raise ValidationError("El IVA no puede ser un valor negativo.")
        if self.total < 0:
            raise ValidationError("El total no puede ser un valor negativo.")

    def calcular_totales(self):
        config = configparser.ConfigParser()
        config.read("django_bd/utilidades/config.ini")
        self.subtotal = sum(detalle.precio_total for detalle in self.detalles.all())
        porcentaje_iva = Decimal(config.get("Settings", "iva", fallback="0.15"))
        self.iva = self.subtotal * porcentaje_iva
        self.total = self.subtotal + self.iva
        self.save()

    def actualizar_stock(self):
        for detalle in self.detalles.all():
            detalle.producto.stock -= detalle.cantidad
            detalle.producto.save()

    def __str__(self):
        return f"Factura {self.id} - {self.cliente.nombre} {self.cliente.apellido}"


class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        super().clean()
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser un valor positivo.")
        if self.precio_unitario is not None and self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser un valor positivo.")

    def save(self, *args, **kwargs):
        self.precio_unitario = self.producto.precio
        self.precio_total = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
        self.factura.calcular_totales()

    def __str__(self):
        return f"Detalle de Factura {self.factura.id} - Producto {self.producto.nombre}"
