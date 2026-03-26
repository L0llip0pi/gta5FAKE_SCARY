import tkinter as tk
import ctypes

# Для работы с F11 на Windows
user32 = ctypes.windll.user32

class FullscreenApp:
    def __init__(self):
        self.root = tk.Tk()
        
        # Получаем размеры экрана
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Настройка окна на полный экран
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Убираем курсор мыши
        self.root.config(cursor="none")
        
        # Привязываем клавишу F11 для выхода (на всякий случай)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_app)
        
        # Создаем основной фрейм для центрирования
        frame = tk.Frame(self.root, bg='black')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Главная надпись "Бу!"
        label_main = tk.Label(
            frame, 
            text="Бу!", 
            font=("Arial", 120, "bold"),
            fg="red",
            bg="black"
        )
        label_main.pack()
        
        # Подпись мелким шрифтом
        label_sub = tk.Label(
            frame,
            text="Это просто шутка, тут нет GTA V",
            font=("Arial", 14),
            fg="gray",
            bg="black"
        )
        label_sub.pack(pady=(20, 0))
        
        # Автоматическое закрытие через 3 секунды
        self.root.after(3000, self.exit_app)
        
        self.root.mainloop()
    
    def toggle_fullscreen(self, event=None):
        """Переключение полноэкранного режима (на случай F11)"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
    
    def exit_app(self, event=None):
        """Закрытие приложения"""
        self.root.destroy()

if __name__ == "__main__":
    app = FullscreenApp()
