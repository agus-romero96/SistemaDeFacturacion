import wx
import configparser
import os


# Crear una instancia de ConfigParser
config = configparser.ConfigParser()

# Usar la ruta relativa específica
ruta_config = os.path.join('django_bd', 'utilidades', 'config.ini')
config.read(ruta_config)

class Configuraciones(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        # Crear cuadros de edición
        lbl_ruta = wx.StaticText(self, label="Selecciona la Ruta donde se almacenarán las facturas:")
        self.ruta_txt = wx.TextCtrl(self, size=(300, -1))
        self.boton_buscar = wx.Button(self, label="Seleccionar Ruta")
        lbl_iva = wx.StaticText(self, label="IVA (%):")
        self.iva_txt = wx.TextCtrl(self, size=(100, -1))

        # Botón para agregar o actualizar la empresa
        self.boton_empresa = wx.Button(self, label="Agregar Empresa")  # Etiqueta inicial

        # Botón "Guardar Configuración"
        self.boton_guardar = wx.Button(self, label="Guardar Configuración")

        # Layout del panel
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Layout horizontal para la ruta
        ruta_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ruta_sizer.Add(lbl_ruta, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        ruta_sizer.Add(self.ruta_txt, proportion=1, flag=wx.ALL, border=5)
        ruta_sizer.Add(self.boton_buscar, flag=wx.ALL, border=5)

        # Layout horizontal para el IVA
        iva_sizer = wx.BoxSizer(wx.HORIZONTAL)
        iva_sizer.Add(lbl_iva, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        iva_sizer.Add(self.iva_txt, proportion=0, flag=wx.ALL, border=5)

        # Añadir elementos al sizer principal
        sizer.Add(ruta_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(iva_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.boton_guardar, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        sizer.Add(self.boton_empresa, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self.SetSizer(sizer)

        # Eventos
        self.boton_buscar.Bind(wx.EVT_BUTTON, self.OnBuscarRuta)
        self.boton_guardar.Bind(wx.EVT_BUTTON, self.OnGuardarConfiguracion)
        self.boton_empresa.Bind(wx.EVT_BUTTON, self.OnGestionarEmpresa)

        # Llamar a la actualización inicial
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        """Actualizar la interfaz dinámica (botón y campos de configuración)"""
        from gestion.db_connection import Empresa  # Importar modelo de Empresa

        # Verificar si existe una empresa y actualizar la etiqueta del botón
        if Empresa.objects.exists():
            self.boton_empresa.SetLabel("Actualizar Empresa")
        else:
            self.boton_empresa.SetLabel("Agregar Empresa")

        # Recargar los valores desde el archivo de configuración
        config.read(ruta_config)  # Volver a leer el archivo
        if config.has_section('Settings'):
            if config.has_option('Settings', 'ruta'):
                self.ruta_txt.SetValue(config.get('Settings', 'ruta'))
            else:
                self.ruta_txt.SetValue("")  # Limpiar si no hay valor
            if config.has_option('Settings', 'iva'):
                self.iva_txt.SetValue(config.get('Settings', 'iva'))
            else:
                self.iva_txt.SetValue("")  # Limpiar si no hay valor

    def OnBuscarRuta(self, event):
        # Diálogo para seleccionar la ruta
        with wx.DirDialog(self, "Seleccione una carpeta", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.ruta_txt.SetValue(dialog.GetPath())
                self.GuardarRuta(dialog.GetPath())

    def OnGuardarConfiguracion(self, event):
        # Definir la ruta específica
        carpeta_utilidades = 'django_bd/utilidades'
        if not os.path.exists(carpeta_utilidades):
            os.makedirs(carpeta_utilidades)

        ruta_config = os.path.join(carpeta_utilidades, 'config.ini')
        ruta = self.ruta_txt.GetValue()
        iva = self.iva_txt.GetValue()
        if not ruta:
            wx.MessageBox("Por favor, seleccione una ruta válida.", "Error", wx.ICON_ERROR)
            return
        try:
            iva = float(iva)
            if not (0.01 <= iva <= 1.00):
                raise ValueError("El IVA debe estar entre 0.01 y 1.00 (ejemplo: 0.15 para 15%).")
        except ValueError as e:
            wx.MessageBox(f"Por favor, ingrese un valor válido para el IVA.\n{e}", "Error", wx.ICON_ERROR)
            return
        config = configparser.ConfigParser()
        if not config.has_section('Settings'):
            config.add_section('Settings')
        config.set('Settings', 'ruta', ruta)
        config.set('Settings', 'iva', f"{iva:.2f}")
        with open(ruta_config, 'w') as configfile:
            config.write(configfile)
        wx.MessageBox("Configuraciones guardadas con éxito.", "Éxito", wx.ICON_INFORMATION)

    def OnGestionarEmpresa(self, event):
        """Abrir formulario para agregar o actualizar la empresa"""
        from gestion.empresa.formulario_empresa import FormularioEmpresa
        from gestion.db_connection import Empresa

        empresa = Empresa.objects.first()
        formulario = FormularioEmpresa(self, empresa=empresa)
        if formulario.ShowModal() == wx.ID_OK:
            self.actualizar_interfaz()  # Actualizar la interfaz después de agregar/actualizar la empresa

    def GuardarRuta(self, ruta):
        """Guarda la ruta en el archivo de configuración."""
        carpeta_utilidades = 'django_bd/utilidades'
        if not os.path.exists(carpeta_utilidades):
            os.makedirs(carpeta_utilidades)
        ruta_config_local = os.path.join(carpeta_utilidades, 'config.ini')
        config = configparser.ConfigParser()
        if os.path.exists(ruta_config_local):
            config.read(ruta_config_local)
        if not config.has_section('Settings'):
            config.add_section('Settings')
        config.set('Settings', 'ruta', ruta)
        with open(ruta_config_local, 'w') as configfile:
            config.write(configfile)
        
