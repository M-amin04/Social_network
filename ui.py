import tkinter as tk
import ttkbootstrap as ttk
import datetime
import database as db
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import DatePickerDialog

class SocialNetworkApp:
    def __init__(self, root):
        db.create_tabel()
        self.root = root
        self.style=ttk.Style()
        self.setup_styles()
        self.root.title('Social Network')
        self.root.geometry('900x700')
        self.current_user = None
        self.ensure_admin_exists()
        self.show_main_menu()
        
    
    def setup_styles(self):
        font_style = ('Tahoma', 13)
        self.style.configure('Return.TButton', font=font_style,
                             background="#CE2020", foreground='white')
        self.style.map('Return.TButton', background=[("active", "#a02315")], foreground=[("active", "white")])
        self.style.configure('My.TButton', font=font_style)
        self.style.configure('My.TLabel', font=font_style,
                             background='#222222', foreground='white')
        self.style.configure('My.TFrame', background='#222222')
        self.style.configure('User.TFrame', background='#222222', relief='solid', borderwidth=1)


    def ensure_admin_exists(self):
        if db.get_user('admin') is None:
            admin_data = {
                'Username': 'admin',
                'Password': 'admin',
                'Name': 'Admin',
                'Lastname': 'Main',
                'Birthdate': '2005-01-01',
                'Gender': 'Unknown',
                'City': 'Tehran'
            }
            db.add_user(admin_data)
    
    
    def save_profile(self, entries):
        updated_data = {k: v.get() for k, v in entries.items()}
        db.update_user(self.current_user['username'], updated_data)
        self.current_user.update(updated_data)
        Messagebox.show_info("Success", "Profile updated successfully!")
    
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    
    def show_main_menu(self):
        self.clear_window() 
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text='Social Network', font=('Tahoma', 19, 'bold'), bootstyle='info').pack(pady=(0, 20))
        ttk.Button(frame, text='Register', style='My.TButton', width=25, command=self.show_register).pack(pady=10, padx=5)
        ttk.Button(frame, text='Login', style='My.TButton', width=25, command=self.show_login).pack(pady=10, padx=5)
        ttk.Button(frame, text='Exit', style='Return.TButton', width=25, command=self.root.destroy).pack(pady=10, padx=5)

    def show_register(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text='Register', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=(20, 10))
        
        entries = {}
        fields = ['Name', 'Lastname', 'City', 'Username', 'Password']
        for field in fields:
            ttk.Label(frame, text=field + ':', style='My.TLabel', bootstyle='info').pack(anchor='w', pady=(5, 0), padx=(15, 0))
            entry = ttk.Entry(frame, style='My.TEntry', width=30)
            entry.pack(pady=5)
            entries[field] = entry
            
        ttk.Label(frame, text='Birthdate:', style='My.TLabel', bootstyle='info').pack(anchor='w', pady=(5, 0), padx=(15, 0))
        birthdate_var = tk.StringVar()
        def pick_date():
            picker = DatePickerDialog(firstweekday=6) 
            date = picker.date_selected
            if date:
                birthdate_var.set(date.strftime('%Y-%m-%d'))
        birthdate_frame = ttk.Frame(frame)
        birthdate_frame.pack(anchor='w', pady=5, padx=(30, 0))
        birthdate_entry = ttk.Entry(birthdate_frame, textvariable=birthdate_var, width=27)
        birthdate_entry.pack(side='left', padx=(0, 5))
        ttk.Button(birthdate_frame, text='📅', width=3, command=pick_date).pack(side='left')
        entries['Birthdate'] = birthdate_var
        
        ttk.Label(frame, text='Gender:', style='My.TLabel', bootstyle='info').pack(anchor='w', pady=(10, 0), padx=(15, 0))
        gender_var = ttk.StringVar(value='male')
        gender_frame = ttk.Frame(frame)
        gender_frame.pack(anchor='w', pady=5)
        ttk.Radiobutton(gender_frame, text='Male', variable=gender_var, value='male', bootstyle='info').pack(side='left', padx=(15, 0))
        ttk.Radiobutton(gender_frame, text='Female', variable=gender_var, value='female', bootstyle='info').pack(side='left', padx=(15, 0))
            
        def submit():
            data = {field: entries[field].get() for field in fields}
            data['Birthdate'] = entries['Birthdate'].get()
            data['Gender'] = gender_var.get()
            data['Posts'] = []
            username = data['Username']
            if db.user_exists(username):
                Messagebox.show_error('Error, This Username Is Already Registered')
                return
            db.add_user(data)
            Messagebox.show_info('Successful, Registration Was Successful!')
            self.show_login()
        ttk.Button(frame, style='My.TButton', width=20, text='Registration', command=submit).pack(pady=15)
        ttk.Button(frame, style='Return.TButton', width=20, text='Return', command=self.show_main_menu).pack()


    def show_login(self):
        self.clear_window()  
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text='Login', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=(20, 10))
        ttk.Label(frame, text='Username:', style='My.TLabel', bootstyle='info', width=22).pack(anchor='w', padx=40)
        username_entry = ttk.Entry(frame, style='My.TEntry', width=30)
        username_entry.pack(pady=5)
        ttk.Label(frame, text='Password:', style='My.TLabel', bootstyle='info', width=22).pack()
        password_entry = ttk.Entry(frame, show='*', style='My.TEntry', width=30)
        password_entry.pack(pady=5)
        
        def login():
            username = username_entry.get()
            password = password_entry.get()
            user = db.get_user(username)
            if user and user['password'] == password:
                self.current_user = user
                Messagebox.show_info('Successful Login', f'Welcome {username}!')
                if username == 'admin':
                    self.show_admin_panel()
                else:
                    self.show_user_menu()
            else:
                Messagebox.show_error('Error, Username Or Password Is Incorrect')
        ttk.Button(frame, text='Login', style='My.TButton', width=19, command=login).pack(pady=15)
        ttk.Button(frame, text='Return', style='Return.TButton', width=19, command=self.show_main_menu).pack()


    def show_admin_panel(self):
        self.clear_window()        
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, pady=20)
        ttk.Label(frame, text='Admin Panel', font=('tahoma', 16, 'bold'), bootstyle='info').pack(pady=15)
        options = [
            ('Profile', self.show_profile),
            ('View Users', self.admin_view_users),
            ('View All Message', self.admin_view_messages),
            ('View All Posts', self.admin_view_posts),
            ('Send A Message To The User', self.admin_send_message),
            ('Logout', self.logout),
            ('Exit', self.root.destroy)
        ]
        for (text, command) in options:
            style = 'My.TButton' if text not in ('Exit', 'Logout') else 'Return.TButton'
            ttk.Button(frame, text=text, style=style, bootstyle=style, width=25, command=command).pack(pady=5)
            
            
    def admin_view_users(self):
        self.clear_window()  
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, pady=10, fill='both')
        ttk.Label(frame, text='Registered User', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(frame, padding=10)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, highlightthickness=0, height=400, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0.5, 0), window=scrollable_frame, anchor='n')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        for user, password, first_name, last_name, birthdate, gender, city in db.get_all_users():
            user_frame = ttk.Frame(scrollable_frame, padding=10, style='User.TFrame')
            user_frame.pack(fill='x', pady=8, padx=20)

            line1 = f'Username: {user} | Password: {password} | Firstname: {first_name} | Lastname: {last_name}'
            ttk.Label(user_frame, text=line1, style='My.TLabel').pack(anchor='w', pady=2)

            line2 = f'Birthdate: {birthdate} | Gender: {gender} | City: {city}'
            ttk.Label(user_frame, text=line2, style='My.TLabel').pack(anchor='w', pady=2)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_admin_panel).pack(pady=10)
      
        
    def admin_view_messages(self):
        self.clear_window()   
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        ttk.Label(frame, text='All Messsage', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, highlightthickness=0, height=400, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind('<Configure>',lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        messages = db.get_all_messages()
        if not messages:
            ttk.Label(scroll_frame, text='No Message Found.', style='My.TLabel').pack(pady=10)
        else:
            for sender, receiver, content, date in messages:
                msg_frame = ttk.Frame(scroll_frame, style='My.TFrame', padding=5)
                msg_frame.pack(fill='x', expand=True, padx=10, pady=5)
                ttk.Label(msg_frame, text=f'{sender} → {receiver} | {date}', font=('Tahoma', 9, 'bold'), style='My.TLabel').pack(anchor='w')
                ttk.Label(msg_frame, text=content, wraplength=300, style='My.TLabel', justify='left').pack(anchor='w')

        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_admin_panel).pack(pady=10)


    def admin_view_posts(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        ttk.Label(frame, text='All Posts', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, highlightthickness=0, height=400, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        posts = db.get_all_posts()
        if not posts:
            ttk.Label(scroll_frame, text='No Posts Found.', style='My.TLabel').pack(pady=10)
        else:
            for username, content, date in posts:
                post_frame = ttk.Frame(scroll_frame, style='My.TFrame', padding=5)
                post_frame.pack(fill='x', expand=True, padx=10, pady=5)
                ttk.Label(post_frame, text=f'{username} | {date}', font=('Tahoma', 9, 'bold'), style='My.TLabel').pack(anchor='w')
                ttk.Label(post_frame, text=content, wraplength=300, style='My.TLabel', justify='right').pack(anchor='w')
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_admin_panel).pack(pady=10)


    def admin_send_message(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text='Send A Message To The User', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        usernames = db.get_all_usernames_except('admin')
        if not usernames:
            ttk.Label(frame, text='No User Found.', style='My.TLabel', bootstyle='info').pack()
            ttk.Button(frame, text='Return', style='Return.TButton', bootstyle='info', command=self.show_admin_panel).pack(pady=15)
            return
        
        selected = ttk.StringVar(value=usernames[0])
        ttk.Label(frame, text='User Selection:', style='My.TLabel', bootstyle='info').pack()
        combo = ttk.Combobox(frame, textvariable=selected, values=usernames, width=30)
        combo.pack(pady=10)
        
        ttk.Label(frame, text='Message Text:', style='My.TLabel', bootstyle='info').pack()
        text_box = ttk.Text(frame, height=5, width=40)
        text_box.pack(pady=5)
        
        def send():
            to = selected.get()
            text = text_box.get('1.0', ttk.END).strip()
            if not text:
                Messagebox.show_warning('Error', 'Message Text Cannot Be Empty.')
                return
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            db.send_message('admin', to, text, now)
            Messagebox.show_info('Sent', 'Message Sent.')
            self.show_admin_panel()
        ttk.Button(frame, text='Send', style='My.TButton', width=20, command=send).pack(pady=10)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_admin_panel).pack()


    def logout(self):
        self.current_user = None
        Messagebox.show_info('Logout', 'You Are Out.')
        self.show_login()


    def show_user_menu(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        
        label = ttk.Label(frame, text=f'Menu User', font=('Tahoma', 16, 'bold'), bootstyle='info')
        label.pack(pady=(20, 15))
        
        options = [
            ('Profile', self.show_profile),
            ('Send Friend Requests', self.friend_request),
            ('Reviewing Friend Requests', self.check_friend_requests),
            ('Send Message', self.send_message),
            ('Create A New Post', self.create_post),
            ('View People Posts', self.view_posts),
            ('View Previous Messages', self.view_messages),
            ('View Previous Posts', self.view_own_posts),
            ('Logout', self.logout),
            ('Exit', self.root.destroy)
        ]
        for (text, command) in options:
            style = 'My.TButton' if text not in ('Exit', 'Logout') else 'Return.TButton'
            ttk.Button(frame, style=style, text=text, width=25, command=command).pack(pady=5, padx=10)


    def show_profile(self):
        if self.current_user is None:
            return
        
        self.clear_window()
        
        ttk.Label(self.root, text='Profile', font=("Tahoma", 16, "bold"), bootstyle="info").pack(pady=20)
        frame = ttk.Frame(self.root, style='My.TFrame', padding=10)
        frame.pack(pady=10, padx=20, fill='x')

        entries = {}

        ttk.Label(frame, text="Username:", style='My.TLabel').pack(anchor='w', pady=(5, 0))
        username_var = ttk.StringVar(value=self.current_user['username'])
        ttk.Entry(frame, textvariable=username_var).pack(fill='x', pady=5)
        entries['username'] = username_var

        ttk.Label(frame, text="First Name:", style='My.TLabel').pack(anchor='w', pady=(5, 0))
        name_var = ttk.StringVar(value=self.current_user['first_name'])
        ttk.Entry(frame, textvariable=name_var).pack(fill='x', pady=5)
        entries['first_name'] = name_var

        ttk.Label(frame, text="Last Name:", style='My.TLabel').pack(anchor='w', pady=(5, 0))
        lastname_var = ttk.StringVar(value=self.current_user['last_name'])
        ttk.Entry(frame, textvariable=lastname_var).pack(fill='x', pady=5)
        entries['last_name'] = lastname_var

        ttk.Label(frame, text='Birthdate:', style='My.TLabel').pack(anchor='w', pady=(5, 0))
        birthdate_var = ttk.StringVar(value=self.current_user['birthdate'])
        def pick_date():
            picker = DatePickerDialog(firstweekday=6)
            date = picker.date_selected
            if date:
                birthdate_var.set(date.strftime('%Y-%m-%d'))

        birthdate_frame = ttk.Frame(frame)
        birthdate_frame.pack(anchor='w', pady=5)
        ttk.Entry(birthdate_frame, textvariable=birthdate_var, width=27).pack(side='left', padx=(0, 5))
        ttk.Button(birthdate_frame, text='📅', width=3, command=pick_date).pack(side='left')
        entries['birthdate'] = birthdate_var

        ttk.Label(frame, text='Gender:', style='My.TLabel').pack(anchor='w', pady=(10, 0))
        gender_var = ttk.StringVar(value=self.current_user['gender'])
        gender_frame = ttk.Frame(frame)
        gender_frame.pack(anchor='w', pady=5)
        ttk.Radiobutton(gender_frame, text='Male', variable=gender_var, value='male', bootstyle='info').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(gender_frame, text='Female', variable=gender_var, value='female', bootstyle='info').pack(side='left')
        entries['gender'] = gender_var

        ttk.Label(frame, text="City:", style='My.TLabel').pack(anchor='w', pady=(5, 0))
        city_var = ttk.StringVar(value=self.current_user['city'])
        ttk.Entry(frame, textvariable=city_var).pack(fill='x', pady=5)
        entries['city'] = city_var

        ttk.Button(frame, text="Save", style="My.TButton", width=20, command=lambda: self.save_profile(entries)).pack(pady=10)
        ttk.Button(frame, text="Return", style="Return.TButton", width=20,
                   command=self.show_admin_panel if self.current_user['username'] == 'admin' else self.show_user_menu).pack(padx=10)


    def friend_request(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text='Send Friend Requests', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        current_username = self.current_user['username']
        users = db.get_all_usernames_except(current_username)
        if not users:
            ttk.Label(frame, text='No Users Found', style='My.TLabel', bootstyle='info').pack(pady=10)
            ttk.Button(frame, text='Return', style='Return.TButton', bootstyle='danger', command=self.show_user_menu).pack(pady=10)
            return
        filtered_users = [user for user in users if user != "admin"]
        selected = ttk.StringVar(value=filtered_users[0])
        ttk.Label(frame, text="Choosing a User:", style='My.TLabel', bootstyle='info').pack(pady=10)
        combo = ttk.Combobox(frame, textvariable=selected, values=filtered_users, width=30)
        combo.pack(pady=10)
        
        def send():
            to_user = selected.get()
            self.send_request_to(to_user)
        ttk.Button(frame, text='Send Request', style='My.TButton',width=20, command=send).pack(pady=10)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(padx=10)


    def send_request_to(self, to_user):
        from_user = self.current_user['username']
        success = db.send_friend_request(from_user, to_user)
        if success:
            Messagebox.show_info('Sent', f'The Request Was Sent To {to_user}.')
        else:
            Messagebox.show_warning('Repetitive', f'Request Sent Or You Are A Friend.')
        self.friend_request()
        
            
    def check_friend_requests(self):
        self.clear_window() 
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, pady=20)
        ttk.Label(frame, text='Requests Received', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        username = self.current_user['username']
        requests = db.get_incoming_requests(username)
        if not requests:
            ttk.Label(frame, text='There Are No Requests.', style='My.TLabel', bootstyle='info').pack(pady=10)
        else:
            for sender in requests:
                sub_frame = ttk.Frame(frame)
                sub_frame.pack(expand=True, pady=5, fill='x')
                ttk.Label(sub_frame, text=f'Request From {sender}', style='My.TLabel', bootstyle='info').pack(side=ttk.LEFT, padx=5)
                ttk.Button(sub_frame, text='Accept', style='My.TButton', bootstyle='success',
                           command=lambda u=sender: self.accept_request(u)).pack(side=ttk.LEFT, padx=5)
                ttk.Button(sub_frame, text='Reject', style='Return.TButton', bootstyle='danger',
                           command=lambda u=sender: self.reject_request(u)).pack(side=ttk.LEFT, padx=5)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=10)


    def accept_request(self, from_user):
        to_user = self.current_user['username']
        db.accept_friend_request(from_user, to_user)
        Messagebox.show_info('Acceped', f'The Request From {from_user} Was Accepted')
        self.check_friend_requests()


    def reject_request(self, from_user):
        to_user = self.current_user['username']
        db.reject_friend_request(from_user, to_user)
        Messagebox.show_info('Rejected', f'The Request From {from_user} Was Rejected')
        self.check_friend_requests()


    def view_posts(self):
        self.clear_window()
        ttk.Label(self.root, text='Select a Friend To View Posts', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=(20, 15))
        friends = db.get_friends(self.current_user['username'])
        if not friends:
            ttk.Label(self.root, text='You Have No Friends Yet', style='My.TLabel', bootstyle='info').pack(pady=10)
        else:
            self.selected_friend = ttk.StringVar(value=friends[0])
            combo = ttk.Combobox(self.root, textvariable=self.selected_friend, values=friends)
            combo.pack(pady=10)
            ttk.Button(self.root, text='View Post', style='My.TButton', bootstyle='success', width=20,
                           command=lambda: self.show_friend_posts(self.selected_friend.get())).pack(pady=10)
        ttk.Button(self.root, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=15)
    
    
    def show_friend_posts(self, friend_username):
        self.clear_window()
        ttk.Label(self.root, text=f'Posts By {friend_username}', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(self.root, style='My.TFrame', padding=10)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, height=400, highlightthickness=0, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        posts = db.get_posts_by_users(friend_username)
        if not posts:
            ttk.Label(scroll_frame, text='There Are No Posts To Display.', style='My.TLabel').pack(anchor='center', pady=20)
        else:
            for content, date in posts:
                post_frame = ttk.Frame(scroll_frame, style='My.TFrame', padding=5,)
                post_frame.pack(fill='x', pady=5, padx=20)
                ttk.Label(post_frame, text=f'{date}', font=('Tahoma', 9, 'bold'), style='My.TLabel').pack(anchor='w')
                ttk.Label(post_frame, text=content, wraplength=300, style='My.TLabel', justify='left').pack(anchor='w')
        return_frame = ttk.Frame(self.root)
        return_frame.pack(side='bottom', fill='x', pady=15)
        ttk.Button(return_frame, text='Return', style='Return.TButton', width=20, command=self.view_posts).pack(pady=15)
        
        
    def send_message(self):
        self.clear_window()
        font_style = ('Tahoma', 13)
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill='both')
        
        ttk.Label(frame, text='Send Message', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        from_user = self.current_user['username']
        friends = db.get_friends(from_user)
        if not friends:
            ttk.Label(frame,text='You Have No Friends.', style='My.TLabel', bootstyle='info').pack(pady=10)
            ttk.Button(frame, text='Return', style='Return.TButton', bootstyle='danger-outline', width=20, command=self.show_user_menu).pack(pady=10)
            return
        
        selected = ttk.StringVar(value=friends[0])
        ttk.Label(frame, text='Choosing a Friend:', style='My.TLabel', bootstyle='info').pack(pady=5)
        combo = ttk.Combobox(frame, textvariable=selected, values=friends, width=30)
        combo.pack(pady=5)
        
        ttk.Label(frame, text='Message Text:', style='My.TLabel', bootstyle='info').pack(pady=5)
        message_box = tk.Text(frame, height=5, width=40, font=font_style, wrap='word')
        message_box.pack(pady=10)
        def send():
            to_user = selected.get()
            content = message_box.get('1.0', ttk.END).strip()
            if not content:
                Messagebox.show_warning('Error', 'Message Text Cannot Be Empty.')
                return
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            db.send_message(from_user, to_user, content, now)
            Messagebox.show_info('Sent', f'The Message Was Sent To {to_user}.')
            self.show_user_menu()
        ttk.Button(frame, text='Send', style='My.TButton', width=20, command=send).pack(pady=5)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=10)
        
        
    def create_post(self):
        self.clear_window()
        font_style = ('Tahoma', 13)
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, pady=20)
        
        ttk.Label(frame, text='Create A New Post', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        post_entry = tk.Text(frame, height=6, width=50, font=font_style, wrap='word')
        post_entry.pack(pady=10)

        def save():
            content = post_entry.get('1.0', ttk.END).strip()
            if not content:
                Messagebox.show_warning('Error', 'Post Content Cannot Be Empty.')
                return
            username = self.current_user['username']
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            db.add_post(username, content, now)
            Messagebox.show_info('Registered', 'The Post Was Successfully Submitted.')
            self.show_user_menu()

        ttk.Button(frame, text='Send A Post', style='My.TButton', width=20, command=save).pack(pady=5)
        ttk.Button(frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=10)
        

    def view_messages(self):
        self.clear_window() 
        ttk.Label(self.root, text='Your Messages', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(self.root, style='My.TFrame', padding=10)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, height=400, highlightthickness=0, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style='My.TFrame')
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        friends = db.get_friends(self.current_user['username'])
        messages = db.get_messages_with_friends(self.current_user['username'], friends)
        
        if not messages:
            ttk.Label(scroll_frame, text='There Are No Messages To Display.', style='My.TLabel').pack(anchor='center', pady=20)
        else:
            for msg in messages:
                sender = msg['sender']
                receiver = msg['receiver']
                content = msg['content']
                date = msg['date']
                frame = ttk.Frame(scroll_frame, style='My.TFrame', padding=10)
                frame.pack(pady=5, fill=ttk.X, padx=20)
                ttk.Label(frame, text=f'{sender} → {receiver} | {date}', font=('Tahoma', 9, 'bold'), style='My.TLabel').pack(anchor='w')
                ttk.Label(frame, text=content, wraplength=300, style='My.TLabel', justify='left').pack(anchor='w')
        return_frame = ttk.Frame(self.root)
        return_frame.pack(side='bottom', fill='x', pady=15)
        ttk.Button(return_frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=15)
        
        
    def view_own_posts(self):
        self.clear_window()      
        ttk.Label(self.root, text='Your Posts', font=('Tahoma', 16, 'bold'), bootstyle='info').pack(pady=10)
        
        container = ttk.Frame(self.root, style='My.TFrame', padding=10)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(container, height=400, highlightthickness=0, bg='#222222')
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style='My.TFrame')
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        username = self.current_user['username']
        posts = db.get_posts_by_user(username)
        
        if not posts:
            ttk.Label(scroll_frame, text='You Have Not Posted Anything Yet.', style='My.TLabel').pack(anchor='center', pady=20)
        else:
            for content, date in posts:
                frame = ttk.Frame(scroll_frame, style='My.TFrame', padding=10)
                frame.pack(pady=5, fill='x', padx=20)
                ttk.Label(frame, text=f'Date: {date}', font=('Tahoma', 9, 'bold'), style='My.TLabel').pack(anchor='w')
                ttk.Label(frame, text=content, wraplength=300, style='My.TLabel', justify='left').pack(anchor='w')
        return_frame = ttk.Frame(self.root)
        return_frame.pack(side='bottom', fill='x', pady=15)
        ttk.Button(return_frame, text='Return', style='Return.TButton', width=20, command=self.show_user_menu).pack(pady=15)