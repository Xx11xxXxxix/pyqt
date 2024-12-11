from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QLabel)
from services.comment_service import CommentService


class CommentWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.comment_service = CommentService()
        self.current_page = 1
        self.last_cursor = None
        self.cursor_history = []
        self.resource_type = 0
        self.resource_id = None
        self.init_ui()

    def init_ui(self):
        layout=QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        controls_layout = QHBoxLayout()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['系统排的吧', '谁的赞多', '谁写的早'])
        self.sort_combo.setCurrentIndex(2)

        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)


        self.prev_btn = QPushButton('PREV')
        self.page_label = QLabel('1')
        self.next_btn = QPushButton('NEXT')

        self.next_btn.clicked.connect(self.load_next_page)
        self.prev_btn.clicked.connect(self.load_prev_page)

        controls_layout.addWidget(self.sort_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.page_label)
        controls_layout.addWidget(self.next_btn)

        self.comment_table = QTableWidget()
        self.comment_table.setColumnCount(4)
        self.comment_table.setHorizontalHeaderLabels(['谁写的', '写的啥', '几点', '点赞的'])

        layout.addLayout(controls_layout)
        layout.addWidget(self.comment_table)


    def load_comments(self):

        try:
            sort_type = self.sort_combo.currentIndex() + 1
            if sort_type==3 and self.current_page > 1:
                cursor=self.cursor_history[self.current_page-2]
            else:
                cursor=None

            response = self.comment_service.get_comments(
                id=self.resource_id,
                type=self.resource_type,
                page_no=self.current_page,
                sort_type=sort_type,
                cursor=self.last_cursor
            )

            if response.get('code') == 200:
                comments = response.get('data', {}).get('comments', [])
                self.update_comments_table(comments)

                if comments and sort_type == 3:
                    new_cursor=comments[-1].get('time')
                    if self.current_page>len(self.cursor_history):
                        self.cursor_history.append(new_cursor)
                    else:
                        self.cursor_history[self.current_page-1]=new_cursor
                    self.last_cursor = comments[-1].get('time')

            self.page_label.setText(f'第{self.current_page}页')
            self.prev_btn.setEnabled(self.current_page > 1)

        except Exception as e:
            print(f"WRONG_COMMENT: {e}")

    def update_comments_table(self, comments):
        self.comment_table.setRowCount(len(comments))
        for row, comment in enumerate(comments):
            user = comment.get('user', {})
            username = user.get('nickname', 'Unknown')
            self.comment_table.setItem(row, 0, QTableWidgetItem(username))

            content = comment.get('content', '')
            self.comment_table.setItem(row, 1, QTableWidgetItem(content))

            time = comment.get('timeStr', '')
            self.comment_table.setItem(row, 2, QTableWidgetItem(time))

            liked_count = str(comment.get('likedCount', 0))
            self.comment_table.setItem(row, 3, QTableWidgetItem(liked_count))

        self.comment_table.resizeColumnsToContents()

    def on_sort_changed(self):
        self.current_page = 1
        self.last_cursor = None
        self.cursor_history = []
        self.load_comments()

    def load_next_page(self):
        self.current_page += 1
        self.load_comments()

    def load_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_comments()

    def update_for_song(self,song_id):
        self.resource_id=song_id
        self.resource_type = 0
        self.current_page=1
        self.last_cursor=None
        self.cursor_history=[]
        self.load_comments()