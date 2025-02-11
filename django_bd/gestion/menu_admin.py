# -*- coding: utf-8 -*-
import wx
import os
import logging
import traceback
from datetime import datetime

# Importar el logger central configurado
from logging_config import logger

# Importar módulos personalizados y registrar la importación
try:
    from gestion.gestion_producto.producto import PanelProductos
    from gestion.gestion_clientes.cliente import PanelClientes
    from gestion.gestion_proveedor_categoria.ui_proveedor_categoria import PanelProveedor
    from gestion.empresa.config import Configuraciones
    from gestion.gestion_proveedor_categoria.Categoria import PanelCategoria, FormularioCategoria
    logger.info("Módulos para menú admin importados correctamente.")
except ImportError as e:
    logger.critical("Error al importar módulos: %s", traceback.format_exc())
    raise

class VentanaAdmin(wx.Dialog):
    def __init__(self, parent):
        try:
            super().__init__(parent, title="Sistema de Gestión - Administrador", size=(1024, 768))
            logger.debug("VentanaAdmin inicializada.")
            
            # Panel principal
            self.panel = wx.Panel(self)
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            
            # Crear el notebook (sistema de pestañas)
            self.notebook = wx.Notebook(self.panel)
            
            # Crear las páginas del notebook (con la pestaña de configuraciones primero)
            self.page_config = Configuraciones(self.notebook)
            self.page_clientes = PanelClientes(self.notebook)
            self.page_productos = PanelProductos(self.notebook)
            self.page_proveedores = PanelProveedor(self.notebook)
            self.page_categoria = PanelCategoria(self.notebook)
            
            # Añadir las páginas al notebook
            self.notebook.AddPage(self.page_config, "Configuraciones")
            self.notebook.AddPage(self.page_clientes, "Gestión de Clientes")
            self.notebook.AddPage(self.page_productos, "Gestión de Productos")
            self.notebook.AddPage(self.page_proveedores, "Gestión de Proveedores")
            self.notebook.AddPage(self.page_categoria, "Gestión de Categorías")
            
            self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
            
            # Botón "Volver al Menú"
            btn_volver = wx.Button(self.panel, label="&Volver al Menú Principal")
            btn_volver.Bind(wx.EVT_BUTTON, self.volver_al_menu)
            self.sizer.Add(btn_volver, 0, wx.ALL | wx.CENTER, 10)
            
            self.panel.SetSizer(self.sizer)
            self.Centre()
            logger.info("VentanaAdmin configurada correctamente.")
        except Exception as e:
            logger.error("Error al inicializar VentanaAdmin: %s", traceback.format_exc())
            raise

    def volver_al_menu(self, event):
        logger.info("Se ha solicitado volver al menú principal desde VentanaAdmin.")
        self.Hide()
        self.GetParent().Show()


class VentanaLogin(wx.Dialog):
    def __init__(self, parent):
        try:
            super().__init__(parent, title="Inicio de Sesión - Administrador", size=(400, 275))
            logger.debug("VentanaLogin inicializada.")
            
            self.panel = wx.Panel(self)
            self.sizer = wx.BoxSizer(wx.VERTICAL)

            # Sizer para el usuario
            sizer_usuario = wx.BoxSizer(wx.VERTICAL)
            self.lbl_usuario = wx.StaticText(self.panel, label="&Usuario:")
            self.txt_usuario = wx.TextCtrl(self.panel)
            sizer_usuario.Add(self.lbl_usuario, 0, wx.ALL, 5)
            sizer_usuario.Add(self.txt_usuario, 0, wx.EXPAND | wx.ALL, 5)
            
            # Sizer para la contraseña (oculta y visible)
            self.sizer_contrasena = wx.BoxSizer(wx.VERTICAL)
            self.lbl_contrasena = wx.StaticText(self.panel, label="&Contraseña:")
            self.txt_contrasena_oculta = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
            self.sizer_contrasena.Add(self.lbl_contrasena, 0, wx.ALL, 5)
            self.sizer_contrasena.Add(self.txt_contrasena_oculta, 0, wx.EXPAND | wx.ALL, 5)
            
            self.txt_contrasena_visible = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
            self.txt_contrasena_visible.Hide()
            self.sizer_contrasena.Add(self.txt_contrasena_visible, 0, wx.EXPAND | wx.ALL, 5)
            
            self.sizer.Add(sizer_usuario, 0, wx.EXPAND | wx.ALL, 0)
            self.sizer.Add(self.sizer_contrasena, 0, wx.EXPAND | wx.ALL, 0)

            # Casilla de verificación para mostrar/ocultar contraseña
            self.chk_mostrar_contrasena = wx.CheckBox(self.panel, label="Mostrar Contraseña")
            self.sizer.Add(self.chk_mostrar_contrasena, 0, wx.ALL, 5)
            self.chk_mostrar_contrasena.Bind(wx.EVT_CHECKBOX, self.OnMostrarContrasena)

            # Botones
            btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.btn_login = wx.Button(self.panel, label="Iniciar Sesión")
            self.btn_cancelar = wx.Button(self.panel, label="Cancelar")
            btn_sizer.Add(self.btn_login, 1, wx.EXPAND | wx.ALL, 5)
            btn_sizer.Add(self.btn_cancelar, 1, wx.EXPAND | wx.ALL, 5)
            self.sizer.Add(btn_sizer, 0, wx.CENTER)

            # Eventos
            self.txt_contrasena_oculta.Bind(wx.EVT_TEXT_ENTER, self.validar_login)
            self.txt_contrasena_visible.Bind(wx.EVT_TEXT_ENTER, self.validar_login)
            self.btn_login.Bind(wx.EVT_BUTTON, self.validar_login)
            self.btn_cancelar.Bind(wx.EVT_BUTTON, self.cancelar)

            self.panel.SetSizer(self.sizer)
            self.Centre()
            logger.info("VentanaLogin configurada correctamente.")
        except Exception as e:
            logger.error("Error al inicializar VentanaLogin: %s", traceback.format_exc())
            raise

    def OnMostrarContrasena(self, event):
        logger.debug("Cambio de estado de la casilla de mostrar contraseña.")
        try:
            if self.chk_mostrar_contrasena.GetValue():
                self.txt_contrasena_visible.SetValue(self.txt_contrasena_oculta.GetValue())
                self.txt_contrasena_oculta.Hide()
                self.txt_contrasena_visible.Show()
                self.txt_contrasena_visible.SetFocus()
                logger.debug("Contraseña visible activada.")
            else:
                self.txt_contrasena_oculta.SetValue(self.txt_contrasena_visible.GetValue())
                self.txt_contrasena_visible.Hide()
                self.txt_contrasena_oculta.Show()
                self.txt_contrasena_oculta.SetFocus()
                logger.debug("Contraseña oculta activada.")
            self.panel.Layout()
        except Exception as e:
            logger.error("Error en OnMostrarContrasena: %s", traceback.format_exc())

    def validar_login(self, event):
        logger.debug("Validando login.")
        username = self.txt_usuario.GetValue()
        if self.chk_mostrar_contrasena.GetValue():
            password = self.txt_contrasena_visible.GetValue()
        else:
            password = self.txt_contrasena_oculta.GetValue()
        
        if not username or not password:
            wx.MessageBox("Por favor ingrese usuario y contraseña", "Error", wx.ICON_ERROR)
            logger.warning("Campos de usuario o contraseña vacíos.")
            return
            
        try:
            try:
                from django.contrib.auth.hashers import check_password
                from gestion.db_connection import AdminPassword
                logger.info("Módulos de autenticación importados correctamente.")
            except ImportError as e:
                logger.critical("Error al importar módulos de autenticación: %s", traceback.format_exc())
                raise
            user = AdminPassword.objects.get(username=username)
            if check_password(password, user.password):
                logger.info("Login exitoso para usuario: %s", username)
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox("Contraseña incorrecta", "Error", wx.ICON_ERROR)
                logger.warning("Contraseña incorrecta para usuario: %s", username)
                if self.chk_mostrar_contrasena.GetValue():
                    self.txt_contrasena_visible.SetFocus()
                else:
                    self.txt_contrasena_oculta.SetFocus()
        except Exception as e:
            wx.MessageBox("Usuario no encontrado", "Error", wx.ICON_ERROR)
            logger.warning("Usuario no encontrado: %s", username)
            self.txt_usuario.SetFocus()

    def cancelar(self, event):
        logger.info("Login cancelado por el usuario.")
        self.EndModal(wx.ID_CANCEL)
