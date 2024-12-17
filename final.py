import requests
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QInputDialog,
    QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt
import sys
import random
import datetime

current_captcha = None
main_user = None
def generate_captcha():
    """Генерирует новую капчу."""
    return str(random.randint(1000, 9999))

def hash_password(password):
    """Хеширует пароль с использованием hashlib."""
    return hashlib.sha256(password.encode()).hexdigest()

class BuyTicketDialog(QDialog):
    def __init__(self,parent, movie):
        super().__init__(parent)
        self.movie = movie
        self.movie_booked = requests.get('https://nazimascinema.pythonanywhere.com/get_movie', params={'movie': self.movie['title']}).json()
        self.setWindowTitle(f"Buy Ticket - {self.movie['title']}")
        self.resize(1000, 1000)
        self.setStyleSheet("background-color: rgb(159, 159, 159);")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.seat_grid = QGridLayout()
        self.layout.addLayout(self.seat_grid)

        self.seats_now = []

        rows = 'ABCDEF'
        cols = 9
        for i, row in enumerate(rows):  # 6 rows (from 'a' to 'f')
                for col in range(1, cols + 1):  # 9 columns (1 to 9)
                    seat_id = f'{row}{col}'  # Seat ID format like 'a1', 'b2', 'c3', etc.

                    # Create a button for the seat
                    button = QPushButton(seat_id)

                    # Connect the button click event
                    button.clicked.connect(self.make_button_click_handler(seat_id, button))

                    # Set the button style based on whether the seat is booked or available
                    if seat_id not in self.movie_booked:  # If the seat is not booked
                        button.setStyleSheet("background-color: #90EE90;")  # Style for free seats
                    else:  # If the seat is booked
                        button.setStyleSheet("background-color: #FF4C4C;")  # Style for booked seats
                        button.setEnabled(False)  # Disable the booked button

                    # Add the button to the grid layout (auto placement handled by the layout)
                    self.seat_grid.addWidget(button, i, col - 1)

        self.buy_button = QPushButton("Buy Ticket")
        self.buy_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.buy_button.clicked.connect(self.buy_ticket)
        self.layout.addWidget(self.buy_button)

    def make_button_click_handler(self, seat_id, button):
        def handler():
            self.toggle_seat(seat_id, button)
        return handler

    def toggle_seat(self, seat_id, button):
        if seat_id in self.seats_now:
            self.seats_now.remove(seat_id) 
            button.setStyleSheet("background-color: #90EE90;") 
        else:
            self.seats_now.append(seat_id) 
            button.setStyleSheet("background-color: #FF4C4C;") 

    def buy_ticket(self):
        if self.seats_now:
            purchase_info = f"{main_user} bought {len(self.seats_now)} tickets for {self.movie['title']} ({', '.join(self. seats_now)}) at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            requests.get('https://nazimascinema.pythonanywhere.com/booking_seats', params={'movie': self.movie['title'], 'seats': ','.join(self.seats_now), 'user': main_user, 'price': self.movie['price'], 'history': purchase_info}) 

            QMessageBox.information(self, "Success", f"Ticket(s) bought for {len(self.seats_now)} seat(s) for {self.movie['title']} for {len(self.seats_now)*self.movie['price']} KGZ!")
            self.close()
        else:
            QMessageBox.warning(self, "No Seats", "Please select seats to buy.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FILMBOX - Main")
        self.resize(1000, 1000)
        self.movies = requests.get('https://nazimascinema.pythonanywhere.com/get_movies').json()

        # Таблица фильмов
        self.table = QTableWidget()
        self.table.setRowCount(len(self.movies))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Title", "Price ($)", "Sold", "Income", "Actions", "Remove"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # for row, movie in enumerate(self.movies):
        #     self.table.setItem(row, 0, QTableWidgetItem(movie["title"]))
        #     self.table.setItem(row, 1, QTableWidgetItem(str(movie["price"])))
        #     self.table.setItem(row, 2, QTableWidgetItem(str(movie["sold"])))
        #     self.table.setItem(row, 3, QTableWidgetItem(str(movie["income"])))

        #     buy_button = QPushButton("Buy Ticket")
        #     buy_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        #     buy_button.clicked.connect(lambda _, r=row: self.buy_ticket(r))
        #     self.table.setCellWidget(row, 4, buy_button)

        #     remove_button = QPushButton("Remove")
        #     remove_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        #     remove_button.clicked.connect(lambda _, r=row: self.remove_movie(r))
        #     self.table.setCellWidget(row, 5, remove_button)

        self.add_movie_button = QPushButton("Add Movie")
        self.add_movie_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.add_movie_button.clicked.connect(self.add_movie)

        self.history_button = QPushButton(" Movie History")
        self.history_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.history_button.clicked.connect(self.show_movie_history)

        self.user_history_button = QPushButton(" User History")
        self.user_history_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.user_history_button.clicked.connect(self.show_user_history)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Available Movies"))
        layout.addWidget(self.table)
        layout.addWidget(self.add_movie_button)
        layout.addWidget(self.history_button)
        layout.addWidget(self.user_history_button)

        container = QDialog()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_movie_table()

    def buy_ticket(self, movie_index):
        movie = self.movies[movie_index]
        buy_dialog = BuyTicketDialog(self, movie)  # Replace with actual logged-in user
        buy_dialog.exec_()

    def add_movie(self):
        text, ok = QInputDialog.getText(self, "Add Movie", "Enter movie title:")
        if ok and text:
            requests.get('https://nazimascinema.pythonanywhere.com/add_movie', params={'movie': text, 'price': '600'})
        self.update_movie_table()

    def remove_movie(self, movie):
        requests.get('https://nazimascinema.pythonanywhere.com/remove_movie', params={'movie': movie})
        self.update_movie_table()

    def update_movie_table(self):
        movies = requests.get('https://nazimascinema.pythonanywhere.com/get_movies').json()
        self.table.setRowCount(len(movies))
        for row, movie in enumerate(movies):
            self.table.setItem(row, 0, QTableWidgetItem(movie["title"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(movie["price"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(movie["sold"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(movie["income"])))

            buy_button = QPushButton("Buy Ticket")
            buy_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")
            buy_button.clicked.connect(lambda _, r=row: self.buy_ticket(r))
            self.table.setCellWidget(row, 4, buy_button)

            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")
            remove_button.clicked.connect(lambda _, r=movie['title']: self.remove_movie(r))
            self.table.setCellWidget(row, 5, remove_button)

    def show_movie_history(self):
        history_window = QDialog(self)
        history_layout = QVBoxLayout()
        movies = requests.get('https://nazimascinema.pythonanywhere.com/get_movies').json()
        for movie in movies:
            history_layout.addWidget(QLabel(f"Movie: {movie['title']}"))
            for entry in movie["history"]:
                history_layout.addWidget(QLabel(entry))

        history_window.setLayout(history_layout)
        history_window.setWindowTitle("Movie History")
        history_window.exec_()

    def show_user_history(self):
        user_window = QDialog(self)
        user_layout = QVBoxLayout()
        history = requests.get('https://nazimascinema.pythonanywhere.com/get_history').json()
        for username, history in history.items():
            user_layout.addWidget(QLabel(f"User: {username}"))
            for entry in history:
                user_layout.addWidget(QLabel(entry))

        user_window.setLayout(user_layout)
        user_window.setWindowTitle("User History")
        user_window.exec_()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        global current_captcha
        current_captcha = generate_captcha()
        self.setWindowTitle("Login")
        self.setStyleSheet("background-color: lightgray;")
        self.resize(1000, 1000)

        self.label = QLabel("FILMBOX")
        self.label.setAlignment(Qt.AlignCenter)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.captcha_label = QLabel(f"Captcha: {current_captcha}")
        self.captcha_input = QLineEdit(self)
        self.captcha_input.setPlaceholderText("Enter Captcha")

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.login_button.clicked.connect(self.check_login)

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.register_button.clicked.connect(self.register_user)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.captcha_label)
        layout.addWidget(self.captcha_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

    def check_login(self):
        global current_captcha
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        captcha_input = self.captcha_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password required.")
            return

        if captcha_input != current_captcha:
            QMessageBox.warning(self, "Error", "Invalid Captcha.")
            current_captcha = generate_captcha()
            self.captcha_label.setText(f"Captcha: {current_captcha}")
            return
        response = requests.get('https://nazimascinema.pythonanywhere.com/get_user', params={'user': username}).json()
        if response == True:
            response = requests.get('https://nazimascinema.pythonanywhere.com/login', params={'user': username, 'password': hash_password(password)}).json()
            if response == True:
                global main_user
                main_user = username
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password.")

    def register_user(self):
        reg_dialog = RegisterDialog()
        if reg_dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Success", "Registration complete!")

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        global current_captcha
        current_captcha = generate_captcha()
        self.setWindowTitle("Register")
        self.setStyleSheet("background-color: lightgray;") 
        self.resize(1000, 1000)

        self.label = QLabel("Register Account")
        self.label.setAlignment(Qt.AlignCenter)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.captcha_label = QLabel(f"Captcha: {current_captcha}")
        self.captcha_input = QLineEdit()
        self.captcha_input.setPlaceholderText("Enter Captcha")

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("background-color: rgb(70, 117, 122); color: black;")  # Changed button color
        self.register_button.clicked.connect(self.register_action)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.captcha_label)
        layout.addWidget(self.captcha_input)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

    def register_action(self):
        global current_captcha
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        captcha_input = self.captcha_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        if captcha_input != current_captcha:
            QMessageBox.warning(self, "Error", "Invalid Captcha.")
            current_captcha = generate_captcha()
            self.captcha_label.setText(f"Captcha: {current_captcha}")
            return

        response = requests.get('https://nazimascinema.pythonanywhere.com/get_user', params={'user': username}).json()
        if response == True:
            QMessageBox.warning(self, "Error", "Username already exists.")
            
        else:
            requests.get('https://nazimascinema.pythonanywhere.com/add_user', params={'user': username, 'password': hash_password(password)})
            self.accept()
        
 
if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()

    sys.exit(app.exec_())
