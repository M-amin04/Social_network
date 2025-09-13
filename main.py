import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui import SocialNetworkApp

if __name__ == '__main__':
    root = ttk.Window(themename='darkly')
    app = SocialNetworkApp(root)
    root.mainloop()