from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
import wx
from gestion.db_connection import Producto, Proveedor, Categoria, Factura, DetalleFactura, Cliente, generar_factura
from decimal import Decimal
from gestion.gestion_clientes.agregar_cliente import AgregarCliente

class MenuCompras(wx.Frame):
    def __init__(self, parent):
        super(MenuCompras, self).__init__(parent, title="Menu de Compras", size=(800, 600))
        self.carrito = []
        self.InitUI()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Etiqueta para la lista de productos
        self.label_productos = wx.StaticText(panel, label="Lista de Productos:")
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
        self.label_carrito = wx.StaticText(panel, label="Carrito de Compras:")
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

        # Ocultar botones y el carrito de compras al inicio
        self.btn_quitar.Hide()
        self.btn_facturar.Hide()
        self.carrito_list.Hide()

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


    def generar_pdf_factura(self, factura):

        from django.utils.timezone import localtime # importar la hora local de django para que la fecha sea correcta y acorde con la hora local.
        # Crear carpeta si no existe
        if not os.path.exists('facturas'):
            os.makedirs('facturas')

        # Ruta del PDF
        pdf_path = f"facturas/factura_{factura.id}.pdf"
        # Crear documento
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elementos = []

        # Estilos
        styles = getSampleStyleSheet()
        estilo_titulo = styles['Heading1']
        estilo_texto = styles['Normal']

        # Encabezado
        titulo = Paragraph(f"Factura ID: {factura.id}", estilo_titulo)
        cliente = Paragraph(f"Cliente: {factura.cliente.nombre} {factura.cliente.apellido}", estilo_texto)
        fecha_formateada = localtime(factura.fecha).strftime('%d de %B de %Y %H:%M:%S') # Formatear la fecha a la hora local
        fecha = Paragraph(f"Fecha: {fecha_formateada}", estilo_texto)
        elementos.append(titulo)
        elementos.append(cliente)
        elementos.append(fecha)
        # Tabla de detalles
        data = [["Código", "Nombre", "Cantidad", "Precio Unitario", "Total"]]
        for detalle in factura.detalles.all():
            data.append([
                detalle.producto.codigo,
                detalle.producto.nombre,
                detalle.cantidad,
                f"${detalle.precio_unitario:.2f}",
                f"${detalle.precio_total:.2f}"
            ])

        # Totales
        data.append(["", "", "", "Subtotal", f"${factura.subtotal:.2f}"])
        data.append(["", "", "", "IVA", f"${factura.iva:.2f}"])
        data.append(["", "", "", "Total", f"${factura.total:.2f}"])
        # Crear tabla con estilos
        tabla = Table(data, colWidths=[80, 150, 80, 100, 100])
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

    def generar_factura(self, event):
        if not self.carrito:
            wx.MessageBox('El carrito está vacío', 'Error', wx.OK | wx.ICON_ERROR)
            return

        # Diálogo para seleccionar cliente
        dlg = wx.TextEntryDialog(self, 'Ingrese la cédula del cliente:', 'Cliente')
        if dlg.ShowModal() == wx.ID_OK:
            try:
                cliente = Cliente.objects.get(cedula=dlg.GetValue())
                
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
                
                # Limpiar carrito
                self.carrito = []
                self.carrito_list.DeleteAllItems()
                self.actualizar_lista(None)
                self.Layout()
                # generar el pdf con los detalles de la factura.
                self.generar_pdf_factura(factura)
                wx.MessageBox(f'Factura generada con éxito\nTotal: ${factura.total}', 'Éxito', wx.OK | wx.ICON_INFORMATION)
                self.btn_quitar.Hide()
                self.btn_facturar.Hide()
                self.carrito_list.Hide()
                self.Layout()
            except Cliente.DoesNotExist:
                wx.MessageBox('Cliente no encontrado. Agregue el cliente.', 'Error', wx.OK | wx.ICON_ERROR)
                dlg.Destroy()
                # Abrir el formulario para agregar un cliente
                agregar_cliente = AgregarCliente(self.actualizar_lista)
            except Exception as e:
                wx.MessageBox(f'Error al generar la factura: {str(e)}', 'Error', wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

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

    def agregar_al_carrito(self, event):
        """Agregar producto seleccionado al carrito"""
        selected = self.list_control.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Seleccione un producto primero.", "Error", wx.ICON_ERROR)
            return
        # Obtener detalles del producto seleccionado
        codigo = self.list_control.GetItemText(selected, 0)
        try:
            # Buscar el objeto Producto en la base de datos
            producto = Producto.objects.get(codigo=codigo)
        except Producto.DoesNotExist:
            wx.MessageBox("El producto no existe en la base de datos.", "Error", wx.ICON_ERROR)
            return
        # Abrir un cuadro de diálogo para ingresar la cantidad
        dlg = wx.TextEntryDialog(self, 'Ingrese la cantidad:', 'Cantidad', '1')
        if dlg.ShowModal() == wx.ID_OK:
            try:
                cantidad = int(dlg.GetValue())
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a cero.")
                if cantidad > producto.stock:
                    wx.MessageBox(f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles.", "Error", wx.ICON_ERROR)
                    return
                # Calcular el total
                precio = float(producto.precio)
                total = cantidad * precio
                # Agregar el producto al carrito
                self.carrito.append({
                    'producto': producto,  # Agregar el objeto Producto al carrito
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'cantidad': cantidad,
                    'precio': precio,
                    'total': total
                })
                # Actualizar la lista del carrito
                index = self.carrito_list.GetItemCount()
                self.carrito_list.InsertItem(index, producto.codigo)
                self.carrito_list.SetItem(index, 1, producto.nombre)
                self.carrito_list.SetItem(index, 2, str(cantidad))
                self.carrito_list.SetItem(index, 3, f"${precio:.2f}")
                self.carrito_list.SetItem(index, 4, f"${total:.2f}")
                # Hacer visibles los botones y el carrito
                self.btn_quitar.Show()
                self.btn_facturar.Show()
                self.carrito_list.Show()
            except ValueError as e:
                wx.MessageBox(f"Entrada no válida: {e}", "Error", wx.ICON_ERROR)
        dlg.Destroy()


    def volver(self, event):
        self.Parent.Show()
        self.Destroy()

