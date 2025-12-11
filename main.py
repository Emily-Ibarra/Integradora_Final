import customtkinter as ctk
import ui_views as views
import sys

# Configuración Global
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema Restaurante - El Pueblito")
        self.user = None
        self.current_frame = None
        
        # Contenedor principal
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        # Iniciar en Login
        self.show_view("Login")

    def set_user(self, user_data):
        self.user = user_data
        self.show_view("Dashboard")

    def logout(self):
        self.user = None
        self.show_view("Login")

    def show_view(self, view_name, **kwargs):
        # 1. Destruir vista anterior
        if self.current_frame:
            self.current_frame.destroy()
        
        # 2. LÓGICA DE PANTALLA
        w_screen = self.winfo_screenwidth()
        h_screen = self.winfo_screenheight()

        if view_name == "Login":
            # --- MODO VENTANA PEQUEÑA (LOGIN) ---
            w_win, h_win = 500, 650
            x = (w_screen - w_win) // 2
            y = (h_screen - h_win) // 2
            
            # Restaurar estado normal antes de cambiar tamaño
            if sys.platform.startswith("linux"):
                self.attributes('-zoomed', False)
            else:
                self.state('normal')
            
            self.geometry(f"{w_win}x{h_win}+{x}+{y}")
            self.resizable(False, False)

        else:
            # --- MODO PANTALLA COMPLETA (SISTEMA) ---
            self.resizable(True, True)
            
            
            self.update_idletasks() # Asegura que Tkinter esté listo para el cambio
            
            if sys.platform.startswith("linux"):
                self.attributes('-zoomed', True)
            else:
                try: 
                    self.state("zoomed")
                except: 
                    pass

        # 3. Cargar Vista
        if view_name == "Login":
            self.current_frame = views.LoginView(self.container, self)
        elif view_name == "Dashboard":
            self.current_frame = views.DashboardView(self.container, self)
        elif view_name == "Order":
            order_id = kwargs.get("order_id")
            self.current_frame = views.OrderView(self.container, self, order_id)
        elif view_name == "ListOrders":
            self.current_frame = views.OrdersListView(self.container, self, is_kitchen=False)
        elif view_name == "Kitchen":
            self.current_frame = views.OrdersListView(self.container, self, is_kitchen=True)
        elif view_name == "AdminMenu":
            self.current_frame = views.AdminMenuView(self.container, self)
        elif view_name == "AdminUsers":
            self.current_frame = views.AdminUsersView(self.container, self)
        
        self.current_frame.pack(fill="both", expand=True)

    def edit_order(self, pedido_data):
        self.temp_pedido_edit = pedido_data
        self.show_view("Order", order_id=pedido_data['id'])

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()