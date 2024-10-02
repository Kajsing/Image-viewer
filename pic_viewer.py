# Importér nødvendige biblioteker
import os
import shutil
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ExifTags
import exifread

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Avanceret Billedfremviser")
        
        # Opret hovedramme
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Opret billedramme
        self.image_frame = Frame(self.main_frame)
        self.image_frame.pack(fill=BOTH, expand=True)
        
        self.image_label = Label(self.image_frame)
        self.image_label.pack(fill=BOTH, expand=True)
        
        # Opret toolbar i bunden
        self.toolbar = Frame(self.main_frame, bg='#f0f0f0')
        self.toolbar.pack(side=BOTTOM, fill=X)
        
        # Opret knapper med farver og ikoner
        self.open_button = Button(self.toolbar, text="Åbn Mappe", command=self.open_folder, bg='#4CAF50', fg='white', padx=10)
        self.open_button.pack(side=LEFT, padx=5, pady=5)
        
        # Dropdown menu til sortering
        self.sort_var = StringVar(value="Navn")
        self.sort_menu = OptionMenu(self.toolbar, self.sort_var, "Navn", "Dato", "Størrelse", "Filtype", command=self.sort_images)
        self.sort_menu.config(bg='#2196F3', fg='white')
        self.sort_menu.pack(side=LEFT, padx=5, pady=5)
        
        # Separator
        Frame(self.toolbar, width=2, bg='gray').pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # Knapper til billedhåndtering
        self.rename_button = Button(self.toolbar, text="Batch Omdøb", command=self.batch_rename, bg='#FFC107', fg='black', padx=10)
        self.rename_button.pack(side=LEFT, padx=5, pady=5)
        
        self.move_button = Button(self.toolbar, text="Flyt Billede", command=self.move_image, bg='#FF5722', fg='white', padx=10)
        self.move_button.pack(side=LEFT, padx=5, pady=5)
        
        self.tag_button = Button(self.toolbar, text="Tilføj Tag", command=self.add_tag, bg='#9C27B0', fg='white', padx=10)
        self.tag_button.pack(side=LEFT, padx=5, pady=5)
        
        # Separator
        Frame(self.toolbar, width=2, bg='gray').pack(side=LEFT, fill=Y, padx=5, pady=5)
        
        # Navigationsknapper
        self.prev_button = Button(self.toolbar, text="◀ Forrige", command=self.prev_image, bg='#607D8B', fg='white', padx=10)
        self.prev_button.pack(side=LEFT, padx=5, pady=5)
        
        self.next_button = Button(self.toolbar, text="Næste ▶", command=self.next_image, bg='#607D8B', fg='white', padx=10)
        self.next_button.pack(side=LEFT, padx=5, pady=5)
        
        # Initialiser variabler
        self.images = []
        self.index = 0
        self.current_folder = ""
        self.tags = {}
        
    def open_folder(self):
        # Åbn mappe dialog og indlæs billeder
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.current_folder = folder_selected
            self.load_images(folder_selected)
            if self.images:
                self.show_image(self.index)
    
    def load_images(self, folder):
        # Definer understøttede billedformater
        supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        self.images = []
        # Gennemgå filer i mappen og tilføj understøttede billeder til listen
        for file in os.listdir(folder):
            if file.lower().endswith(supported_formats):
                full_path = os.path.join(folder, file)
                self.images.append(full_path)
        self.sort_images()
        self.index = 0
    
    def show_image(self, index):
        # Vis det valgte billede
        image = Image.open(self.images[index])
        image.thumbnail((800, 600))  # Skaler billedet
        self.photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.photo)
        self.root.title(f"Billedfremviser - {os.path.basename(self.images[index])}")
    
    def next_image(self):
        # Vis næste billede
        if self.images:
            self.index = (self.index + 1) % len(self.images)
            self.show_image(self.index)
    
    def prev_image(self):
        # Vis forrige billede
        if self.images:
            self.index = (self.index - 1) % len(self.images)
            self.show_image(self.index)
    
    def sort_images(self, *args):
        # Sorter billeder baseret på valgt kriterie
        sort_by = self.sort_var.get()
        if sort_by == "Navn":
            self.images.sort()
        elif sort_by == "Dato":
            self.images.sort(key=lambda x: os.path.getmtime(x))
        elif sort_by == "Størrelse":
            self.images.sort(key=lambda x: os.path.getsize(x))
        elif sort_by == "Filtype":
            self.images.sort(key=lambda x: os.path.splitext(x)[1])
        self.index = 0
        if self.images:
            self.show_image(self.index)
    
    def batch_rename(self):
        # Batch omdøbning af billeder
        if not self.images:
            messagebox.showwarning("Advarsel", "Ingen billeder at omdøbe.")
            return
        pattern = simpledialog.askstring("Batch Omdøb", "Indtast navnemønster (brug #nummer for nummerering):")
        if pattern:
            for i, image_path in enumerate(self.images, start=1):
                dir_name = os.path.dirname(image_path)
                ext = os.path.splitext(image_path)[1]
                new_name = pattern.replace("#nummer", str(i)) + ext
                new_path = os.path.join(dir_name, new_name)
                os.rename(image_path, new_path)
            self.load_images(self.current_folder)
            messagebox.showinfo("Succes", "Billeder omdøbt.")
    
    def move_image(self):
        # Flyt det aktuelle billede til en anden mappe
        if not self.images:
            messagebox.showwarning("Advarsel", "Ingen billeder at flytte.")
            return
        destination = filedialog.askdirectory(title="Vælg destinationsmappe")
        if destination:
            current_image = self.images[self.index]
            shutil.move(current_image, destination)
            del self.images[self.index]
            if self.index >= len(self.images):
                self.index = 0
            if self.images:
                self.show_image(self.index)
            else:
                self.image_label.config(image='')
                self.root.title("Billedfremviser")
            messagebox.showinfo("Succes", "Billede flyttet.")
    
    def add_tag(self):
        # Tilføj tag til det aktuelle billede
        if not self.images:
            messagebox.showwarning("Advarsel", "Ingen billeder at tagge.")
            return
        tag = simpledialog.askstring("Tilføj Tag", "Indtast tag:")
        if tag:
            image_path = self.images[self.index]
            # Tilføj tag til vores interne tag-dictionary
            if image_path in self.tags:
                self.tags[image_path].append(tag)
            else:
                self.tags[image_path] = [tag]
            messagebox.showinfo("Succes", f"Tag '{tag}' tilføjet til billede.")
    
    # Funktionen til at gemme tags til filens metadata er kompleks og kræver yderligere biblioteker.
    # Vi holder os til en simpel implementation her.

if __name__ == "__main__":
    root = Tk()
    viewer = ImageViewer(root)
    root.mainloop()
