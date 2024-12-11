from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QLabel)
from services.comment_service import CommentService

class CommentLoaderThread(QThread):
    comments_loaded = pyqtSignal(dict,int)
    error_occurred = pyqtSignal(str)

    def __init__(self, comment_service, resource_id, page_no, sort_type, cursor=None):
        super().__init__()
        self.comment_service = comment_service
        self.resource_id = resource_id
        self.page_no = page_no
        self.sort_type = sort_type
        self.cursor = cursor

    def run(self):
        try:
            response = self.comment_service.get_comments(
                id=self.resource_id,
                type=0,
                page_no=self.page_no,
                sort_type=self.sort_type,
                cursor=self.cursor
            )
            self.comments_loaded.emit(response,self.page_no)
        except Exception as e:
            self.error_occurred.emit(str(e))
class CommentWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.comment_service = CommentService()
        self.current_page = 1
        self.last_cursor = None
        self.cursor_history = []
        self.resource_type = 0
        self.resource_id = None
        self.comments_cache={}
        self.init_ui()
        self.loader_thread = None
        self.load_initial_comments()


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

    def load_initial_comments(self):
        self.loader_thread=CommentLoaderThread(
            self.comment_service,
            self.resource_id,
            self.current_page,
            self.sort_combo.currentIndex()+1,
            cursor=None
        )
        self.loader_thread.comments_loaded.connect(self.handle_comments_loaded)
        self.loader_thread.error_occurred.connect(self.handle_load_error)
        self.loader_thread.start()


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
        self.comments_cache={}
        self.load_initial_comments()

    def load_next_page(self):
        self.next_btn.setEnabled(False)
        sort_type=self.sort_combo.currentIndex()+1
        cursor=None
        if sort_type==3 and self.current_page>0:
            if len(self.cursor_history)>=self.current_page:
                cursor=self.cursor_history[self.current_page-1]
            else:
                cursor=self.last_cursor

        self.loader_thread=CommentLoaderThread(
            self.comment_service,
            self.resource_id,
            self.current_page+1,
            sort_type,
            cursor
        )
        self.loader_thread.comments_loaded.connect(self.handle_comments_loaded)
        self.loader_thread.error_occurred.connect(self.handle_load_error)
        self.loader_thread.finished.connect(lambda:self.next_btn.setEnabled(True))
        self.loader_thread.start()

    def load_prev_page(self):
        if self.current_page > 1:
            prev_page=self.current_page-1
            if prev_page in self.comments_cache:
                self.current_page=prev_page
                self.update_comments_table(self.comments_cache[prev_page])
                self.page_label.setText(f'{self.current_page}')
                self.prev_btn.setEnabled(self.current_page>1)
            else:
                self.current_page=prev_page
                self.loader_thread=CommentLoaderThread(
                    self.comment_service,
                    self.resource_id,
                    self.current_page,
                    self.sort_combo.currentIndex()+1,
                    cursor=self.cursor_history[self.current_page-1]if self.sort_combo.currentIndex()+1== 3 else None
                )
                self.loader_thread.comments_loaded.connect(self.handle_comments_loaded)
                self.loader_thread.error_occurred.connect(self.handle_load_error)
                self.loader_thread.start()

    def update_for_song(self,song_id):
        self.resource_id=song_id
        self.resource_type = 0
        self.current_page=1
        self.last_cursor=None
        self.cursor_history=[]
        self.comments_cache={}
        self.load_initial_comments()

    def handle_comments_loaded(self,response,page_no):
        if response.get('code') == 200:
            comments=response.get('data',{}).get('comments',[])
            if comments:
                self.comments_cache[page_no]=comments
                self.update_comments_table(comments)
                sort_type=self.sort_combo.currentIndex()+1
                if sort_type==3:
                    new_cursor=comments[-1].get('time')
                    if page_no>len(self.cursor_history):
                        self.cursor_history.append(new_cursor)
                    else:
                        self.cursor_history[page_no-1]=new_cursor
                    self.last_cursor=new_cursor
                self.current_page=page_no
                self.page_label.setText(f'{self.current_page}')
                self.prev_btn.setEnabled(self.current_page>1)
            else:
                print(f'{page_no}meipinglun')
                if page_no>1:
                    self.current_page-=1
        else:
            print(f"NO!!!: {response.get('message', 'UNKNOW')}")
        self.next_btn.setEnabled(True)


    def handle_load_error(self,error_msg):
        print(f'COMMENT LOAD ERROR: {error_msg}')
        self.next_btn.setEnabled(True)
