from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('django')

hiddenimports += [
    'django.core.management',
    'django.core.serializers',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.db.models',
    'facturacion.apps.FacturacionConfig',
    'pymysql',          # Si usas PyMySQL
    'django_bd.settings'
]