from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator 	#para hacer validaciones especiales letras y 							espacio (o expresiones regulares)

def validacion_numeros(value):
    if not value.isdigit():
        raise ValidationError("El valor debe contener solo números") #raise funciona como como un 									print para devolver un mensaje en 									caso de que no se cumpla la condicion

def Validacion_letras(value):
    if not value.isalpha():
        raise ValidationError("El valor debe contener solo letras")
