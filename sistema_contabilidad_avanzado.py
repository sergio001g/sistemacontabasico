import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os
import shutil

class SistemaContabilidad:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Contabilidad Avanzado para Mercados")
        self.root.geometry("1000x700")
        
        self.items = self.cargar_items()
        self.combo_items = None # Update 1
        self.ventas = self.cargar_ventas()
        self.modo_oscuro = False
        
        self.crear_menu()
        self.crear_pestanas()
        self.actualizar_interfaz()
    
    def crear_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Exportar Inventario", command=self.exportar_inventario)
        archivo_menu.add_command(label="Exportar Ventas", command=self.exportar_ventas)
        archivo_menu.add_command(label="Hacer Respaldo", command=self.hacer_respaldo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        
        ver_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ver", menu=ver_menu)
        ver_menu.add_command(label="Cambiar Modo", command=self.cambiar_modo)
    
    def crear_pestanas(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_ventas = ttk.Frame(self.notebook)
        self.tab_informes = ttk.Frame(self.notebook)
        self.tab_estadisticas = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_inventario, text="Inventario")
        self.notebook.add(self.tab_ventas, text="Ventas")
        self.notebook.add(self.tab_informes, text="Informes")
        self.notebook.add(self.tab_estadisticas, text="Estadísticas")
        
        self.crear_tab_inventario()
        self.crear_tab_ventas()
        self.crear_tab_informes()
        self.crear_tab_estadisticas()
    
    def crear_tab_inventario(self):
        frame_añadir = ttk.LabelFrame(self.tab_inventario, text="Añadir/Editar Item")
        frame_añadir.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame_añadir, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = ttk.Entry(frame_añadir)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_añadir, text="Precio:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_precio = ttk.Entry(frame_añadir)
        self.entry_precio.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_añadir, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_cantidad = ttk.Entry(frame_añadir)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_añadir, text="Categoría:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_categoria = ttk.Entry(frame_añadir)
        self.entry_categoria.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Button(frame_añadir, text="Añadir/Actualizar", command=self.añadir_item).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(frame_añadir, text="Eliminar", command=self.eliminar_item).grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        frame_buscar = ttk.Frame(self.tab_inventario)
        frame_buscar.pack(padx=10, pady=5, fill="x")
        
        self.entry_buscar = ttk.Entry(frame_buscar, width=30)
        self.entry_buscar.pack(side="left", padx=5)
        ttk.Button(frame_buscar, text="Buscar", command=self.buscar_item).pack(side="left")
        
        self.tree_inventario = ttk.Treeview(self.tab_inventario, columns=("Nombre", "Precio", "Cantidad", "Categoría"), show="headings")
        self.tree_inventario.heading("Nombre", text="Nombre")
        self.tree_inventario.heading("Precio", text="Precio")
        self.tree_inventario.heading("Cantidad", text="Cantidad")
        self.tree_inventario.heading("Categoría", text="Categoría")
        self.tree_inventario.pack(padx=10, pady=10, expand=True, fill="both")
        
        self.tree_inventario.bind("<ButtonRelease-1>", self.seleccionar_item)
        
        self.actualizar_inventario()
    
    def crear_tab_ventas(self):
        frame_venta = ttk.LabelFrame(self.tab_ventas, text="Registrar Venta")
        frame_venta.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame_venta, text="Item:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_items = ttk.Combobox(frame_venta, values=list(self.items.keys()))
        self.combo_items.grid(row=0, column=1, padx=5, pady=5)
        self.actualizar_inventario() # Update 3
        
        ttk.Label(frame_venta, text="Cantidad:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_venta_cantidad = ttk.Entry(frame_venta)
        self.entry_venta_cantidad.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_venta, text="Descuento (%):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_descuento = ttk.Entry(frame_venta)
        self.entry_descuento.grid(row=1, column=1, padx=5, pady=5)
        self.entry_descuento.insert(0, "0")
        
        ttk.Button(frame_venta, text="Registrar Venta", command=self.registrar_venta).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        self.tree_ventas = ttk.Treeview(self.tab_ventas, columns=("Fecha", "Item", "Cantidad", "Total", "Descuento"), show="headings")
        self.tree_ventas.heading("Fecha", text="Fecha")
        self.tree_ventas.heading("Item", text="Item")
        self.tree_ventas.heading("Cantidad", text="Cantidad")
        self.tree_ventas.heading("Total", text="Total")
        self.tree_ventas.heading("Descuento", text="Descuento")
        self.tree_ventas.pack(padx=10, pady=10, expand=True, fill="both")
        
        self.actualizar_ventas()
    
    def crear_tab_informes(self):
        ttk.Button(self.tab_informes, text="Generar Informe de Ventas", command=self.generar_informe_ventas).pack(padx=10, pady=10)
        ttk.Button(self.tab_informes, text="Generar Informe de Inventario", command=self.generar_informe_inventario).pack(padx=10, pady=10)
        
        self.text_informe = tk.Text(self.tab_informes, height=20, width=80)
        self.text_informe.pack(padx=10, pady=10, expand=True, fill="both")
    
    def crear_tab_estadisticas(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_estadisticas)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        ttk.Button(self.tab_estadisticas, text="Ventas por Día", command=lambda: self.mostrar_grafico('dia')).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.tab_estadisticas, text="Ventas por Categoría", command=lambda: self.mostrar_grafico('categoria')).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.tab_estadisticas, text="Top 5 Productos", command=lambda: self.mostrar_grafico('top')).pack(side=tk.LEFT, padx=5, pady=5)
    
    def cargar_items(self):
        try:
            with open("items.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def guardar_items(self):
        with open("items.txt", "w") as file:
            json.dump(self.items, file)
    
    def cargar_ventas(self):
        try:
            with open("ventas.txt", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    def guardar_ventas(self):
        with open("ventas.txt", "w") as file:
            json.dump(self.ventas, file)
    
    def añadir_item(self):
        nombre = self.entry_nombre.get()
        precio = self.entry_precio.get()
        cantidad = self.entry_cantidad.get()
        categoria = self.entry_categoria.get()
        
        if nombre and precio and cantidad and categoria:
            try:
                precio = float(precio)
                cantidad = int(cantidad)
                self.items[nombre] = {"precio": precio, "cantidad": cantidad, "categoria": categoria}
                self.guardar_items()
                self.actualizar_inventario()
                self.limpiar_campos_item()
                messagebox.showinfo("Éxito", "Item añadido/actualizado correctamente")
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
    
    def eliminar_item(self):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion)['values'][0]
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar {item}?"):
                del self.items[item]
                self.guardar_items()
                self.actualizar_inventario()
                self.limpiar_campos_item()
        else:
            messagebox.showerror("Error", "Por favor, seleccione un item para eliminar")
    
    def seleccionar_item(self, event):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion)['values']
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, item[0])
            self.entry_precio.delete(0, tk.END)
            self.entry_precio.insert(0, item[1])
            self.entry_cantidad.delete(0, tk.END)
            self.entry_cantidad.insert(0, item[2])
            self.entry_categoria.delete(0, tk.END)
            self.entry_categoria.insert(0, item[3])
    
    def limpiar_campos_item(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_cantidad.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
    
    def buscar_item(self):
        busqueda = self.entry_buscar.get().lower()
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        for nombre, datos in self.items.items():
            if busqueda in nombre.lower() or busqueda in datos['categoria'].lower():
                self.tree_inventario.insert("", "end", values=(nombre, f"${datos['precio']:.2f}", datos['cantidad'], datos['categoria']))
    
    def actualizar_inventario(self):
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        for nombre, datos in self.items.items():
            self.tree_inventario.insert("", "end", values=(nombre, f"${datos['precio']:.2f}", datos['cantidad'], datos['categoria']))
        if hasattr(self, 'combo_items') and self.combo_items: # Update 2
            self.combo_items['values'] = list(self.items.keys())
        self.verificar_inventario_bajo()
    
    def verificar_inventario_bajo(self):
        items_bajos = [nombre for nombre, datos in self.items.items() if datos['cantidad'] < 5]
        if items_bajos:
            messagebox.showwarning("Alerta de Inventario", f"Los siguientes items están bajos en inventario:\n{', '.join(items_bajos)}")
    
    def registrar_venta(self):
        item = self.combo_items.get()
        cantidad = self.entry_venta_cantidad.get()
        descuento = self.entry_descuento.get()
        
        if item and cantidad and descuento:
            try:
                cantidad = int(cantidad)
                descuento = float(descuento)
                if item in self.items and self.items[item]['cantidad'] >= cantidad:
                    precio_unitario = self.items[item]['precio']
                    total = precio_unitario * cantidad
                    total_con_descuento = total * (1 - descuento / 100)
                    self.items[item]['cantidad'] -= cantidad
                    self.guardar_items()
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    venta = {
                        "fecha": fecha,
                        "item": item,
                        "cantidad": cantidad,
                        "total": total_con_descuento,
                        "descuento": descuento
                    }
                    self.ventas.append(venta)
                    self.guardar_ventas()
                    self.actualizar_inventario()
                    self.actualizar_ventas()
                    self.entry_venta_cantidad.delete(0, tk.END)
                    self.entry_descuento.delete(0, tk.END)
                    self.entry_descuento.insert(0, "0")
                    self.generar_recibo(venta)
                    messagebox.showinfo("Éxito", f"Venta registrada: {cantidad} {item}(s) por ${total_con_descuento:.2f}")
                else:
                    messagebox.showerror("Error", "Cantidad insuficiente en inventario")
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
    
    def actualizar_ventas(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        for venta in self.ventas:
            self.tree_ventas.insert("", 0, values=(venta['fecha'], venta['item'], venta['cantidad'], f"${venta['total']:.2f}", f"{venta['descuento']}%"))
    
    def generar_informe_ventas(self):
        if self.ventas:
            total_ventas = sum(venta['total'] for venta in self.ventas)
            informe = f"Informe de Ventas\n\n"
            informe += f"Total de ventas: ${total_ventas:.2f}\n"
            informe += f"Número de transacciones: {len(self.ventas)}\n\n"
            informe += "Detalles de ventas:\n"
            for venta in self.ventas:
                informe += f"{venta['fecha']} - {venta['item']}: {venta['cantidad']} unidades, ${venta['total']:.2f}, Descuento: {venta['descuento']}%\n"
            
            self.text_informe.delete(1.0, tk.END)
            self.text_informe.insert(tk.END, informe)
        else:
            messagebox.showinfo("Informe de Ventas", "No hay ventas registradas")
    
    def generar_informe_inventario(self):
        informe = "Informe de Inventario\n\n"
        valor_total = 0
        for nombre, datos in self.items.items():
            valor_item = datos['precio'] * datos['cantidad']
            valor_total += valor_item
            informe += f"{nombre}: {datos['cantidad']} unidades, ${datos['precio']:.2f} c/u, Total: ${valor_item:.2f}, Categoría: {datos['categoria']}\n"
        informe += f"\nValor total del inventario: ${valor_total:.2f}"
        
        self.text_informe.delete(1.0, tk.END)
        self.text_informe.insert(tk.END, informe)
    
    def mostrar_grafico(self, tipo):
        self.ax.clear()
        if tipo == 'dia':
            ventas_por_dia = {}
            for venta in self.ventas:
                fecha = venta['fecha'].split()[0]
                ventas_por_dia[fecha] = ventas_por_dia.get(fecha, 0) + venta['total']
            fechas = list(ventas_por_dia.keys())
            totales = list(ventas_por_dia.values())
            self.ax.bar(fechas, totales)
            self.ax.set_xlabel('Fecha')
            self.ax.set_ylabel('Total de Ventas')
            self.ax.set_title('Ventas por Día')
        elif tipo == 'categoria':
            ventas_por_categoria = {}
            for venta in self.ventas:
                categoria = self.items[venta['item']]['categoria']
                ventas_por_categoria[categoria] = ventas_por_categoria.get(categoria, 0) + venta['total']
            categorias = list(ventas_por_categoria.keys())
            totales = list(ventas_por_categoria.values())
            self.ax.pie(totales, labels=categorias, autopct='%1.1f%%')
            self.ax.set_title('Ventas por Categoría')
        elif tipo == 'top':
            ventas_por_producto = {}
            for venta in self.ventas:
                ventas_por_producto[venta['item']] = ventas_por_producto.get(venta['item'], 0) + venta['cantidad']
            top_productos = sorted(ventas_por_producto.items(), key=lambda x: x[1], reverse=True)[:5]
            productos, cantidades = zip(*top_productos)
            self.ax.bar(productos, cantidades)
            self.ax.set_xlabel('Producto')
            self.ax.set_ylabel('Cantidad Vendida')
            self.ax.set_title('Top 5 Productos Más Vendidos')
        
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()
    
    def exportar_inventario(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Nombre", "Precio", "Cantidad", "Categoría"])
                for nombre, datos in self.items.items():
                    writer.writerow([nombre, datos['precio'], datos['cantidad'], datos['categoria']])
            messagebox.showinfo("Éxito", f"Inventario exportado a {filename}")
    
    def exportar_ventas(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Fecha", "Item", "Cantidad", "Total", "Descuento"])
                for venta in self.ventas:
                    writer.writerow([venta['fecha'], venta['item'], venta['cantidad'], venta['total'], venta['descuento']])
            messagebox.showinfo("Éxito", f"Ventas exportadas a {filename}")
    
    def hacer_respaldo(self):
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta_respaldo = f"respaldo_{fecha_actual}"
        os.mkdir(carpeta_respaldo)
        shutil.copy("items.txt", carpeta_respaldo)
        shutil.copy("ventas.txt", carpeta_respaldo)
        messagebox.showinfo("Éxito", f"Respaldo creado en la carpeta {carpeta_respaldo}")
    
    def cambiar_modo(self):
        self.modo_oscuro = not self.modo_oscuro
        self.actualizar_interfaz()
    
    def actualizar_interfaz(self):
        estilo = ttk.Style()
        if self.modo_oscuro:
            estilo.theme_use('clam')
            estilo.configure(".", background="black", foreground="white")
            estilo.configure("TNotebook", background="black")
            estilo.configure("TNotebook.Tab", background="gray", foreground="white")
            estilo.configure("TFrame", background="black")
            estilo.configure("TLabel", background="black", foreground="white")
            estilo.configure("TButton", background="gray", foreground="white")
            estilo.configure("Treeview", background="black", foreground="white", fieldbackground="black")
            estilo.configure("Treeview.Heading", background="gray", foreground="white")
        else:
            estilo.theme_use('default')
    
    def generar_recibo(self, venta):
        recibo = f"""
        ===== RECIBO DE VENTA =====
        Fecha: {venta['fecha']}
        Item: {venta['item']}
        Cantidad: {venta['cantidad']}
        Precio unitario: ${self.items[venta['item']]['precio']:.2f}
        Descuento: {venta['descuento']}%
        Total: ${venta['total']:.2f}
        ============================
        """
        print(recibo)  # En una aplicación real, esto se enviaría a una impresora o se guardaría en un archivo

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaContabilidad(root)
    root.mainloop()

