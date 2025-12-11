import customtkinter as ctk
from tkinter import messagebox, Menu
import backend as db
import styles as st

class MenuItemCard(ctk.CTkFrame):
    def __init__(self, master, item, command_add, command_sub):
        
        color = st.Color.DEFAULT
        if "Gordita" in item['categoria']: color = st.Color.CAT_GORDITA
        elif "Burro" in item['categoria']: color = st.Color.CAT_BURRO
        elif "Kilo" in item['categoria']: color = st.Color.CAT_KILO
        elif "Bebida" in item['categoria']: color = st.Color.CAT_BEBIDA

        super().__init__(master, fg_color=color, corner_radius=10)
        self.item = item
        
        
        ctk.CTkLabel(self, text=item['nombre'], font=st.font_bold(), text_color="black").pack(pady=(10,0))
        ctk.CTkLabel(self, text=f"${item['precio']}", text_color="#555").pack()

        
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(pady=10)

        ctk.CTkButton(ctrl_frame, text="-", width=30, fg_color=st.Color.DANGER, 
                      command=lambda: command_sub(item)).pack(side="left", padx=5)
        
        self.lbl_cant = ctk.CTkLabel(ctrl_frame, text="0", font=st.font_bold(), text_color="black", width=30)
        self.lbl_cant.pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_frame, text="+", width=30, fg_color=st.Color.SUCCESS, 
                      command=lambda: command_add(item)).pack(side="left", padx=5)

    def update_qty(self, qty):
        self.lbl_cant.configure(text=str(qty))



class LoginView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.PRIMARY)
        self.app = app
        
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=20, width=400)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="EL PUEBLITO", font=st.font_title(), text_color=st.Color.PRIMARY).pack(pady=30)
        
        self.user = ctk.CTkEntry(card, placeholder_text="Correo", width=300, height=40)
        self.user.pack(pady=10)
        
        self.pwd = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=300, height=40)
        self.pwd.pack(pady=10)
        
        ctk.CTkButton(card, text="INGRESAR", command=self.do_login, width=300, height=40, 
                      fg_color=st.Color.PRIMARY, hover_color=st.Color.SECONDARY).pack(pady=30)

    def do_login(self):
        u = db.login(self.user.get(), self.pwd.get())
        if u:
            messagebox.showinfo("Bienvenido", f"Hola, {u['nombre']}\nRol: {u['rol'].upper()}")
            self.app.set_user(u)
        else:
            messagebox.showerror("Error", "Credenciales Incorrectas")


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        
        
        nav = ctk.CTkFrame(self, fg_color=st.Color.PRIMARY, height=60, corner_radius=0)
        nav.pack(fill="x")
        
        ctk.CTkLabel(nav, text=f"USUARIO: {app.user['nombre'].upper()}", text_color="white", font=st.font_bold()).pack(side="left", padx=20)
        ctk.CTkButton(nav, text="CERRAR SESIÓN", fg_color="transparent", border_width=1, border_color="white", 
                      command=app.logout).pack(side="right", padx=20, pady=10)

       
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_menu_buttons()

    def show_menu_buttons(self):
        for w in self.main_content.winfo_children(): w.destroy()
        
        role = self.app.user['rol']
        
       
        grid = ctk.CTkFrame(self.main_content, fg_color="transparent")
        grid.pack(expand=True)

        options = []
        # Definición de permisos
        if role in ['admin', 'mesero']:
            options.extend([
                ("NUEVO PEDIDO", "➕", lambda: self.app.show_view("Order")),
                ("VER PEDIDOS / EDITAR", "📝", lambda: self.app.show_view("ListOrders")),
            ])
        if role in ['admin', 'cocina']:
            options.append(("COCINA", "👨‍🍳", lambda: self.app.show_view("Kitchen")))
        if role == 'admin':
            options.extend([
                ("ADMIN MENU", "🍔", lambda: self.app.show_view("AdminMenu")),
                ("ADMIN USUARIOS", "👥", lambda: self.app.show_view("AdminUsers")),
                ("REPORTE EXCEL", "📊", self.generar_excel)
            ])

        
        r, c = 0, 0
        for txt, icon, cmd in options:
            btn = ctk.CTkButton(grid, text=f"{icon}\n{txt}", font=st.font_subtitle(), width=220, height=150, 
                                corner_radius=15, fg_color="white", text_color="black", 
                                hover_color="#EEE", command=cmd)
            btn.grid(row=r, column=c, padx=15, pady=15)
            c += 1
            if c > 2:
                c = 0; r += 1

    def generar_excel(self):
        if db.exportar_excel():
            messagebox.showinfo("Éxito", "Reporte generado correctamente") # Punto 1

# --- VISTA PEDIDO (AGREGAR / EDITAR) FUSIONADA (Punto 6) ---
class OrderView(ctk.CTkFrame):
    def __init__(self, master, app, order_id=None):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        self.order_id = order_id
        self.cart = {} # {nombre: {obj_item, cantidad}}
        
        
        self.grid_columnconfigure(0, weight=1) # Menu
        self.grid_columnconfigure(1, weight=1) # Resumen
        self.grid_rowconfigure(0, weight=1)

        
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", pady=5)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar platillo...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(search_frame, text="🔍", width=40, command=self.load_menu).pack(side="right")
        self.entry_search.bind("<Return>", lambda e: self.load_menu())

        self.scroll_menu = ctk.CTkScrollableFrame(left_panel, label_text="MENÚ DISPONIBLE")
        self.scroll_menu.pack(fill="both", expand=True)

        
        right_panel = ctk.CTkFrame(self, fg_color="white")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(right_panel, text="DETALLES DE LA ORDEN", font=st.font_subtitle(), text_color=st.Color.PRIMARY).pack(pady=10)
        
        form = ctk.CTkFrame(right_panel, fg_color="transparent")
        form.pack(fill="x", padx=20)
        self.entry_cli = ctk.CTkEntry(form, placeholder_text="Nombre Cliente")
        self.entry_cli.pack(fill="x", pady=5)
        self.entry_mesa = ctk.CTkEntry(form, placeholder_text="Mesa")
        self.entry_mesa.pack(fill="x", pady=5)

        self.cart_frame = ctk.CTkScrollableFrame(right_panel, fg_color="#F9F9F9")
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_total = ctk.CTkLabel(right_panel, text="TOTAL: $0.00", font=st.font_title(), text_color=st.Color.PRIMARY)
        self.lbl_total.pack(pady=10)

        btns = ctk.CTkFrame(right_panel, fg_color="transparent")
        btns.pack(fill="x", pady=20, padx=20)
        ctk.CTkButton(btns, text="GUARDAR", fg_color=st.Color.SUCCESS, command=self.save_order).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(btns, text="CANCELAR", fg_color=st.Color.DANGER, command=lambda: app.show_view("Dashboard")).pack(side="right", fill="x", expand=True, padx=5)

        self.load_menu()
        if order_id: self.load_existing_order()

    def load_menu(self):
        for w in self.scroll_menu.winfo_children(): w.destroy()
        items = db.get_menu(self.entry_search.get())
        
        # Grid layout para tarjetas
        r, c = 0, 0
        for item in items:
            card = MenuItemCard(self.scroll_menu, item, self.add_item, self.sub_item)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            
            # Sincronizar si ya está en carrito
            if item['nombre'] in self.cart:
                card.update_qty(self.cart[item['nombre']]['cantidad'])
            
            # Guardamos referencia para actualizar UI luego
            item['ui_ref'] = card 
            
            c += 1
            if c > 2: c=0; r+=1

    def add_item(self, item):
        name = item['nombre']
        if name not in self.cart:
            self.cart[name] = {'data': item, 'cantidad': 0}
        self.cart[name]['cantidad'] += 1
        item['ui_ref'].update_qty(self.cart[name]['cantidad'])
        self.update_cart_ui()

    def sub_item(self, item):
        name = item['nombre']
        if name in self.cart and self.cart[name]['cantidad'] > 0:
            self.cart[name]['cantidad'] -= 1
            item['ui_ref'].update_qty(self.cart[name]['cantidad'])
            if self.cart[name]['cantidad'] == 0:
                del self.cart[name]
            self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_frame.winfo_children(): w.destroy()
        total = 0
        for name, info in self.cart.items():
            qty = info['cantidad']
            price = info['data']['precio']
            sub = qty * price
            total += sub
            
            row = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{qty} x {name}", anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"${sub:.2f}", anchor="e").pack(side="right")
        
        self.lbl_total.configure(text=f"TOTAL: ${total:.2f}")
        self.current_total = total

    def save_order(self):
        cli = self.entry_cli.get()
        mesa = self.entry_mesa.get()
        if not cli or not mesa or not self.cart:
            messagebox.showwarning("Faltan datos", "Revise cliente, mesa y carrito.")
            return

        items_list = [{"nombre": k, "precio": v['data']['precio'], "cantidad": v['cantidad']} for k, v in self.cart.items()]
        
        if db.guardar_pedido(cli, mesa, items_list, self.current_total, self.app.user['id'], self.order_id):
            messagebox.showinfo("Éxito", "Pedido guardado correctamente.") # Punto 1
            self.app.show_view("Dashboard")
        else:
            messagebox.showerror("Error", "No se pudo guardar.")

    def load_existing_order(self):
        
        pass

# --- LISTA DE PEDIDOS Y COCINA ---
class OrdersListView(ctk.CTkFrame):
    def __init__(self, master, app, is_kitchen=False):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        self.is_kitchen = is_kitchen
        
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        
        title = "COCINA - COMANDAS" if is_kitchen else "HISTORIAL DE PEDIDOS"
        ctk.CTkLabel(top, text=title, font=st.font_title()).pack(side="left")
        ctk.CTkButton(top, text="VOLVER", command=lambda: app.show_view("Dashboard"), fg_color="gray").pack(side="right")

        # Buscador (Punto 4)
        if not is_kitchen:
            self.entry_search = ctk.CTkEntry(top, placeholder_text="Buscar por Cliente o Mesa...")
            self.entry_search.pack(side="left", padx=20)
            ctk.CTkButton(top, text="Buscar", width=50, command=self.load_data).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.load_data()

    def load_data(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        search = self.entry_search.get() if hasattr(self, 'entry_search') else ""
        pedidos = db.obtener_pedidos(filtro_estado="pendiente" if self.is_kitchen else None, busqueda=search)

        if not pedidos:
            ctk.CTkLabel(self.scroll, text="No hay pedidos.").pack(pady=20)
            return

        # Grid responsivo
        r, c = 0, 0
        for p in pedidos:
            self.draw_card(p, r, c)
            c += 1
            if c > 2: c=0; r+=1 

    def draw_card(self, p, r, c):
        color = "#FFF"
        if p['estado'] == 'Listo': color = "#E8F5E9" 
        
        card = ctk.CTkFrame(self.scroll, fg_color=color, corner_radius=10, border_width=2, border_color="#DDD")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

        # Header
        head = ctk.CTkFrame(card, fg_color=st.Color.PRIMARY if p['estado']=='Pendiente' else st.Color.SUCCESS, height=30)
        head.pack(fill="x")
        ctk.CTkLabel(head, text=f"MESA {p['mesa']}", text_color="white", font=st.font_bold()).pack()

        # Body
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(body, text=f"Cliente: {p['cliente']}", font=st.font_bold()).pack(anchor="w")
        
        txt_items = ""
        for it in p['items']:
            txt_items += f"• {it['cantidad']} {it['nombre']}\n"
        
        lbl_items = ctk.CTkLabel(body, text=txt_items, justify="left", anchor="w")
        lbl_items.pack(anchor="w")

        # Footer Actions
        foot = ctk.CTkFrame(card, fg_color="transparent")
        foot.pack(fill="x", padx=5, pady=5)

        if self.is_kitchen:
            if p['estado'] == 'Pendiente':
                ctk.CTkButton(foot, text="MARCAR LISTO ✅", fg_color=st.Color.SUCCESS, 
                              command=lambda: self.change_status(p['id'], "Listo")).pack(fill="x")
        else:
            # Vista General (Admin/Mesero)
            ctk.CTkLabel(foot, text=f"Total: ${p['total']}", font=st.font_bold()).pack(side="left")
            ctk.CTkLabel(foot, text=p['estado'], text_color="gray").pack(side="right")
            
            # Botones Admin (Editar/Borrar)
            if self.app.user['rol'] == 'admin':
                 ctk.CTkButton(card, text="EDITAR", height=20, fg_color="#FFA000",
                               command=lambda: self.app.edit_order(p)).pack(fill="x", padx=5, pady=2)
                 ctk.CTkButton(card, text="ELIMINAR", height=20, fg_color="#D32F2F",
                               command=lambda: self.delete_order(p['id'])).pack(fill="x", padx=5, pady=(0,5))

    def change_status(self, pid, status):
        if db.cambiar_estado(pid, status):
            messagebox.showinfo("Estado", f"Pedido marcado como {status}")
            self.load_data()

    def delete_order(self, pid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este pedido permanentemente?"):
            db.eliminar_pedido(pid)
            self.load_data()

# --- ADMIN: GESTIÓN DE MENÚ (Punto 7) ---
class AdminMenuView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        
        ctk.CTkLabel(self, text="AGREGAR NUEVO PLATILLO", font=st.font_title()).pack(pady=20)
        
        form = ctk.CTkFrame(self, fg_color="white", padx=20, pady=20)
        form.pack()

        self.en_nom = ctk.CTkEntry(form, placeholder_text="Nombre Platillo", width=250)
        self.en_nom.pack(pady=5)
        
        self.en_cat = ctk.CTkComboBox(form, values=["Gorditas", "Burros", "Kilos", "Bebidas", "Extras"], width=250)
        self.en_cat.pack(pady=5)
        
        self.en_pre = ctk.CTkEntry(form, placeholder_text="Precio", width=250)
        self.en_pre.pack(pady=5)
        
        ctk.CTkButton(form, text="GUARDAR", command=self.guardar).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER", command=lambda: app.show_view("Dashboard"), fg_color="gray").pack()

    def guardar(self):
        try:
            precio = float(self.en_pre.get())
            if db.agregar_producto(self.en_nom.get(), self.en_cat.get(), precio):
                messagebox.showinfo("Éxito", "Producto agregado") # Punto 1
                self.en_nom.delete(0, "end"); self.en_pre.delete(0, "end")
            else:
                messagebox.showerror("Error", "No se pudo agregar")
        except: messagebox.showerror("Error", "Precio inválido")

# --- ADMIN: GESTIÓN DE USUARIOS (Punto 8) ---
class AdminUsersView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        
        ctk.CTkLabel(self, text="REGISTRAR PERSONAL", font=st.font_title()).pack(pady=20)
        
        form = ctk.CTkFrame(self, fg_color="white", padx=20, pady=20)
        form.pack()

        self.en_nom = ctk.CTkEntry(form, placeholder_text="Nombre Completo", width=250)
        self.en_nom.pack(pady=5)
        self.en_mail = ctk.CTkEntry(form, placeholder_text="Correo Electrónico", width=250)
        self.en_mail.pack(pady=5)
        self.en_pass = ctk.CTkEntry(form, placeholder_text="Contraseña", width=250)
        self.en_pass.pack(pady=5)
        self.en_rol = ctk.CTkComboBox(form, values=["mesero", "cocina", "admin"], width=250)
        self.en_rol.pack(pady=5)

        ctk.CTkButton(form, text="CREAR USUARIO", command=self.guardar).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER", command=lambda: app.show_view("Dashboard"), fg_color="gray").pack()

    def guardar(self):
        if db.crear_usuario(self.en_nom.get(), self.en_mail.get(), self.en_pass.get(), self.en_rol.get()):
            messagebox.showinfo("Éxito", f"Usuario {self.en_nom.get()} creado.") # Punto 1
        else:
            messagebox.showerror("Error", "Error al crear (¿Correo duplicado?)")