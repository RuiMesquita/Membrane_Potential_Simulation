import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
from PIL import ImageTk, Image


def gui():
    gui_variables = []
    # ================================================== Interface grafica =======================================================================
    root = tk.Tk()
    root.title("Initial Menu")
    root.configure(background="#C6C5B9")

    # Ler as imagens
    colorpicker_icon = ImageTk.PhotoImage(Image.open("./images/colorpicker.png"), master=root)
    info_icon = ImageTk.PhotoImage(Image.open("./images/info_icon.png"), master=root)
    isep_icon = ImageTk.PhotoImage(Image.open("./images/isepLogo2.png"), master=root)

    # Botao de informacoes

    def openInfo():
        messagebox.showinfo('Information', "Controls: \n\ni - Information related with Voltage\ne - Instant Kinetic Energy Value\nn - Add sodium ions\nk - add potassium ions\na - remove sodium ions\ns - remove potassium ions\nESC - Pause/Resume\nLeft/Righ arrow key - change backgound color")

    # Guarda os valores inseridos numa lista e destroi a janela da interface

    def startProgram():
        try:
            color_k = colorEntryK.get()
            color_Na = colorEntryNa.get()
            number_Na = Na_entry.get()
            number_K = K_entry.get()
            if int(number_K) + int(number_Na) > 250:
                msg_box = tk.messagebox.askquestion(title="Warning!", message="A number above 250 ions may drastically reduce the performance of the simulation. Wish to proceed?", icon='warning')
                if msg_box == 'yes':
                    gui_variables.append(color_k)
                    gui_variables.append(color_Na)
                    gui_variables.append(number_Na)
                    gui_variables.append(number_K)
                    root.destroy()
                else:
                    pass
            else:
                gui_variables.append(color_k)
                gui_variables.append(color_Na)
                gui_variables.append(number_Na)
                gui_variables.append(number_K)
                root.destroy()
        except Exception:
            print("Invalid values")

    # Permite escolher a cor das particulas de sodio

    def chooseNacolor():
        try:
            Na_color = colorchooser.askcolor()
            colorEntryNa.delete(0, tk.END)
            colorEntryNa.insert(tk.END, Na_color[0])
        except Exception:
            print("No color selected for sodium. Insert a color to proceed")

    # Permite escolher a cor das particulas de potassio

    def chooseKcolor():
        try:
            K_color = colorchooser.askcolor()
            colorEntryK.delete(0, tk.END)
            colorEntryK.insert(tk.END, K_color[0])
        except Exception:
            print("No color selected for potassium. Insert a color to proceed")

    # Atribui valores default a todas as entradas de texto

    def defaultValues():
        # limpar as caixas todas
        Na_entry.delete(0, tk.END)
        K_entry.delete(0, tk.END)
        colorEntryK.delete(0, tk.END)
        colorEntryNa.delete(0, tk.END)

        # Atribuir valores default
        Na_entry.insert(tk.END, 75)
        K_entry.insert(tk.END, 75)
        colorEntryK.insert(tk.END, (0, 0, 255))
        colorEntryNa.insert(tk.END, (255, 0, 0))

    # Butoes, labels e entradas de texto
    isep_log = tk.Label(root, image=isep_icon, padx=10, pady=10, bd=0, background="#C6C5B9")

    Na_label = tk.Label(root, text="Nº of sodiums", pady=5, justify=tk.LEFT, bg="#393D3F", fg="#FFFFFF")
    K_label = tk.Label(root, text="Nº of potassiums", pady=5, justify=tk.LEFT, bg="#393D3F", fg="#FFFFFF")
    labelColor1 = tk.Label(root, text="Ion color", pady=5, padx=33, justify=tk.LEFT, bg="#393D3F", fg="#FFFFFF")
    labelColor2 = tk.Label(root, text="Ion color", pady=5, padx=33, justify=tk.LEFT, bg="#393D3F", fg="#FFFFFF")

    Na_entry = tk.Entry(root)
    K_entry = tk.Entry(root)
    colorEntryNa = tk.Entry(root, relief=tk.SUNKEN)
    colorEntryK = tk.Entry(root, relief=tk.SUNKEN)

    colorNa_button = tk.Button(root, image=colorpicker_icon, compound=tk.CENTER, command=chooseNacolor, bd=3, bg="#FFFFFF")
    colorK_button = tk.Button(root, image=colorpicker_icon, compound=tk.CENTER, command=chooseKcolor, bd=3, bg="#FFFFFF")
    default_button = tk.Button(root, text="Insert Default Values", command=defaultValues, padx=4, pady=4, bg="#393D3F", fg="#FFFFFF")

    startButton = tk.Button(root, text="Start Simulation", command=startProgram, padx=4, pady=4, bg="#393D3F", fg="#FFFFFF")
    infoButton = tk.Button(root, image=info_icon, padx=0, command=openInfo, justify=tk.LEFT, bd=0, bg="#C6C5B9")

    # Meter os widgets no ecra
    isep_log.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    Na_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E + tk.W)
    labelColor1.grid(row=1, column=1, padx=10, pady=5)
    colorEntryNa.grid(row=2, column=1, padx=10, pady=5)
    Na_entry.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W + tk.E)
    colorNa_button.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W + tk.E)

    K_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E + tk.W)
    labelColor2.grid(row=3, column=1, padx=10, pady=5)
    colorEntryK.grid(row=4, column=1, padx=10, pady=5)
    K_entry.grid(row=4, column=0, padx=10, pady=5, sticky=tk.E + tk.W)
    colorK_button.grid(row=4, column=2, padx=10, pady=5, sticky=tk.W + tk.E)

    startButton.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W)
    infoButton.grid(row=7, column=0, padx=10, ipadx=0, pady=5, sticky=tk.W)
    default_button.grid(row=6, column=0, columnspan=3, padx=10, pady=1, sticky=tk.E + tk.W)

    root.mainloop()
    return gui_variables
