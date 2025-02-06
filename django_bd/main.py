# -*- coding: utf-8 -*-
import wx
import os
import sys
import io
import traceback
import logging_config
from logging_config import logger

# Intentar importar módulos personalizados
try:
    from gestion.menu_admin import VentanaAdmin, VentanaLogin
    from gestion.menu_compras import MenuCompras
    logger.info("Módulos para main importados correctamente")
except ImportError as e:
    logger.critical("Error al importar módulos: %s", traceback.format_exc())
    sys.exit(1)

class VentanaBienvenida(wx.Frame):
    def __init__(self):
        try:
            super().__init__(None, title="Bienvenido al Sistema", size=(600, 500))
            logger.debug("interfaz de main inicializada")
            
            self.panel = wx.Panel(self)
            self.panel.SetBackgroundColour(wx.Colour(240, 240, 240))

            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self._crear_interfaz()
            self.Centre()
            
        except Exception as e:
            logger.error("Error al inicializar ventana principal: %s", traceback.format_exc())
            raise

    def _crear_interfaz(self):
        """Crea los componentes de la interfaz gráfica"""
        try:
            # Configuración de fuentes
            font_titulo = wx.Font(30, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            
            # Título
            titulo = wx.StaticText(self.panel, label="¡Sistema de Ventas!")
            titulo.SetFont(font_titulo)
            titulo.SetForegroundColour(wx.Colour(21, 67, 96))
            titulo.SetBackgroundColour(wx.Colour(212, 230, 241))
            
            # Imagen
            ruta_imagen = self._obtener_ruta_imagen("logo.jpg")
            image_ctrl = self._cargar_imagen(ruta_imagen, (300, 250))
            
            # Botones
            botones_sizer = self._crear_botones()
            
            # Ensamblado final
            self.sizer.AddStretchSpacer()
            self.sizer.Add(titulo, 0, wx.ALL | wx.CENTER, 20)
            self.sizer.Add(image_ctrl, 0, wx.ALL | wx.CENTER, 20)
            self.sizer.Add(botones_sizer, 0, wx.ALL | wx.CENTER, 10)
            self.sizer.AddStretchSpacer()
            
            self.panel.SetSizer(self.sizer)
            logger.debug("Interfaz gráfica creada correctamente")
            
        except Exception as e:
            logger.error("Error al crear interfaz: %s", traceback.format_exc())
            raise

    def _obtener_ruta_imagen(self, nombre_archivo):
        """Obtiene la ruta absoluta de un recurso"""
        try:
            base_path = os.path.abspath(os.path.dirname(__file__))
            ruta = os.path.join(base_path, nombre_archivo)
            logger.debug("Buscando imagen en: %s", ruta)
            
            if not os.path.exists(ruta):
                logger.warning("Imagen no encontrada en: %s", ruta)
                raise FileNotFoundError(f"Imagen {nombre_archivo} no encontrada")
                
            return ruta
        except Exception as e:
            logger.error("Error al obtener ruta de imagen: %s", traceback.format_exc())
            raise

    def _cargar_imagen(self, ruta, size):
        """Carga y redimensiona una imagen"""
        try:
            logger.debug("Intentando cargar imagen desde: %s", ruta)
            image = wx.Image(ruta, wx.BITMAP_TYPE_ANY)
            image = image.Scale(*size, wx.IMAGE_QUALITY_HIGH)
            return wx.StaticBitmap(self.panel, wx.ID_ANY, image.ConvertToBitmap())
        except Exception as e:
            logger.error("Error al cargar imagen: %s", traceback.format_exc())
            return wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(1, 1))

    def _crear_botones(self):
        """Crea los botones de la interfaz"""
        try:
            botones_sizer = wx.BoxSizer(wx.HORIZONTAL)
            font_botones = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            
            botones_info = [
                ("Administrador", wx.Colour(41, 128, 185), self.entrar_como_admin),
                ("Compras", wx.Colour(39, 174, 96), self.entrar_como_cliente),
                ("Salir", wx.Colour(192, 57, 43), self.salir)
            ]
            
            for label, color, action in botones_info:
                btn = wx.Button(self.panel, label=label, size=(180, 50))
                btn.SetFont(font_botones)
                btn.SetBackgroundColour(color)
                btn.SetForegroundColour(wx.WHITE)
                btn.Bind(wx.EVT_BUTTON, action)
                botones_sizer.Add(btn, 0, wx.ALL, 10)
                logger.debug("Botón creado: %s", label)
                
            return botones_sizer
        except Exception as e:
            logger.error("Error al crear botones: %s", traceback.format_exc())
            raise

    def entrar_como_admin(self, event):
        """Manejador para el botón de administrador"""
        try:
            logger.info("Intentando acceder como administrador")
            dialogo_login = VentanaLogin(self)
            
            if dialogo_login.ShowModal() == wx.ID_OK:
                logger.debug("Login de administrador exitoso")
                self.Hide()
                try:
                    VentanaAdmin(self).Show()
                    logger.info("Ventana de administración mostrada")
                except Exception as e:
                    logger.error("Error al mostrar ventana de administración: %s", traceback.format_exc())
                    self.Show()
            dialogo_login.Destroy()
            
        except Exception as e:
            logger.error("Error en entrar_como_admin: %s", traceback.format_exc())
            wx.MessageBox("Error al abrir el módulo de administración", "Error", wx.ICON_ERROR)

    def entrar_como_cliente(self, event):
        """Manejador para el botón de compras"""
        try:
            logger.info("Intentando acceder como cliente")
            self.Hide()
            try:
                MenuCompras(self).Show()
                logger.info("Ventana de compras mostrada")
            except Exception as e:
                logger.error("Error al mostrar ventana de compras: %s", traceback.format_exc())
                self.Show()
                raise
        except Exception as e:
            logger.error("Error en entrar_como_cliente: %s", traceback.format_exc())
            wx.MessageBox("Error al abrir el módulo de compras", "Error", wx.ICON_ERROR)

    def salir(self, event):
        """Manejador para el botón de salir"""
        logger.info("Solicitud de salida recibida")
        if wx.MessageBox("¿Seguro que deseas salir?", "Confirmación", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            logger.info("Usuario confirmó salida")
            self.Close()

class Aplicacion(wx.App):
    def OnInit(self):
        try:
            self.ventana = VentanaBienvenida()
            self.ventana.Show()
            return True
        except Exception as e:
            logger.critical("Error fatal durante la inicialización: %s", traceback.format_exc())
            return False

# Manejo de excepciones no capturadas
def excepthook(exctype, value, tb):
    logger.critical("Excepción no capturada: %s", "".join(traceback.format_exception(exctype, value, tb)))
    wx.MessageBox(f"Error crítico: {str(value)}", "Error", wx.ICON_ERROR)
    sys.exit(1)

sys.excepthook = excepthook

if __name__ == "__main__":
    try:
        logger.info("Iniciando bucle principal")
        app = Aplicacion()
        app.MainLoop()
        logger.info("Aplicación finalizada correctamente")
    except Exception as e:
        logger.critical("Error en el bucle principal: %s", traceback.format_exc())