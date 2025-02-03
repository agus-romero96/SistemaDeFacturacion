import wx
from gestion.db_connection import Producto, Proveedor, Categoria, Factura, DetalleFactura, Cliente, generar_factura,Empresa
from decimal import Decimal


class MenuCompras(wx.Frame):
    def __init__(self, parent):
        super(MenuCompras, self).__init__(parent, title="Menu de Compras", size=(800, 600))
        self.carrito = []
        self.InitUI()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Etiqueta para filtro
        self.label_filtro = wx.StaticText(panel, label="&Filtrar productos por:")
        self.sizer.Add(self.label_filtro, 0, wx.LEFT | wx.TOP, 5)

        # ComboBox para categorías
        self.combo_categorias = wx.ComboBox(panel, choices=["Mostrar Todos"] + [cat.nombre for cat in Categoria.objects.all()], style=wx.CB_READONLY)
        self.combo_categorias.Bind(wx.EVT_COMBOBOX, self.filtrar_por_categoria)
        self.sizer.Add(self.combo_categorias, 0, wx.EXPAND | wx.ALL, 5)


        # Etiqueta para la lista de productos
        self.label_productos = wx.StaticText(panel, label="&Lista de Productos:")
        self.sizer.Add(self.label_productos, 0, wx.LEFT | wx.TOP, 5)

        # Lista de productos
        self.list_control = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.list_control.InsertColumn(0, 'Código', width=80)
        self.list_control.InsertColumn(1, 'Nombre', width=150)
        self.list_control.InsertColumn(2, 'Precio', width=80)
        self.list_control.InsertColumn(3, 'Stock', width=80)
        self.list_control.InsertColumn(4, 'Categoría', width=120)
        self.list_control.InsertColumn(5, 'Proveedor', width=120)
        self.sizer.Add(self.list_control, 1, wx.EXPAND | wx.ALL, 5)

        # Etiqueta para el carrito de compras
        self.label_carrito = wx.StaticText(panel, label="Carrito &de Compras:")
        self.sizer.Add(self.label_carrito, 0, wx.LEFT | wx.TOP, 5)

        # Carrito de compras
        self.carrito_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.carrito_list.InsertColumn(0, 'Código', width=80)
        self.carrito_list.InsertColumn(1, 'Nombre', width=150)
        self.carrito_list.InsertColumn(2, 'Cantidad', width=80)
        self.carrito_list.InsertColumn(3, 'Precio Unit.', width=80)
        self.carrito_list.InsertColumn(4, 'Total', width=80)
        self.sizer.Add(self.carrito_list, 1, wx.EXPAND | wx.ALL, 5)

        # Botones
        button_panel = wx.Panel(panel)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_agregar = wx.Button(button_panel, label="Agregar al &Carrito")
        self.btn_quitar = wx.Button(button_panel, label="&Quitar del Carrito")
        self.btn_facturar = wx.Button(button_panel, label="&Facturar")
        self.btn_salir = wx.Button(button_panel, label="&Volver al menú principal")

        # desabilitar botones de facturar y quitar del carrito cuando se inicie la ventana
        self.btn_quitar.Disable()
        self.btn_facturar.Disable()

        button_sizer.Add(self.btn_agregar, 0, wx.RIGHT, 5)
        button_sizer.Add(self.btn_quitar, 0, wx.RIGHT, 5)
        button_sizer.Add(self.btn_facturar, 0, wx.RIGHT, 5)
        button_sizer.Add(self.btn_salir, 0)

        button_panel.SetSizer(button_sizer)

        # Eventos de botones
        self.btn_agregar.Bind(wx.EVT_BUTTON, self.agregar_al_carrito)
        self.btn_quitar.Bind(wx.EVT_BUTTON, self.quitar_del_carrito)
        self.btn_facturar.Bind(wx.EVT_BUTTON, self.generar_factura)
        self.btn_salir.Bind(wx.EVT_BUTTON, self.volver)

        # Layout
        self.sizer.Add(button_panel, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(self.sizer)
        self.actualizar_lista(None)

    def quitar_del_carrito(self, event):
        selected = self.carrito_list.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Seleccione un producto del carrito primero.", "Error", wx.ICON_ERROR)
            return
        # Obtener detalles del producto seleccionado en el carrito
        producto = self.carrito[selected]
        cantidad_actual = producto['cantidad']
        dlg = wx.TextEntryDialog(self, f"Ingrese la cantidad a quitar (actual: {cantidad_actual}):", "Cantidad")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                cantidad_a_quitar = int(dlg.GetValue())
                if cantidad_a_quitar <= 0:
                    raise ValueError("La cantidad debe ser mayor a cero.")
                if cantidad_a_quitar > cantidad_actual:
                    raise ValueError("No puede quitar más cantidad de la que está en el carrito.")
                # Actualizar cantidad o eliminar producto del carrito
                if cantidad_a_quitar == cantidad_actual:
                    # Eliminar producto del carrito si la cantidad restante es 0
                    self.carrito_list.DeleteItem(selected)
                    self.carrito.pop(selected)
                else:
                    # Reducir la cantidad del producto
                    nueva_cantidad = cantidad_actual - cantidad_a_quitar
                    self.carrito[selected]['cantidad'] = nueva_cantidad
                    self.carrito[selected]['total'] = nueva_cantidad * producto['precio']

                    # Actualizar la interfaz del carrito
                    self.carrito_list.SetItem(selected, 2, str(nueva_cantidad))
                    self.carrito_list.SetItem(selected, 4, f"${self.carrito[selected]['total']:.2f}")

                # Ocultar botones si el carrito queda vacío
                if not self.carrito:
                    self.btn_quitar.Hide()
                    self.btn_facturar.Hide()
                    self.carrito_list.Hide()
                    self.Layout()

            except ValueError as e:
                wx.MessageBox(f"Entrada no válida: {e}", "Error", wx.ICON_ERROR)

        dlg.Destroy()


    def actualizar_lista(self, event):
        self.list_control.DeleteAllItems()
        productos = Producto.objects.all()
        
        for producto in productos:
            index = self.list_control.GetItemCount()
            self.list_control.InsertItem(index, producto.codigo)
            self.list_control.SetItem(index, 1, producto.nombre)
            self.list_control.SetItem(index, 2, str(producto.precio))
            self.list_control.SetItem(index, 3, str(producto.stock))
            self.list_control.SetItem(index, 4, producto.categoria.nombre if producto.categoria else '')
            self.list_control.SetItem(index, 5, producto.proveedor.nombre if producto.proveedor else '')

    def volver(self, event):
        self.Parent.Show()
        self.Destroy()

    def agregar_al_carrito(self, event):
        """Agregar producto seleccionado al carrito"""
        selected = self.list_control.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Seleccione un producto primero.", "Error", wx.ICON_ERROR)
            return

        # Obtener detalles del producto seleccionado
        codigo = self.list_control.GetItemText(selected, 0)
        try:
            # Buscar el Producto en la base de datos
            producto = Producto.objects.get(codigo=codigo)
        except Producto.DoesNotExist:
            wx.MessageBox("El producto no existe en la base de datos.", "Error", wx.ICON_ERROR)
            return
        dlg = wx.TextEntryDialog(self, 'Cantidad:', 'Cantidad')
        if dlg.ShowModal() == wx.ID_OK:
            try:
                cantidad = int(dlg.GetValue())
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a cero.")
                if cantidad > producto.stock:
                    wx.MessageBox(f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles.", "Error", wx.ICON_ERROR)
                    return

                # Verificar si el producto ya está en el carrito
                for idx, item in enumerate(self.carrito):
                    if item['codigo'] == codigo:
                        # Actualizar la cantidad y el total del producto existente
                        nueva_cantidad = item['cantidad'] + cantidad
                        if nueva_cantidad > producto.stock:
                            wx.MessageBox(f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles.", "Error", wx.ICON_ERROR)
                            return

                        self.carrito[idx]['cantidad'] = nueva_cantidad
                        self.carrito[idx]['total'] = nueva_cantidad * item['precio']

                        # Actualizar la lista del carrito
                        self.carrito_list.SetItem(idx, 2, str(nueva_cantidad))
                        self.carrito_list.SetItem(idx, 4, f"${self.carrito[idx]['total']:.2f}")
                        break
                else:
                    # Si el producto no está en el carrito, agregarlo como nuevo
                    precio = float(producto.precio)
                    total = cantidad * precio
                    self.carrito.append({
                        'producto': producto,  # Agregar el objeto Producto al carrito
                        'codigo': producto.codigo,
                        'nombre': producto.nombre,
                        'cantidad': cantidad,
                        'precio': precio,
                        'total': total
                    })
                    # Agregar el producto a la lista del carrito
                    index = self.carrito_list.GetItemCount()
                    self.carrito_list.InsertItem(index, producto.codigo)
                    self.carrito_list.SetItem(index, 1, producto.nombre)
                    self.carrito_list.SetItem(index, 2, str(cantidad))
                    self.carrito_list.SetItem(index, 3, f"${precio:.2f}")
                    self.carrito_list.SetItem(index, 4, f"${total:.2f}")
                # actualizar la lista de productos
                self.update_categoria()
                # Habilitar botones de facturar y quitar del carrito
                self.btn_quitar.Enable()
                self.btn_facturar.Enable()
                self.Layout()

            except ValueError as e:
                wx.MessageBox(f"Entrada no válida: {e}", "Error", wx.ICON_ERROR)
        dlg.Destroy()


    def filtrar_por_categoria(self, event):
        """Filtrar productos según la categoría seleccionada"""
        categoria = self.combo_categorias.GetValue()
        if categoria == "Mostrar Todos":
            categoria = None
        self.update_categoria(categoria=categoria)

    def update_categoria(self, categoria=None):
        """Actualizar la lista de productos, opcionalmente filtrados por categoría"""
        self.list_control.DeleteAllItems()
        
        if categoria:
            productos = Producto.objects.filter(categoria__nombre=categoria)
        else:
            productos = Producto.objects.all()
        
        for producto in productos:
            index = self.list_control.InsertItem(self.list_control.GetItemCount(), producto.codigo)
            self.list_control.SetItem(index, 1, producto.nombre)
            self.list_control.SetItem(index, 2, str(producto.precio))
            self.list_control.SetItem(index, 3, str(producto.stock))
            self.list_control.SetItem(index, 4, producto.categoria.nombre)
            self.list_control.SetItem(index, 5, producto.proveedor.nombre)

    def generar_factura(self, event):
        from gestion.gestion_clientes.agregar_cliente import AgregarCliente
        if not self.carrito:
            wx.MessageBox('El carrito está vacío', 'Error', wx.OK | wx.ICON_ERROR)
            return
        # Crear un cuadro de diálogo personalizado para seleccionar o ingresar cliente
        dlg = wx.Dialog(self, title="Seleccionar Cliente", size=(400, 200))
        dlg_sizer = wx.BoxSizer(wx.VERTICAL)
        # Etiqueta y cuadro de texto para ingresar la cédula
        cedula_label = wx.StaticText(dlg, label="&Ingrese la cédula del cliente (dejar en blanco para escoger un usuario de la lista):")
        cedula_text = wx.TextCtrl(dlg)
        dlg_sizer.Add(cedula_label, 0, wx.ALL, 5)
        dlg_sizer.Add(cedula_text, 0, wx.EXPAND | wx.ALL, 5)
        # Etiqueta y ComboBox para seleccionar cliente
        combo_label = wx.StaticText(dlg, label="&O seleccione un cliente de la lista:")
        combo_box = wx.ComboBox(dlg, choices=[
            f"{cliente.cedula} - {cliente.nombre} {cliente.apellido}" for cliente in Cliente.objects.all()
        ], style=wx.CB_READONLY)
        dlg_sizer.Add(combo_label, 0, wx.ALL, 5)
        dlg_sizer.Add(combo_box, 0, wx.EXPAND | wx.ALL, 5)
        # Botones para confirmar o cancelar
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(dlg, label="Aceptar")
        btn_cancel = wx.Button(dlg, label="Cancelar")
        btn_sizer.Add(btn_ok, 0, wx.RIGHT, 5)
        btn_sizer.Add(btn_cancel, 0, wx.LEFT, 5)
        dlg_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        dlg.SetSizer(dlg_sizer)
        # Eventos de botones
        btn_ok.Bind(wx.EVT_BUTTON, lambda evt: dlg.EndModal(wx.ID_OK))
        btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: dlg.EndModal(wx.ID_CANCEL))
        # Mostrar el cuadro de diálogo
        if dlg.ShowModal() == wx.ID_OK:
            try:
                # Priorizar la cédula ingresada manualmente
                cedula = cedula_text.GetValue().strip()
                cliente = None
                if cedula:  # Si se ingresó la cédula manualmente
                    cliente = Cliente.objects.get(cedula=cedula)
                elif combo_box.GetSelection() != wx.NOT_FOUND:  # Si se seleccionó un cliente del ComboBox
                    cedula_seleccionada = combo_box.GetValue().split(' - ')[0]  # Extraer la cédula del formato
                    cliente = Cliente.objects.get(cedula=cedula_seleccionada)
                else:
                    # mostrar un error
                    wx.MessageBox('Seleccione un cliente o ingrese la cédula del cliente', 'Error', wx.OK | wx.ICON_ERROR)
                    return
                # Crear factura
                factura = Factura.objects.create(cliente=cliente)
                # Crear detalles
                for item in self.carrito:
                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=item['producto'],
                        cantidad=item['cantidad']
                    )
                # Actualizar stock
                factura.actualizar_stock()
                # Guardar la categoría seleccionada
                categoria = self.combo_categorias.GetValue()
                if categoria == "Mostrar Todos":
                    categoria = None
                # Limpiar carrito
                self.carrito = []
                self.carrito_list.DeleteAllItems()
                # Actualizar la lista con la categoría guardada, y ocultar botones
                self.update_categoria(categoria)
                self.btn_quitar.Disable()
                self.btn_facturar.Disable()
                self.Layout()
                # Generar el PDF con los detalles de la factura
                self.generar_pdf_factura(factura)
                wx.MessageBox(f'Factura generada con éxito\nTotal: ${factura.total}', 'Éxito', wx.OK | wx.ICON_INFORMATION)
            except Cliente.DoesNotExist:
                wx.MessageBox('Cliente no encontrado. Agregue el cliente.', 'Error', wx.OK | wx.ICON_ERROR)
                dlg.Destroy()
                # Abrir el formulario para agregar un cliente
                AgregarCliente(actualizar_lista_callback=self.actualizar_lista)
            except Exception as e:
                wx.MessageBox(f'Error al generar la factura: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def generar_pdf_factura(self, factura):
        import configparser
        import os
        import sys
        from datetime import datetime
        from django.utils.timezone import localtime
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        # Leer configuración
        config = configparser.ConfigParser()
        config.read('django_bd/utilidades/config.ini')
        if not config.has_section('Settings') or not config.has_option('Settings', 'ruta'):
            wx.MessageBox('No se ha configurado la ruta para guardar las facturas', 'Error', wx.OK | wx.ICON_ERROR)
            return
        ruta_base = config.get('Settings', 'ruta', fallback='facturas')
        # Crear carpeta base si no existe
        if not os.path.exists(ruta_base):
            os.makedirs(ruta_base)
        # Obtener la fecha y formatearla
        fecha_formateada = localtime(factura.fecha).strftime('%d-%m-%Y')
        cliente_nombre = f"{factura.cliente.nombre}{factura.cliente.apellido}".replace(" ", "").lower()
        hora_factura = localtime(factura.fecha).strftime('%H-%M-%S')  # Cambiar formato aquí
        # Crear ruta completa
        ruta_fecha = os.path.join(ruta_base, 'facturas', fecha_formateada)
        ruta_cliente = os.path.join(ruta_fecha, cliente_nombre)
        if not os.path.exists(ruta_cliente):
            os.makedirs(ruta_cliente)
        # Ruta del PDF
        pdf_path = os.path.join(ruta_cliente, f"factura_{hora_factura}.pdf")
        # Obtener información de la empresa
        empresa = Empresa.objects.first()
        # Crear documento
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elementos = []
        # Estilos
        styles = getSampleStyleSheet()
        estilo_titulo = styles['Heading1']
        estilo_texto = styles['Normal']
        # Encabezado de la empresa
        empresa_info = [
            Paragraph(f"{empresa.nombre}", estilo_titulo),
            Paragraph(f"RUC: {empresa.ruc}", estilo_texto),
            Paragraph(f"Email: {empresa.email}", estilo_texto),
            Paragraph(f"Teléfono: {empresa.telefono}", estilo_texto),
            Paragraph(f"Dirección: {empresa.direccion}", estilo_texto)
        ]
        elementos.extend(empresa_info)
        elementos.append(Paragraph("<br/><br/>", estilo_texto))  # Espacio en blanco
        # Información de la factura
        titulo = Paragraph(f"Factura ID: {factura.id}", estilo_titulo)
        cliente = Paragraph(f"Cliente: {factura.cliente.nombre} {factura.cliente.apellido}", estilo_texto)
        cliente_cedula = Paragraph(f"Cédula: {factura.cliente.cedula}", estilo_texto)
        cliente_email = Paragraph(f"Email: {factura.cliente.email}", estilo_texto)
        cliente_telefono = Paragraph(f"Teléfono: {factura.cliente.telefono}", estilo_texto)
        cliente_direccion = Paragraph(f"Dirección: {factura.cliente.direccion}", estilo_texto)
        fecha = Paragraph(f"Fecha: {localtime(factura.fecha).strftime('%d de %B de %Y %H:%M:%S')}", estilo_texto)
        elementos.append(titulo)
        elementos.append(cliente)
        elementos.append(cliente_cedula)
        elementos.append(cliente_email)
        elementos.append(cliente_telefono)
        elementos.append(cliente_direccion)
        elementos.append(fecha)
        elementos.append(Paragraph("<br/><br/>", estilo_texto))  # Espacio en blanco
        # Tabla de detalles
        data = [["Código", "Nombre", "Descripción", "Cantidad", "Precio Unitario", "Total"]]
        for detalle in factura.detalles.all():
            data.append([
                detalle.producto.codigo,
                detalle.producto.nombre,
                detalle.producto.descripcion or "",
                detalle.cantidad,
                f"${detalle.precio_unitario:.2f}",
                f"${detalle.precio_total:.2f}"
            ])
        # Totales
        data.append(["", "", "", "", "Subtotal", f"${factura.subtotal:.2f}"])
        data.append(["", "", "", "", "IVA", f"${factura.iva:.2f}"])
        data.append(["", "", "", "", "Total", f"${factura.total:.2f}"])
        # Crear tabla con estilos
        tabla = Table(data, colWidths=[80, 150, 200, 80, 100, 100])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10)
        ]))
        elementos.append(tabla)
        # Crear PDF
        doc.build(elementos)
