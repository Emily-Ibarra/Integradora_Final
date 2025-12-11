import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import backend as db
import styles as st

# --- TARJETA DE PRODUCTO ---
class MenuItemCard(ctk.CTkFrame):
    def __init__(self, master, item, command_add, command_sub):
        color = st.Color.DEFAULT
        cat = item['categoria'].lower()
        if "gordita" in cat: color = st.Color.CAT_GORDITA
        elif "burro" in cat: color = st.Color.CAT_BURRO
        elif "kilo" in cat: color = st.Color.CAT_KILO
        elif "bebida" in cat: color = st.Color.CAT_BEBIDA

        super().__init__(master, fg_color=color, corner_radius=10, border_width=1, border_color="#DDD")
        
        ctk.CTkLabel(self, text=item['nombre'], font=("Segoe UI", 13, "bold"), text_color="black", wraplength=140).pack(pady=(10,0))
        ctk.CTkLabel(self, text=f"${item['precio']}", text_color="#555").pack()

        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(pady=10)

        ctk.CTkButton(ctrl_frame, text="-", width=35, height=35, fg_color=st.Color.DANGER, 
                      command=lambda: command_sub(item)).pack(side="left", padx=5)
        
        self.lbl_cant = ctk.CTkLabel(ctrl_frame, text="0", font=st.font_bold(), text_color="black", width=30)
        self.lbl_cant.pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_frame, text="+", width=35, height=35, fg_color=st.Color.SUCCESS, 
                      command=lambda: command_add(item)).pack(side="left", padx=5)

    def update_qty(self, qty):
        self.lbl_cant.configure(text=str(qty))


# --- PANTALLA LOGIN ---
class LoginView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.PRIMARY)
        self.app = app
        
        # Vincular tecla ENTER para ingresar
        self.master.bind('<Return>', lambda event: self.do_login())
        
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=20, width=400)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # LOGO
        try:
            if os.path.exists("logo.PNG"):
                img = ctk.CTkImage(light_image=Image.open("logo.PNG"), size=(150, 150))
                ctk.CTkLabel(card, image=img, text="").pack(pady=(30, 10))
        except Exception as e:
            print(f"No logo: {e}")

        ctk.CTkLabel(card, text="EL PUEBLITO", font=st.font_title(), text_color=st.Color.PRIMARY).pack(pady=(0, 20))
        
        self.user = ctk.CTkEntry(card, placeholder_text="Correo Electrónico", width=300, height=45)
        self.user.pack(pady=10)
        
        self.pwd = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=300, height=45)
        self.pwd.pack(pady=10)
        
        ctk.CTkButton(card, text="INGRESAR", command=self.do_login, width=300, height=50, 
                      fg_color=st.Color.PRIMARY, hover_color=st.Color.SECONDARY, font=st.font_subtitle()).pack(pady=30)

    def do_login(self):
        u = db.login(self.user.get(), self.pwd.get())
        if u:
            # 1. Mostrar mensaje (el código se detiene aquí hasta que das OK)
            messagebox.showinfo("Bienvenido", f"Hola {u['nombre']}\nRol: {u['rol'].upper()}")
            
            # 2. Desvincular Enter para que no afecte otras pantallas
            self.master.unbind('<Return>')
            
            # 3. Cambiar a pantalla completa (Dashboard)
            self.app.set_user(u)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")


# --- DASHBOARD ---
class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        
        nav = ctk.CTkFrame(self, fg_color=st.Color.PRIMARY, height=70, corner_radius=0)
        nav.pack(fill="x")
        ctk.CTkLabel(nav, text=f"Hola, {app.user['nombre']}", text_color="white", font=st.font_subtitle()).pack(side="left", padx=30)
        ctk.CTkButton(nav, text="CERRAR SESIÓN", fg_color="transparent", border_width=1, border_color="white", 
                      command=app.logout).pack(side="right", padx=20)

        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=40, pady=40)
        self.show_menu_buttons()

    def show_menu_buttons(self):
        role = self.app.user['rol']
        grid = ctk.CTkFrame(self.main_content, fg_color="transparent")
        grid.pack(expand=True)

        options = []
        if role in ['admin', 'mesero']:
             options.append(("NUEVO PEDIDO", "➕", lambda: self.app.show_view("Order")))
             options.append(("VER PEDIDOS", "📝", lambda: self.app.show_view("ListOrders")))
             
        if role in ['admin', 'cocina']:
            options.append(("COCINA / COMANDAS", "👨‍🍳", lambda: self.app.show_view("Kitchen")))
            
        if role == 'admin':
            options.extend([
                ("ADMIN MENU", "🍔", lambda: self.app.show_view("AdminMenu")),
                ("ADMIN USUARIOS", "👥", lambda: self.app.show_view("AdminUsers")),
                ("REPORTE EXCEL", "📊", self.generar_excel)
            ])

        r, c = 0, 0
        for txt, icon, cmd in options:
            btn = ctk.CTkButton(grid, text=f"{icon}\n{txt}", font=("Segoe UI", 20, "bold"), 
                                width=250, height=160, corner_radius=15, 
                                fg_color="white", text_color="black", hover_color="#EEE", command=cmd)
            btn.grid(row=r, column=c, padx=20, pady=20)
            c += 1
            if c > 2: c = 0; r += 1

    def generar_excel(self):
        if db.exportar_excel(): messagebox.showinfo("Éxito", "Excel generado.")
        else: messagebox.showwarning("Error", "No se guardó el archivo.")


# --- VISTA PEDIDO ---
class OrderView(ctk.CTkFrame):
    def __init__(self, master, app, order_id=None):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        self.order_id = order_id
        self.cart = {}
        
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        search_frame = ctk.CTkFrame(left_panel, fg_color="white")
        search_frame.pack(fill="x", pady=5)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar platillo...", height=40, font=st.font_normal())
        self.entry_search.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.entry_search.bind("<Return>", lambda e: self.load_menu())
        ctk.CTkButton(search_frame, text="🔍", width=50, command=self.load_menu).pack(side="right", padx=10)

        self.scroll_menu = ctk.CTkScrollableFrame(left_panel, label_text="MENÚ")
        self.scroll_menu.pack(fill="both", expand=True)

        right_panel = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(right_panel, text="DETALLES", font=st.font_title(), text_color=st.Color.PRIMARY).pack(pady=15)
        
        form = ctk.CTkFrame(right_panel, fg_color="transparent")
        form.pack(fill="x", padx=20)
        self.entry_cli = ctk.CTkEntry(form, placeholder_text="Cliente", height=40)
        self.entry_cli.pack(fill="x", pady=5)
        self.entry_mesa = ctk.CTkEntry(form, placeholder_text="Mesa", height=40)
        self.entry_mesa.pack(fill="x", pady=5)

        self.cart_frame = ctk.CTkScrollableFrame(right_panel, fg_color="#F5F5F5", height=300)
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_total = ctk.CTkLabel(right_panel, text="TOTAL: $0.00", font=("Segoe UI", 28, "bold"), text_color=st.Color.SUCCESS)
        self.lbl_total.pack(pady=10)

        btns = ctk.CTkFrame(right_panel, fg_color="transparent")
        btns.pack(fill="x", pady=20, padx=20)
        ctk.CTkButton(btns, text="GUARDAR", height=50, fg_color=st.Color.PRIMARY, command=self.save_order).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(btns, text="CANCELAR", height=50, fg_color="gray", command=lambda: app.show_view("Dashboard")).pack(side="right", fill="x", expand=True, padx=5)

        self.load_menu()
        if order_id: self.load_existing_order()

    def load_menu(self):
        for w in self.scroll_menu.winfo_children(): w.destroy()
        items = db.get_menu(self.entry_search.get())
        
        self.scroll_menu.grid_columnconfigure((0,1,2), weight=1)
        r, c = 0, 0
        for item in items:
            card = MenuItemCard(self.scroll_menu, item, self.add_item, self.sub_item)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
            if item['nombre'] in self.cart: card.update_qty(self.cart[item['nombre']]['cantidad'])
            item['ui_ref'] = card 
            c += 1
            if c > 2: c = 0; r += 1

    def add_item(self, item):
        name = item['nombre']
        if name not in self.cart: self.cart[name] = {'data': item, 'cantidad': 0}
        self.cart[name]['cantidad'] += 1
        item['ui_ref'].update_qty(self.cart[name]['cantidad'])
        self.update_cart_ui()

    def sub_item(self, item):
        name = item['nombre']
        if name in self.cart and self.cart[name]['cantidad'] > 0:
            self.cart[name]['cantidad'] -= 1
            item['ui_ref'].update_qty(self.cart[name]['cantidad'])
            if self.cart[name]['cantidad'] == 0: del self.cart[name]
            self.update_cart_ui()

    def update_cart_ui(self):
        for w in self.cart_frame.winfo_children(): w.destroy()
        total = 0
        for name, info in self.cart.items():
            qty = info['cantidad']
            price = float(info['data']['precio'])
            sub = qty * price
            total += sub
            row = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{qty} x", font=("Segoe UI", 12, "bold"), width=30).pack(side="left")
            ctk.CTkLabel(row, text=name, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=f"${sub:.2f}", anchor="e", width=60).pack(side="right")
        self.lbl_total.configure(text=f"TOTAL: ${total:.2f}")
        self.current_total = total

    def save_order(self):
        if not self.entry_cli.get() or not self.cart: return messagebox.showwarning("Error", "Faltan datos.")
        items_list = [{"nombre": k, "precio": float(v['data']['precio']), "cantidad": v['cantidad']} for k, v in self.cart.items()]
        if db.guardar_pedido(self.entry_cli.get(), self.entry_mesa.get(), items_list, self.current_total, self.app.user['id'], self.order_id):
            messagebox.showinfo("Éxito", "Pedido guardado.")
            self.app.show_view("Dashboard")
        else: messagebox.showerror("Error", "Error al guardar.")

    def load_existing_order(self):
        p = getattr(self.app, 'temp_pedido_edit', None)
        if p:
            self.entry_cli.insert(0, p['cliente'])
            self.entry_mesa.insert(0, p['mesa'])
            for item in p['items']:
                 mock = {"nombre": item['nombre'], "precio": item.get('precio', 0), "categoria": "Cargado"}
                 self.cart[item['nombre']] = {'data': mock, 'cantidad': item['cantidad']}
            self.update_cart_ui()


# --- VISTA LISTA PEDIDOS Y COCINA ---
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

        if not is_kitchen:
            bar = ctk.CTkFrame(top, fg_color="transparent")
            bar.pack(side="left", padx=40)
            self.search = ctk.CTkEntry(bar, placeholder_text="Buscar cliente...", width=200)
            self.search.pack(side="left", padx=5)
            ctk.CTkButton(bar, text="Buscar", width=60, command=self.load_data).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_data()

    def load_data(self):
        for w in self.scroll.winfo_children(): w.destroy()
        s = self.search.get() if hasattr(self, 'search') else ""
        filtro = "cocina" if self.is_kitchen else None
        pedidos = db.obtener_pedidos(filtro_estado=filtro, busqueda=s)

        if not pedidos:
            ctk.CTkLabel(self.scroll, text="No hay pedidos.").pack(pady=50)
            return

        self.scroll.grid_columnconfigure((0,1,2), weight=1)
        r, c = 0, 0
        for p in pedidos:
            self.draw_card(p, r, c)
            c += 1
            if c > 2: c = 0; r += 1

    def draw_card(self, p, r, c):
        color_bg = "#E8F5E9" if p['estado'] == 'Listo' else "white"
        card = ctk.CTkFrame(self.scroll, fg_color=color_bg, corner_radius=15, border_width=2, border_color="#DDD")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

        head_col = st.Color.SUCCESS if p['estado'] == 'Listo' else st.Color.PRIMARY
        head = ctk.CTkFrame(card, fg_color=head_col, height=35, corner_radius=0)
        head.pack(fill="x")
        ctk.CTkLabel(head, text=f"MESA {p['mesa']}", text_color="white", font=st.font_bold()).pack()

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(body, text=p['cliente'], font=st.font_subtitle()).pack(anchor="w")
        
        txt_items = ""
        for it in p['items']:
            txt_items += f"• {it['cantidad']} {it['nombre']}\n"
        
        ctk.CTkLabel(body, text=txt_items, justify="left", anchor="w", 
                     font=("Courier New", 16, "bold"), text_color="#333").pack(anchor="w", pady=5)

        foot = ctk.CTkFrame(card, fg_color="transparent")
        foot.pack(fill="x", padx=10, pady=10)

        rol = self.app.user['rol']
        
        if self.is_kitchen and p['estado'] == 'Pendiente':
             ctk.CTkButton(foot, text="MARCAR LISTO ✅", fg_color=st.Color.SUCCESS, height=40,
                           command=lambda: self.change_status(p['id'], "Listo")).pack(fill="x", pady=(0,5))

        if rol in ['admin', 'cocina']:
            admin_box = ctk.CTkFrame(card, fg_color="transparent")
            admin_box.pack(fill="x", pady=5)
            ctk.CTkButton(admin_box, text="EDITAR / DETALLES", height=30, fg_color=st.Color.WARNING,
                          command=lambda: self.app.edit_order(p)).pack(fill="x", padx=5)
            
            if rol == 'admin':
                 ctk.CTkButton(admin_box, text="BORRAR", height=30, fg_color=st.Color.DANGER,
                               command=lambda: self.delete_order(p['id'])).pack(fill="x", padx=5, pady=(5,0))

    def change_status(self, pid, status):
        if db.cambiar_estado(pid, status): self.load_data()

    def delete_order(self, pid):
        if messagebox.askyesno("Confirmar", "¿Eliminar?"): 
            db.eliminar_pedido(pid)
            self.load_data()


# --- ADMIN: MENU Y USUARIOS ---
class AdminMenuView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        ctk.CTkLabel(self, text="AGREGAR PLATILLO", font=st.font_title()).pack(pady=30)
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form.pack(padx=20, pady=20)
        self.en_nom = ctk.CTkEntry(form, placeholder_text="Nombre", width=300); self.en_nom.pack(pady=10)
        self.en_cat = ctk.CTkComboBox(form, values=["Gorditas","Burros","Kilos","Bebidas"], width=300); self.en_cat.pack(pady=10)
        self.en_pre = ctk.CTkEntry(form, placeholder_text="Precio", width=300); self.en_pre.pack(pady=10)
        ctk.CTkButton(form, text="GUARDAR", command=self.guardar, width=300, fg_color=st.Color.SUCCESS).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER", command=lambda: app.show_view("Dashboard"), fg_color="gray").pack()

    def guardar(self):
        try:
            if db.agregar_producto(self.en_nom.get(), self.en_cat.get(), float(self.en_pre.get())):
                messagebox.showinfo("Éxito","Guardado"); self.en_nom.delete(0,"end"); self.en_pre.delete(0,"end")
        except: messagebox.showerror("Error","Revise datos")

class AdminUsersView(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=st.Color.BG_MAIN)
        self.app = app
        ctk.CTkLabel(self, text="NUEVO EMPLEADO", font=st.font_title()).pack(pady=30)
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form.pack(padx=20, pady=20)
        self.en_nom = ctk.CTkEntry(form, placeholder_text="Nombre", width=300); self.en_nom.pack(pady=10)
        self.en_mail = ctk.CTkEntry(form, placeholder_text="Correo", width=300); self.en_mail.pack(pady=10)
        self.en_pass = ctk.CTkEntry(form, placeholder_text="Contraseña", width=300); self.en_pass.pack(pady=10)
        self.en_rol = ctk.CTkComboBox(form, values=["mesero","cocina","admin"], width=300); self.en_rol.pack(pady=10)
        ctk.CTkButton(form, text="CREAR", command=self.guardar, width=300).pack(pady=20)
        ctk.CTkButton(self, text="VOLVER", command=lambda: app.show_view("Dashboard"), fg_color="gray").pack()

    def guardar(self):
        if db.crear_usuario(self.en_nom.get(), self.en_mail.get(), self.en_pass.get(), self.en_rol.get()):
            messagebox.showinfo("Éxito","Usuario creado")
        else: messagebox.showerror("Error","No se creó")