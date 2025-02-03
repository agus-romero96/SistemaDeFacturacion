import wx
import os
from gestion.menu_admin import VentanaAdmin, VentanaLogin
from gestion.menu_compras import MenuCompras

class VentanaBienvenida(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Bienvenido al Sistema", size=(600, 500))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(240, 240, 240))  # Fondo gris muy claro

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Fuente para título
        font_titulo = wx.Font(30, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # **Título con fondo similar al fondo general**
        titulo = wx.StaticText(panel, label="¡Sistema de Ventas!")
        titulo.SetFont(font_titulo)
        titulo.SetForegroundColour(wx.Colour(21, 67, 96))  # Azul oscuro elegante
        titulo.SetBackgroundColour(wx.Colour(212, 230, 241))  # Azul pastel similar al fondo
        titulo.SetWindowStyle(wx.BORDER_SIMPLE)
        titulo.Wrap(600)

        # Imagen
        ruta_imagen = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
        image_ctrl = self.cargar_imagen(panel, ruta_imagen, (300, 250))

        # Botones con colores mejorados
        botones_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_botones = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        botones_info = [
            ("Administrador", wx.Colour(41, 128, 185), self.entrar_como_admin),  # Azul fuerte
            ("Compras", wx.Colour(39, 174, 96), self.entrar_como_cliente),  # Verde fuerte
            ("Salir", wx.Colour(192, 57, 43), self.salir)  # Rojo oscuro
        ]

        self.botones = []
        for label, color, action in botones_info:
            btn = wx.Button(panel, label=label, size=(180, 50))
            btn.SetFont(font_botones)
            btn.SetBackgroundColour(color)
            btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Texto blanco
            btn.Bind(wx.EVT_BUTTON, action)
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda evt, b=btn, c=color: self.on_hover(evt, b, c, True))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda evt, b=btn, c=color: self.on_hover(evt, b, c, False))
            botones_sizer.Add(btn, 0, wx.ALL, 10)
            self.botones.append(btn)

        # Añadir widgets al sizer principal
        sizer.AddStretchSpacer()
        sizer.Add(titulo, 0, wx.ALL | wx.CENTER, 20)
        sizer.Add(image_ctrl, 0, wx.ALL | wx.CENTER, 20)
        sizer.Add(botones_sizer, 0, wx.ALL | wx.CENTER, 10)
        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        self.Centre()

    def cargar_imagen(self, panel, ruta, size):
        """Carga una imagen y la redimensiona"""
        if os.path.exists(ruta):
            try:
                image = wx.Image(ruta, wx.BITMAP_TYPE_ANY).Scale(*size, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
                return wx.StaticBitmap(panel, wx.ID_ANY, image)
            except Exception as e:
                wx.MessageBox(f"No se pudo cargar la imagen: {e}", "Error", wx.ICON_ERROR)
        return wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(1, 1))  # Imagen vacía en caso de error

    def on_hover(self, event, button, original_color, enter):
        """Efecto de hover con colores más marcados"""
        hover_color = wx.Colour(
            min(original_color.Red() + 30, 255),
            min(original_color.Green() + 30, 255),
            min(original_color.Blue() + 30, 255)
        )
        button.SetBackgroundColour(hover_color if enter else original_color)
        button.Refresh()

    def entrar_como_admin(self, event):
        """Abrir la ventana de administración solo si el login es exitoso"""
        dialogo_login = VentanaLogin(self)
        if dialogo_login.ShowModal() == wx.ID_OK:
            self.Hide()
            VentanaAdmin(self).Show()
        dialogo_login.Destroy()

    def entrar_como_cliente(self, event):
        """Abrir la ventana de compras"""
        self.Hide()
        MenuCompras(self).Show()

    def salir(self, event):
        """Salir con confirmación"""
        if wx.MessageBox("¿Seguro que deseas salir?", "Confirmación", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            self.Close()

class Aplicacion(wx.App):
    def OnInit(self):
        VentanaBienvenida().Show()
        return True

if __name__ == "__main__":
    app = Aplicacion()
    app.MainLoop()
