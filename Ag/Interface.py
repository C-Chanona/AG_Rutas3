import ttkbootstrap as ttkb
import tkintermapview as mp
import matplotlib.pyplot as plt
from ttkbootstrap.constants import LEFT, BOTH, VERTICAL, RIGHT, Y
import pandas as pd

class Interface:

    dataset = pd.read_excel("./completo.xlsx")
    types = dataset['nombre'].values.tolist()[:10]

    window = ttkb.Window(themename="darkly")
    map_widget = mp.TkinterMapView(window, width=760, height=450, corner_radius=20)
    style = ttkb.Style()

    @classmethod
    def create_input(cls, text, labx=None, laby=None, inpx=None, inpy=None):
        cls.style.configure("TLabel", font=("Arial", 12), background="#202020", foreground="White")
        label = ttkb.Label(cls.window, text=text, style="TLabel")
        entry = ttkb.Entry(cls.window)
        label.place(x=labx, y=laby), entry.place(x=inpx, y=inpy)
        entry.bind('<FocusIn>', cls.on_entry_click), entry.bind('<FocusOut>', cls.on_focusout)
        return entry
    
    @classmethod
    def create_combobox(cls, options, label_text, labx=None, laby=None, comx=None, comy=None):
        cls.style.configure('TCombobox', font=("Arial", 12), background="#202020", foreground="White")
        label = ttkb.Label(cls.window, text=label_text, style="TLabel")
        combobox = ttkb.Combobox(cls.window, values=options, style="TCombobox", bootstyle="info")
        label.place(x=labx, y=laby), combobox.place(x=comx, y=comy)
        return combobox

    @classmethod
    def create_window(cls, main):
        cls.window.title("Optimizador de rutas")
        # cls.window.geometry("810x850")
        cls.window.geometry("1320x850")
        window_width = cls.window.winfo_reqwidth()
        position_right = int(cls.window.winfo_screenwidth()/2 - window_width/2 - 200) -300
        cls.window.geometry("+{}+50".format(position_right))


        start_poi = cls.create_combobox(cls.types, "Punto de interes inicial para tu recorrido", labx=545, laby=140, comx=600, comy=200)

        cls.style.configure("TButton", font=("Arial", 12))
        button = ttkb.Button(cls.window, text="Iniciar", width=10, bootstyle='success-outline',
                           command=lambda: main(cls.dataset, start_poi.get()),
                           )
        button.place(x=350, y=270)
        button.bind("<Enter>", cls.on_enter), button.bind("<Leave>", cls.on_leave)

        # cls.map_widget.place(relx=0.3, rely=0.65, anchor='center')
        # cls.map_widget.set_zoom(15)
        # cls.map_widget.set_position(19.4326, -99.1332)
        # cls.create_table()

        cls.window.mainloop()
    
    @classmethod
    def on_entry_click(cls, event):
        event.widget.config(bootstyle='info')  # Cambia el estilo al hacer clic

    @classmethod
    def on_focusout(cls, event):
        event.widget.config(bootstyle='')  # Restablece el estilo cuando el foco se pierde
    
    @classmethod
    def on_enter(cls, event):
        event.widget.config(bootstyle='success')  # Cambia el estilo al pasar el ratón

    @classmethod
    def on_leave(cls, event):
        event.widget.config(bootstyle='success-outline')  # Restablece el estilo original al salir el ratón

    @classmethod
    def create_table(cls):
        # Crea el frame que contendrá la tabla
        table_frame = ttkb.Frame(cls.window)
        table_frame.place(x=810, y=50, width=490, height=730)  # Ajusta la posición y tamaño según necesites

        # Crea el Treeview dentro del frame
        cls.tree = ttkb.Treeview(table_frame, columns=("Uno", "Dos", "Tres", "Cuatro"), show="headings", bootstyle="info")
        cls.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Define las columnas
        cls.tree.heading("Uno", text="Punto de interés")
        cls.tree.heading("Dos", text="Nombre")
        cls.tree.heading("Tres", text="Tiempo de visita")
        cls.tree.heading("Cuatro", text="Distancia y Duracion")

        # Configura el tamaño de las columnas
        cls.tree.column("Uno", width=100)
        cls.tree.column("Dos", width=100)
        cls.tree.column("Tres", width=100)
        cls.tree.column("Cuatro", width=100)

        # Scrollbar para el Treeview
        scrollbar = ttkb.Scrollbar(table_frame, orient=VERTICAL, command=cls.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        cls.tree.configure(yscrollcommand=scrollbar.set)

    @classmethod
    def update_table(cls, route):
        # Elimina los datos existentes en la tabla
        for i in cls.tree.get_children():
            cls.tree.delete(i)
        
        # Verifica si hay elementos en la ruta
        if not route["path"]:
            return  # Sale de la función si la ruta está vacía
        
        # Añade el primer elemento con toda la información
        first_row = {
            "valor1": 1,
            "valor2": route["path"][0].name,
            "valor3": round(route["path"][0].visit_time, 2),
            "valor4": f"{round(route['distance'], 2)} km, {route['duration']} h"
        }
        cls.tree.insert("", "end", values=(first_row["valor1"], first_row["valor2"], first_row["valor3"], first_row["valor4"]))
        
        # Añade el resto de los elementos
        for index, path_item in enumerate(route["path"][1:], start=2):  # Comienza en el segundo elemento, índice ajustado a 2
            row = {
                "valor1": index,
                "valor2": path_item.name,
                "valor3": round(path_item.visit_time, 2),
                "valor4": ""  # Vacío para los siguientes elementos
            }
            cls.tree.insert("", "end", values=(row["valor1"], row["valor2"], row["valor3"], row["valor4"]))

    @classmethod
    def create_plot(cls, bests_by_generation):
        fitness_values = [individual['fitness'] for individual in bests_by_generation]
        generations = list(range(1, len(fitness_values) + 1))
        plt.plot(generations, fitness_values)
        plt.xlabel('Generación')
        plt.ylabel('Fitness del mejor individuo')
        plt.title('Evolución del Fitness del Mejor Individuo por Generación')
        plt.grid(True)
        plt.show()