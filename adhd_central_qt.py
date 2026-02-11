import sys
import json
import threading
import time
from datetime import datetime, date, timedelta
import os

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon, Qt, QCursor, QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QListWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QStackedWidget, QFrame, QInputDialog,
    QMessageBox, QDialog, QLineEdit, QSystemTrayIcon, QMenu
)

from acrylic import enable_acrylic

SAVE_FILE = "data.json"
SPRINT_SECONDS = 5 * 60


def get_resource_path(filename):
    """Get path to resource file, works in both development and packaged app"""
    # In a PyInstaller bundle, sys.frozen is set
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, filename)


def get_week_start(d: date):
    return d - timedelta(days=d.weekday())


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.setFixedSize(400, 180)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("Add New Task")
        title.setStyleSheet("color: #e5e7eb; font-size: 16px; font-weight: 600;")
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter task name...")
        self.input.setStyleSheet("""
            QLineEdit {
                background: rgba(15,23,42,0.55);
                color: #f3f4f6;
                border: 1px solid rgba(59,130,246,0.3);
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        self.input.returnPressed.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_add = QPushButton("Add")
        btn_cancel = QPushButton("Cancel")
        
        for btn in (btn_add, btn_cancel):
            btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
            """)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #e5e7eb;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.15);
            }
        """)
        
        btn_add.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_cancel)
        
        layout.addWidget(title)
        layout.addWidget(self.input)
        layout.addLayout(btn_layout)
    
    def get_text(self):
        return self.input.text().strip()


class CircularTimerWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get dimensions
        w, h = self.width(), self.height()
        center_x, center_y = w / 2, h / 2
        radius = min(w, h) / 2 - 10

        # Draw outer circle (background)
        painter.setPen(QColor(59, 130, 246, 100))
        painter.setBrush(QColor(15, 23, 42, 80))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw progress arc
        if self.app.remaining_seconds > 0:
            progress = self.app.remaining_seconds / SPRINT_SECONDS
            angle_span = int(360 * progress)
            
            painter.setPen(QColor(59, 130, 246, 200))
            painter.setBrush(QColor(59, 130, 246, 40))
            painter.drawPie(
                int(center_x - radius), 
                int(center_y - radius), 
                int(radius * 2), 
                int(radius * 2),
                90 * 16,  # Start from top
                -angle_span * 16  # Clockwise
            )

        # Draw inner circle for text background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(15, 23, 42, 120))
        painter.drawEllipse(center_x - radius * 0.6, center_y - radius * 0.6, radius * 1.2, radius * 1.2)

        # Draw time text
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(59, 130, 246))

        mins, secs = divmod(self.app.remaining_seconds, 60)
        time_text = f"{mins:02d}:{secs:02d}"
        
        text_rect = painter.fontMetrics().boundingRect(time_text)
        text_x = center_x - text_rect.width() / 2
        text_y = center_y + text_rect.height() / 4

        painter.drawText(int(text_x), int(text_y), time_text)

        painter.end()


class SidebarButton(QPushButton):
    def __init__(self, icon_path, text):
        super().__init__()
        self.setIcon(QIcon(get_resource_path(icon_path)))
        self.setText(text)
        self.setIconSize(QSize(22, 22))
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                color: #e5e7eb;
                background: transparent;
                border: none;
                padding: 12px 16px;
                text-align: left;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
            }
            QPushButton:checked {
                background: rgba(255,255,255,0.18);
            }
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))


class DashboardPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # LEFT: Tasks
        left = QVBoxLayout()
        left.setSpacing(10)

        title_tasks = QLabel("Tasks")
        title_tasks.setStyleSheet("color: #e5e7eb; font-size: 18px; font-weight: 600;")

        self.tasks_list = QListWidget()
        self.tasks_list.setStyleSheet("""
            QListWidget {
                background: rgba(15,23,42,0.55);
                border-radius: 10px;
                padding: 6px;
                color: #f3f4f6;
            }
            QListWidget::item:selected {
                background: #3b82f6;
            }
        """)

        btn_add = QPushButton("Add Task")
        btn_remove = QPushButton("Remove Task")
        btn_pick = QPushButton("Pick Random")

        for b in (btn_add, btn_pick):
            b.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
            """)
            b.setCursor(QCursor(Qt.PointingHandCursor))

        btn_remove.setStyleSheet("""
            QPushButton {
                background: #dc2626;
                color: white;
                padding: 8px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #b91c1c;
            }
        """)
        btn_remove.setCursor(QCursor(Qt.PointingHandCursor))

        btn_add.clicked.connect(self.add_task)
        btn_remove.clicked.connect(self.remove_task)
        btn_pick.clicked.connect(self.pick_random)

        left.addWidget(title_tasks)
        left.addWidget(self.tasks_list)
        left.addWidget(btn_add)
        left.addWidget(btn_pick)
        left.addWidget(btn_remove)

        # RIGHT: Sprint + Sleep
        right = QVBoxLayout()
        right.setSpacing(10)

        title_sprint = QLabel("Current Sprint")
        title_sprint.setStyleSheet("color: #e5e7eb; font-size: 18px; font-weight: 600;")

        self.current_task_label = QLabel("No active task")
        self.current_task_label.setStyleSheet("color: #e5e7eb; font-size: 15px;")

        self.timer_widget = CircularTimerWidget(self.app)

        btn_start = QPushButton("Start Sprint")
        btn_stop = QPushButton("Stop")
        btn_clear = QPushButton("Clear Timer")
        btn_clear.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                padding: 8px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #b91c1c;
            }
        """)
        btn_clear.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clear.clicked.connect(self.clear_timer)        

        for b in (btn_start, btn_stop):
            b.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
            """)
            b.setCursor(QCursor(Qt.PointingHandCursor))

        btn_start.clicked.connect(self.start_sprint)
        btn_stop.clicked.connect(self.stop_sprint)

        title_sleep = QLabel("Sleep / Wake Log")
        title_sleep.setStyleSheet("color: #e5e7eb; font-size: 16px; font-weight: 500;")

        self.sleep_log = QTextEdit()
        self.sleep_log.setReadOnly(True)
        self.sleep_log.setStyleSheet("""
            QTextEdit {
                background: rgba(15,23,42,0.55);
                border-radius: 10px;
                padding: 6px;
                color: #f3f4f6;
            }
        """)

        btn_sleep = QPushButton("Log Sleep")
        btn_wake = QPushButton("Log Wake")

        for b in (btn_sleep, btn_wake):
            b.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
            """)
            b.setCursor(QCursor(Qt.PointingHandCursor))

        btn_sleep.clicked.connect(self.log_sleep)
        btn_wake.clicked.connect(self.log_wake)

        right.addWidget(title_sprint)
        right.addWidget(self.current_task_label)
        right.addWidget(self.timer_widget)
        right.addWidget(btn_start)
        right.addWidget(btn_stop)
        right.addWidget(btn_clear)
        right.addSpacing(20)
        right.addWidget(title_sleep)
        right.addWidget(self.sleep_log)
        right.addWidget(btn_sleep)
        right.addWidget(btn_wake)

        layout.addLayout(left, 1)
        layout.addLayout(right, 1)

        self.refresh()

    def clear_timer(self):
        self.app.sprint_running = False
        self.app.remaining_seconds = 0
        self.timer_widget.update()
        
    # Task logic
    def add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            text = dialog.get_text()
            if text:
                self.app.tasks.append(text)
                self.app.save_data()
                self.refresh()

    def remove_task(self):
        row = self.tasks_list.currentRow()
        if row >= 0:
            self.app.tasks.pop(row)
            self.app.save_data()
            self.refresh()

    def pick_random(self):
        if self.app.tasks:
            import random
            self.app.current_task = random.choice(self.app.tasks)
            self.current_task_label.setText(f"Focus on: {self.app.current_task}")

    # Sprint logic
    def start_sprint(self):
        if self.app.sprint_running:
            return
        if not self.app.current_task:
            if self.app.tasks:
                self.app.current_task = self.app.tasks[0]
            else:
                QMessageBox.information(self, "No tasks", "Add a task first.")
                return
        self.current_task_label.setText(f"Focus on: {self.app.current_task}")
        self.app.sprint_running = True
        self.app.remaining_seconds = SPRINT_SECONDS
        threading.Thread(target=self.app.run_timer, daemon=True).start()

    def stop_sprint(self):
        self.app.sprint_running = False

    # Sleep
    def log_sleep(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.app.sleep_log_data.append(f"Sleep at {ts}")
        self.app.save_data()
        self.refresh()

    def log_wake(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.app.sleep_log_data.append(f"Wake at {ts}")
        self.app.save_data()
        self.refresh()

    def refresh(self):
        self.tasks_list.clear()
        for t in self.app.tasks:
            self.tasks_list.addItem(t)

        self.sleep_log.clear()
        for entry in self.app.sleep_log_data:
            self.sleep_log.append(entry)

class WeeklyReviewPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        title = QLabel("Weekly Review")
        title.setStyleSheet("color: #e5e7eb; font-size: 22px; font-weight: 700;")
        main_layout.addWidget(title)

        # Stats section
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("""
            color: #e5e7eb; 
            font-size: 14px;
            line-height: 1.8;
        """)
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: rgba(15,23,42,0.55);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        stats_layout.addWidget(self.stats_label)
        main_layout.addWidget(stats_frame)

        # Review sections in a grid
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(15)

        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        left_column.addWidget(self._make_section_title("Wins"))
        self.wins = self._make_box()
        left_column.addWidget(self.wins)

        left_column.addWidget(self._make_section_title("Top 3 Priorities"))
        self.priorities = self._make_box()
        left_column.addWidget(self.priorities)

        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(15)

        right_column.addWidget(self._make_section_title("Struggles"))
        self.struggles = self._make_box()
        right_column.addWidget(self.struggles)

        right_column.addWidget(self._make_section_title("Areas for Improvement"))
        self.improve = self._make_box()
        right_column.addWidget(self.improve)

        grid_layout.addLayout(left_column, 1)
        grid_layout.addLayout(right_column, 1)

        main_layout.addLayout(grid_layout, 1)

        # Save button
        btn_save = QPushButton("Save Weekly Review")
        btn_save.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            QPushButton:pressed {
                background: #1e40af;
            }
        """)
        btn_save.setCursor(QCursor(Qt.PointingHandCursor))
        btn_save.clicked.connect(self.save_review)
        main_layout.addWidget(btn_save)

        self.refresh()

    def _make_section_title(self, text):
        title = QLabel(text)
        title.setStyleSheet("color: #e5e7eb; font-size: 14px; font-weight: 600;")
        return title

    def _make_box(self):
        box = QTextEdit()
        box.setStyleSheet("""
            QTextEdit {
                background: rgba(15,23,42,0.55);
                border: 1px solid rgba(59,130,246,0.2);
                border-radius: 8px;
                padding: 12px;
                color: #f3f4f6;
                font-size: 13px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 1px solid rgba(59,130,246,0.5);
            }
        """)
        return box

    def refresh(self):
        stats = self.app.compute_current_week_stats()
        ws = stats["week_start"].strftime("%b %d, %Y")
        text = (
            f"<b>Week of:</b> {ws}<br>"
            f"<b>Total Sprints:</b> {stats['total_sprints']} ({stats['total_minutes']} mins)<br>"
            f"<b>Active Days:</b> {stats['days_with_sprints']}/7<br>"
            f"<b>Sleep Logs:</b> {stats['sleep_entries']}"
        )
        self.stats_label.setText(text)

        today = date.today()
        week_start_str = get_week_start(today).strftime("%Y-%m-%d")
        entry = next((w for w in self.app.weekly_reviews if w["week_start"] == week_start_str), None)

        for box in (self.wins, self.struggles, self.improve, self.priorities):
            box.clear()

        if entry:
            self.wins.setPlainText(entry.get("wins", ""))
            self.struggles.setPlainText(entry.get("struggles", ""))
            self.improve.setPlainText(entry.get("improvements", ""))
            self.priorities.setPlainText(entry.get("priorities", ""))

    def save_review(self):
        today = date.today()
        week_start = get_week_start(today).strftime("%Y-%m-%d")

        entry = {
            "week_start": week_start,
            "wins": self.wins.toPlainText(),
            "struggles": self.struggles.toPlainText(),
            "improvements": self.improve.toPlainText(),
            "priorities": self.priorities.toPlainText()
        }

        self.app.weekly_reviews = [
            w for w in self.app.weekly_reviews if w["week_start"] != week_start
        ]
        self.app.weekly_reviews.append(entry)
        self.app.save_data()
        QMessageBox.information(self, "Saved", "Weekly review saved.")
        self.refresh()


class ReviewHistoryPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left: List of reviews
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        title_list = QLabel("Previous Reviews")
        title_list.setStyleSheet("color: #e5e7eb; font-size: 18px; font-weight: 600;")
        left_layout.addWidget(title_list)

        self.reviews_list = QListWidget()
        self.reviews_list.setStyleSheet("""
            QListWidget {
                background: rgba(15,23,42,0.55);
                border-radius: 10px;
                padding: 6px;
                color: #f3f4f6;
            }
            QListWidget::item:selected {
                background: #3b82f6;
            }
        """)
        self.reviews_list.itemSelectionChanged.connect(self.on_review_selected)
        left_layout.addWidget(self.reviews_list)

        # Right: Review details
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        title_detail = QLabel("Review Details")
        title_detail.setStyleSheet("color: #e5e7eb; font-size: 18px; font-weight: 600;")
        right_layout.addWidget(title_detail)

        # Create scrollable review details
        scroll_area = QFrame()
        scroll_area.setStyleSheet("""
            QFrame {
                background: rgba(15,23,42,0.55);
                border-radius: 10px;
            }
        """)
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        scroll_layout.setSpacing(15)

        scroll_layout.addWidget(self._make_detail_title("Wins"))
        self.detail_wins = QTextEdit()
        self.detail_wins.setReadOnly(True)
        self.detail_wins.setStyleSheet(self._get_detail_style())
        self.detail_wins.setMaximumHeight(80)
        scroll_layout.addWidget(self.detail_wins)

        scroll_layout.addWidget(self._make_detail_title("Struggles"))
        self.detail_struggles = QTextEdit()
        self.detail_struggles.setReadOnly(True)
        self.detail_struggles.setStyleSheet(self._get_detail_style())
        self.detail_struggles.setMaximumHeight(80)
        scroll_layout.addWidget(self.detail_struggles)

        scroll_layout.addWidget(self._make_detail_title("Areas for Improvement"))
        self.detail_improve = QTextEdit()
        self.detail_improve.setReadOnly(True)
        self.detail_improve.setStyleSheet(self._get_detail_style())
        self.detail_improve.setMaximumHeight(80)
        scroll_layout.addWidget(self.detail_improve)

        scroll_layout.addWidget(self._make_detail_title("Top 3 Priorities"))
        self.detail_priorities = QTextEdit()
        self.detail_priorities.setReadOnly(True)
        self.detail_priorities.setStyleSheet(self._get_detail_style())
        self.detail_priorities.setMaximumHeight(80)
        scroll_layout.addWidget(self.detail_priorities)

        scroll_layout.addStretch()

        right_layout.addWidget(scroll_area, 1)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        self.refresh()

    def _make_detail_title(self, text):
        title = QLabel(text)
        title.setStyleSheet("color: #e5e7eb; font-size: 13px; font-weight: 600;")
        return title

    def _get_detail_style(self):
        return """
            QTextEdit {
                background: rgba(15,23,42,0.8);
                border: 1px solid rgba(59,130,246,0.2);
                border-radius: 6px;
                padding: 8px;
                color: #f3f4f6;
                font-size: 12px;
            }
        """

    def on_review_selected(self):
        current_row = self.reviews_list.currentRow()
        if current_row >= 0:
            review = self.app.weekly_reviews[current_row]
            self.detail_wins.setPlainText(review.get("wins", ""))
            self.detail_struggles.setPlainText(review.get("struggles", ""))
            self.detail_improve.setPlainText(review.get("improvements", ""))
            self.detail_priorities.setPlainText(review.get("priorities", ""))

    def refresh(self):
        self.reviews_list.clear()
        self.detail_wins.clear()
        self.detail_struggles.clear()
        self.detail_improve.clear()
        self.detail_priorities.clear()

        # Sort reviews by date (newest first)
        sorted_reviews = sorted(self.app.weekly_reviews, key=lambda x: x["week_start"], reverse=True)

        for review in sorted_reviews:
            week_date = review["week_start"]
            date_obj = datetime.strptime(week_date, "%Y-%m-%d").date()
            display_text = f"Week of {date_obj.strftime('%b %d, %Y')}"
            self.reviews_list.addItem(display_text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADHD Central")
        self.setWindowIcon(QIcon(get_resource_path("icon.ico")))
        self.resize(1200, 750)

        # Transparent Qt background so acrylic shows through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")

        # Data
        self.tasks = []
        self.sprint_blocks = []
        self.sleep_log_data = []
        self.weekly_reviews = []
        self.current_task = None
        self.sprint_running = False
        self.remaining_seconds = 0

        self.load_data()

        # Central widget
        central = QWidget()
        central.setAttribute(Qt.WA_TranslucentBackground)
        central.setAutoFillBackground(False)
        central.setStyleSheet("background: transparent;")

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar_layout)
        sidebar_frame.setFixedWidth(210)
        # rgba(128, 130, 134, 0.85)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background: rgba(15,23,42,0.85);
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        """)

        self.btn_dashboard = SidebarButton("icons/home_filled.svg", "Dashboard")
        self.btn_review = SidebarButton("icons/calendar_filled.svg", "Weekly Review")
        self.btn_history = SidebarButton("icons/calendar_filled.svg", "Review History")

        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_review.clicked.connect(lambda: self.switch_page(1))
        self.btn_history.clicked.connect(lambda: self.switch_page(2))

        btn_clear_db = QPushButton("Clear Database")
        btn_clear_db.setStyleSheet("""
            QPushButton {
                color: white;
                background: #dc2626;
                border: none;
                padding: 10px 12px;
                margin: 0px 8px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b91c1c;
            }
            QPushButton:pressed {
                background: #991b1b;
            }
        """)
        btn_clear_db.setCursor(QCursor(Qt.PointingHandCursor))
        btn_clear_db.clicked.connect(self.clear_database)

        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_review)
        sidebar_layout.addWidget(self.btn_history)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_clear_db)
        sidebar_layout.addSpacing(8)

        # Pages
        self.pages = QStackedWidget()
        self.pages.setAttribute(Qt.WA_TranslucentBackground)
        self.pages.setAutoFillBackground(False)
        self.pages.setStyleSheet("background: transparent;")

        self.page_dashboard = DashboardPage(self)
        self.page_review = WeeklyReviewPage(self)
        self.page_history = ReviewHistoryPage(self)

        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_review)
        self.pages.addWidget(self.page_history)

        root_layout.addWidget(sidebar_frame)
        root_layout.addWidget(self.pages)

        self.setCentralWidget(central)

        # Default page
        self.btn_dashboard.setChecked(True)
        self.pages.setCurrentIndex(0)

        # Apply acrylic after window is shown
        QTimer.singleShot(80, self.apply_acrylic)

        # Timer label refresher
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_timer_label)
        self.timer.start(200)

        # System tray icon
        self.setup_tray_icon()

    def setup_tray_icon(self):
        """Create system tray icon with context menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(get_resource_path("icon.ico")))

        # Create context menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show_window)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(self.exit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Double-click to restore window
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def show_window(self):
        """Show the main window"""
        self.showNormal()
        self.activateWindow()

    def exit_app(self):
        """Exit the application"""
        self.close()
        QApplication.quit()

    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead"""
        self.hide()
        event.ignore()

    def paintEvent(self, event):
        pass
    
    def apply_acrylic(self):
        hwnd = self.winId().__int__()
        enable_acrylic(hwnd, 0x80282828)

    def switch_page(self, index):
        self.btn_dashboard.setChecked(index == 0)
        self.btn_review.setChecked(index == 1)
        self.btn_history.setChecked(index == 2)
        self.pages.setCurrentIndex(index)

        # Refresh page content when switching
        if index == 0:
            self.page_dashboard.refresh()
        elif index == 1:
            self.page_review.refresh()
        elif index == 2:
            self.page_history.refresh()
    # Timer logic
    def run_timer(self):
        while self.sprint_running and self.remaining_seconds > 0:
            time.sleep(1)
            self.remaining_seconds -= 1

        if self.sprint_running:
            self.sprint_running = False
            self.sprint_blocks.append(datetime.now().isoformat())
            self.save_data()

    def refresh_timer_label(self):
        self.page_dashboard.timer_widget.update()

    # Weekly stats
    def compute_current_week_stats(self):
        today = date.today()
        week_start = get_week_start(today)
        week_end = week_start + timedelta(days=7)

        sprints_this_week = [
            datetime.fromisoformat(ts)
            for ts in self.sprint_blocks
            if week_start <= datetime.fromisoformat(ts).date() < week_end
        ]

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        sprints_per_day = {d: 0 for d in days}

        for dt in sprints_this_week:
            sprints_per_day[days[dt.weekday()]] += 1

        total_sprints = len(sprints_this_week)
        total_minutes = total_sprints * (SPRINT_SECONDS // 60)
        days_with_sprints = sum(1 for v in sprints_per_day.values() if v > 0)

        sleep_entries = [
            entry for entry in self.sleep_log_data
            if week_start <= datetime.strptime(entry.split(" at ")[1], "%Y-%m-%d %H:%M").date() < week_end
        ]

        return {
            "week_start": week_start,
            "total_sprints": total_sprints,
            "total_minutes": total_minutes,
            "sprints_per_day": sprints_per_day,
            "days_with_sprints": days_with_sprints,
            "sleep_entries": len(sleep_entries),
        }

    # Data persistence
    def save_data(self):
        data = {
            "tasks": self.tasks,
            "sprint_blocks": self.sprint_blocks,
            "sleep_log": self.sleep_log_data,
            "weekly_reviews": self.weekly_reviews
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = data.get("tasks", [])
                self.sprint_blocks = data.get("sprint_blocks", [])
                self.sleep_log_data = data.get("sleep_log", [])
                self.weekly_reviews = data.get("weekly_reviews", [])
        except FileNotFoundError:
            pass

    def clear_database(self):
        reply = QMessageBox.question(
            self,
            "Clear Database",
            "Are you sure you want to clear all data? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.tasks = []
            self.sprint_blocks = []
            self.sleep_log_data = []
            self.weekly_reviews = []
            self.current_task = None
            self.sprint_running = False
            self.remaining_seconds = 0
            self.save_data()
            self.page_dashboard.refresh()
            self.page_dashboard.timer_widget.update()
            QMessageBox.information(self, "Success", "Database cleared.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())        
