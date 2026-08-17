import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import random
import sys
import os
import datetime
import subprocess

DEFAULT_WORDS = [
    ("Accomplish", "Verb", "ทำสำเร็จ / บรรลุเป้าหมาย", "She accomplished all her goals for this year.", "/əˈkʌm.plɪʃ/", "TOEIC"),
    ("Benevolent", "Adjective", "เมตตา / มีใจอารี", "The benevolent donor gifted money to the school.", "/bəˈnev.əl.ənt/", "IELTS"),
    ("Collaborate", "Verb", "ร่วมมือทำงาน", "We need to collaborate to finish the project.", "/kəˈlæb.ə.reɪt/", "TOEIC"),
    ("Diligence", "Noun", "ความขยันหมั่นเพียร", "Success is achieved through constant diligence.", "/ˈdɪl.ɪ.dʒəns/", "IELTS"),
    ("Efficient", "Adjective", "มีประสิทธิภาพ", "Automation makes the work process more efficient.", "/ɪˈfɪʃ.ənt/", "TOEIC"),
    ("Fluctuate", "Verb", "ผันผวน / ขึ้นๆ ลงๆ", "Oil prices fluctuate based on global market demand.", "/ˈflʌk.tʃu.eɪt/", "IELTS"),
    ("Generous", "Adjective", "ใจกว้าง / เอื้อเฟื้อ", "It was generous of him to pay for dinner.", "/ˈdʒen.ər.əs/", "Daily"),
    ("Hazardous", "Adjective", "เป็นอันตราย", "Chemical waste can be extremely hazardous.", "/ˈhæz.ə.dəs/", "TOEIC"),
    ("Innovative", "Adjective", "สร้างสรรค์สิ่งใหม่", "They launched an innovative mobile learning platform.", "/ˈɪn.ə.veɪ.tɪv/", "IT Tech"),
    ("Jargon", "Noun", "ศัพท์เฉพาะกลุ่ม / ศัพท์เทคนิค", "Computer programmers often use technical jargon.", "/ˈdʒɑː.ɡən/", "IT Tech"),
    ("Keen", "Adjective", "กระตือรือร้น / สนใจอย่างยิ่ง", "He is keen to learn new computer programming languages.", "/kiːn/", "Daily"),
    ("Lucrative", "Adjective", "ที่ทำกำไรได้งาม", "Trading stocks can be a lucrative business.", "/ˈluː.krə.tɪv/", "TOEIC"),
    ("Meticulous", "Adjective", "พิถีพิถัน / ละเอียดรอบคอบ", "She took meticulous notes during the lecture.", "/məˈtɪk.jə.ləs/", "IELTS"),
    ("Negotiate", "Verb", "เจรจาต่อรอง", "They negotiated a new business contract.", "/nəˈɡəʊ.ʃi.eɪt/", "TOEIC"),
    ("Optimistic", "Adjective", "มองโลกในแง่ดี", "He remains optimistic about the project outcome.", "/ˌɒp.tɪˈmɪs.tɪk/", "Daily"),
    ("Persistence", "Noun", "ความพยายามอย่างไม่ย่อท้อ", "Persistence is key to overcoming difficulties.", "/pəˈsɪs.təns/", "Daily"),
    ("Quantify", "Verb", "วัดปริมาณ / แสดงเป็นจำนวน", "It is hard to quantify the value of good health.", "/ˈkwɒn.tɪ.faɪ/", "IELTS"),
    ("Resilient", "Adjective", "ยืดหยุ่น / ฟื้นตัวได้เร็ว", "She is resilient and recovers quickly from setbacks.", "/rɪˈzɪl.jənt/", "Daily"),
    ("Synchronize", "Verb", "ปรับเวลา/ข้อมูลให้ตรงกัน", "Data will synchronize automatically across all devices.", "/ˈsɪŋ.krə.naɪz/", "IT Tech"),
    ("Thorough", "Adjective", "ละเอียดถี่ถ้วน", "The police conducted a thorough investigation.", "/ˈθʌr.ə/", "IELTS")
]

class VocabDatabase:
    """Handles SQLite database storage, user performance stats, and quiz history log."""

    def __init__(self, db_name="vocabmaster_full.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Words Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    pos TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    example TEXT,
                    phonetic TEXT,
                    category TEXT,
                    is_learned INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0
                )
            """)

            # User Profile Stats Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 1,
                    quizzes_taken INTEGER DEFAULT 0,
                    total_correct INTEGER DEFAULT 0,
                    total_wrong INTEGER DEFAULT 0
                )
            """)

            # Quiz Score History Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_date TEXT,
                    score INTEGER,
                    total_questions INTEGER,
                    accuracy_percentage REAL
                )
            """)

            # Seed default data if empty
            cursor.execute("SELECT COUNT(*) FROM words")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO words (word, pos, meaning, example, phonetic, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, DEFAULT_WORDS)

            cursor.execute("SELECT COUNT(*) FROM user_profile")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO user_profile (id, xp, streak_days) VALUES (1, 0, 1)")

            conn.commit()

    def fetch_words(self, search="", category="ทั้งหมด"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT id, word, pos, meaning, example, phonetic, category, is_learned, correct_count, wrong_count FROM words WHERE 1=1"
            params = []

            if search:
                sql += " AND (word LIKE ? OR meaning LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])

            if category != "ทั้งหมด":
                sql += " AND category = ?"
                params.append(category)

            sql += " ORDER BY id DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()

    def update_word_stats(self, word_id, is_correct):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if is_correct:
                cursor.execute("UPDATE words SET correct_count = correct_count + 1, is_learned = 1 WHERE id = ?", (word_id,))
            else:
                cursor.execute("UPDATE words SET wrong_count = wrong_count + 1, is_learned = 0 WHERE id = ?", (word_id,))
            conn.commit()

    def add_custom_word(self, word, pos, meaning, example, phonetic, category):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO words (word, pos, meaning, example, phonetic, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (word, pos, meaning, example, phonetic, category))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_word(self, word_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
            conn.commit()

    def get_profile(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT xp, streak_days, quizzes_taken, total_correct, total_wrong FROM user_profile WHERE id = 1")
            return cursor.fetchone()

    def save_quiz_result(self, score, total_q):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            accuracy = round((score / total_q) * 100, 1) if total_q > 0 else 0
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            cursor.execute("""
                INSERT INTO quiz_history (quiz_date, score, total_questions, accuracy_percentage)
                VALUES (?, ?, ?, ?)
            """, (date_str, score, total_q, accuracy))

            # Update Profile XP & Total Stats
            xp_gained = score * 15
            wrong_answers = total_q - score
            cursor.execute("""
                UPDATE user_profile 
                SET xp = xp + ?, 
                    quizzes_taken = quizzes_taken + 1,
                    total_correct = total_correct + ?,
                    total_wrong = total_wrong + ?
                WHERE id = 1
            """, (xp_gained, score, wrong_answers))

            conn.commit()

    def get_quiz_history(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quiz_date, score, total_questions, accuracy_percentage FROM quiz_history ORDER BY id DESC LIMIT 10")
            return cursor.fetchall()

class TextToSpeech:
    """Cross-platform Audio Text-To-Speech system."""
    @staticmethod
    def speak(text):
        try:
            if sys.platform == "darwin": # macOS
                subprocess.Popen(["say", text])
            elif sys.platform == "win32": # Windows PowerShell TTS
                cmd = f'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\');"'
                subprocess.Popen(cmd, shell=True)
            else: # Linux espeak
                subprocess.Popen(["espeak", text])
        except Exception:
            pass

class VocabMasterApp:
    """Primary GUI Application Class."""

    def __init__(self, root):
        self.root = root
        self.root.title("VocabMaster - แอปพลิเคชันฝึกคำศัพท์และการทดสอบ")
        self.root.geometry("480x820")
        self.root.configure(bg="#0F172A")
        self.root.resizable(False, False)

        # Database Engine
        self.db = VocabDatabase()

        # State Variables
        self.words = self.db.fetch_words()
        self.card_index = 0
        self.is_flipped = False

        # Quiz State
        self.quiz_active = False
        self.quiz_score = 0
        self.quiz_total = 10
        self.quiz_current = 0
        self.quiz_timer_sec = 15
        self.timer_job = None
        self.current_quiz_word = None

        # Fonts
        self.setup_styles()

        # Build Navigation
        self.create_header_nav()

        # Container Frame
        self.views = {}

        # Views
        self.build_home_view()
        self.build_flashcard_view()
        self.build_quiz_view()
        self.build_manager_view()
        self.build_stats_view()

        # Start View
        self.show_view("home")

    def setup_styles(self):
        fonts = font.families()
        if "Segoe UI" in fonts:
            self.fn_base = "Segoe UI"
        elif "Helvetica" in fonts:
            self.fn_base = "Helvetica"
        else:
            self.fn_base = "Arial"

        self.f_title = (self.fn_base, 18, "bold")
        self.f_header = (self.fn_base, 13, "bold")
        self.f_bold = (self.fn_base, 10, "bold")
        self.f_normal = (self.fn_base, 9)
        self.f_sub = (self.fn_base, 8)

        # TTk Treeview styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1E293B", foreground="#F8FAFC", fieldbackground="#1E293B", rowheight=26)
        style.configure("Treeview.Heading", background="#334155", foreground="#FFFFFF", font=self.f_bold)
        style.map("Treeview", background=[("selected", "#4F46E5")])

    def create_header_nav(self):
        header = tk.Frame(self.root, bg="#1E293B", height=54)
        header.pack(fill="x", side="top")

        lbl_app = tk.Label(header, text="VocabMaster", font=(self.fn_base, 14, "bold"), fg="#818CF8", bg="#1E293B")
        lbl_app.pack(side="top", pady=(4, 0))

        nav_frame = tk.Frame(header, bg="#1E293B")
        nav_frame.pack(side="top", fill="x", pady=2)

        navs = [
            ("🏠 หน้าหลัก", "home"),
            ("🎴 แฟลชการ์ด", "card"),
            ("📝 ทดสอบ", "quiz"),
            ("📚 คลังศัพท์", "manager"),
            ("📊 สถิติ", "stats")
        ]

        for text, name in navs:
            btn = tk.Button(
                nav_frame, text=text, font=self.f_sub, bg="#334155", fg="white",
                activebackground="#4F46E5", activeforeground="white", bd=0, cursor="hand2",
                command=lambda v=name: self.show_view(v)
            )
            btn.pack(side="left", expand=True, fill="x", padx=1, pady=2)

    def show_view(self, view_name):
        # Cancel any active quiz timer when leaving quiz
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        for v in self.views.values():
            v.pack_forget()

        self.views[view_name].pack(fill="both", expand=True, padx=12, pady=10)

        if view_name == "home":
            self.refresh_home_data()
        elif view_name == "card":
            self.words = self.db.fetch_words()
            self.card_index = 0
            self.render_card()
        elif view_name == "quiz":
            self.reset_and_start_quiz()
        elif view_name == "manager":
            self.refresh_manager_list()
        elif view_name == "stats":
            self.refresh_stats_view()

    def build_home_view(self):
        view = tk.Frame(self.root, bg="#0F172A")
        self.views["home"] = view

        # Banner Card
        self.lbl_welcome = tk.Label(view, text="ยินดีต้อนรับสู่ VocabMaster!", font=self.f_title, fg="#F8FAFC", bg="#0F172A")
        self.lbl_welcome.pack(pady=(10, 2))

        lbl_desc = tk.Label(view, text="ฝึกจำคำศัพท์ภาษาอังกฤษ & ทดสอบสะสมคะแนน", font=self.f_normal, fg="#94A3B8", bg="#0F172A")
        lbl_desc.pack(pady=(0, 10))

        # Status XP Card
        self.card_xp = tk.Frame(view, bg="#1E293B", bd=0)
        self.card_xp.pack(fill="x", pady=6, ipady=10)

        self.lbl_xp_val = tk.Label(self.card_xp, text="🏆 0 XP", font=(self.fn_base, 20, "bold"), fg="#F59E0B", bg="#1E293B")
        self.lbl_xp_val.pack()

        self.lbl_streak_val = tk.Label(self.card_xp, text="🔥 ฝึกต่อเนื่อง 1 วัน", font=self.f_bold, fg="#10B981", bg="#1E293B")
        self.lbl_streak_val.pack(pady=2)

        # Quick Start Actions
        lbl_act = tk.Label(view, text="เริ่มต้นใช้งาน", font=self.f_header, fg="#818CF8", bg="#0F172A")
        lbl_act.pack(anchor="w", pady=(12, 6))

        btn_go_quiz = tk.Button(
            view, text="⚡ เริ่มแบบทดสอบสะสมคะแนน (Quiz)", font=self.f_bold,
            bg="#4F46E5", fg="white", bd=0, cursor="hand2",
            command=lambda: self.show_view("quiz")
        )
        btn_go_quiz.pack(fill="x", pady=5, ipady=12)

        btn_go_cards = tk.Button(
            view, text="🎴 ทบทวนแฟลชการ์ด (Flashcards)", font=self.f_bold,
            bg="#0D9488", fg="white", bd=0, cursor="hand2",
            command=lambda: self.show_view("card")
        )
        btn_go_cards.pack(fill="x", pady=5, ipady=12)

        # Categories Quick Select
        lbl_cat = tk.Label(view, text="หมวดหมู่คำศัพท์", font=self.f_header, fg="#F8FAFC", bg="#0F172A")
        lbl_cat.pack(anchor="w", pady=(12, 6))

        cats = [
            ("💼 TOEIC Vocabulary", "TOEIC", "#0EA5E9"),
            ("🎓 IELTS Essential", "IELTS", "#8B5CF6"),
            ("💻 IT & Technology", "IT Tech", "#10B981"),
            ("☕ Daily Life English", "Daily", "#F59E0B")
        ]

        for text, cat, color in cats:
            b = tk.Button(
                view, text=text, font=self.f_bold, bg=color, fg="white", bd=0, cursor="hand2", anchor="w", padx=15,
                command=lambda c=cat: self.start_category_cards(c)
            )
            b.pack(fill="x", pady=3, ipady=8)

    def refresh_home_data(self):
        xp, streak, quizzes, correct, wrong = self.db.get_profile()
        self.lbl_xp_val.configure(text=f"🏆 {xp} XP")
        self.lbl_streak_val.configure(text=f"🔥 ฝึกต่อเนื่อง {streak} วัน | 📝 สอบแล้ว {quizzes} ครั้ง")

    def start_category_cards(self, cat):
        self.words = self.db.fetch_words(category=cat)
        if not self.words:
            messagebox.showinfo("แจ้งเตือน", f"ยังไม่มีคำศัพท์ในหมวด {cat}")
            return
        self.card_index = 0
        self.show_view("card")

    def build_flashcard_view(self):
        view = tk.Frame(self.root, bg="#0F172A")
        self.views["card"] = view

        self.lbl_card_pos = tk.Label(view, text="การ์ดที่ 1 / 10", font=self.f_bold, fg="#94A3B8", bg="#0F172A")
        self.lbl_card_pos.pack(pady=4)

        # Flip Card Container Box
        self.card_box = tk.Frame(view, bg="#4F46E5", bd=0, cursor="hand2")
        self.card_box.pack(fill="both", expand=True, pady=8)

        self.lbl_card_category = tk.Label(self.card_box, text="TOEIC", font=self.f_bold, fg="#C7D2FE", bg="#4F46E5")
        self.lbl_card_category.pack(pady=(20, 0))

        self.lbl_card_word = tk.Label(self.card_box, text="Word", font=(self.fn_base, 24, "bold"), fg="white", bg="#4F46E5")
        self.lbl_card_word.pack(expand=True)

        # Audio Speak Button
        self.btn_tts = tk.Button(
            self.card_box, text="🔊 ฟังเสียงออกเสียง", font=self.f_sub,
            bg="#3730A3", fg="white", bd=0, cursor="hand2", command=self.speak_word
        )
        self.btn_tts.pack(pady=4, ipadx=10, ipady=4)

        self.lbl_card_sub = tk.Label(self.card_box, text="Phonetic / Meaning", font=(self.fn_base, 11), fg="#E0E7FF", bg="#4F46E5", wraplength=340)
        self.lbl_card_sub.pack(expand=True)

        self.lbl_card_hint = tk.Label(self.card_box, text="👆 แตะการ์ดเพื่อดูคำแปล", font=self.f_sub, fg="#A5B4FC", bg="#4F46E5")
        self.lbl_card_hint.pack(pady=(0, 15))

        # Bind Click to Flip Card
        for w in (self.card_box, self.lbl_card_category, self.lbl_card_word, self.lbl_card_sub, self.lbl_card_hint):
            w.bind("<Button-1>", lambda e: self.toggle_card_flip())

        # Action Buttons
        btn_box = tk.Frame(view, bg="#0F172A")
        btn_box.pack(fill="x", pady=8)

        btn_wrong = tk.Button(
            btn_box, text="❌ ยังจำไม่ได้", font=self.f_bold, bg="#EF4444", fg="white", bd=0, cursor="hand2",
            command=lambda: self.process_card_review(False)
        )
        btn_wrong.pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=8)

        btn_correct = tk.Button(
            btn_box, text="✅ จำได้แล้ว", font=self.f_bold, bg="#10B981", fg="white", bd=0, cursor="hand2",
            command=lambda: self.process_card_review(True)
        )
        btn_correct.pack(side="right", expand=True, fill="x", padx=(4, 0), ipady=8)

    def toggle_card_flip(self):
        self.is_flipped = not self.is_flipped
        self.render_card()

    def speak_word(self):
        if self.words and self.card_index < len(self.words):
            word_text = self.words[self.card_index][1]
            TextToSpeech.speak(word_text)

    def render_card(self):
        if not self.words:
            self.lbl_card_word.configure(text="ไม่มีคำศัพท์")
            self.lbl_card_sub.configure(text="กรุณาเพิ่มคำศัพท์ใหม่ในคลังศัพท์")
            return

        w_id, word, pos, meaning, example, phonetic, category, is_learned, c_cnt, w_cnt = self.words[self.card_index]

        self.lbl_card_pos.configure(text=f"การ์ดที่ {self.card_index + 1} จาก {len(self.words)}")

        if not self.is_flipped:
            self.card_box.configure(bg="#4F46E5")
            self.lbl_card_category.configure(text=f"📌 {pos.upper()} • {category}", bg="#4F46E5", fg="#C7D2FE")
            self.lbl_card_word.configure(text=word, bg="#4F46E5")
            self.lbl_card_sub.configure(text=f"คำอ่าน: {phonetic}", bg="#4F46E5")
            self.lbl_card_hint.configure(text="👆 แตะการ์ดเพื่อดูคำแปล", bg="#4F46E5", fg="#A5B4FC")
            self.btn_tts.configure(bg="#3730A3")
        else:
            self.card_box.configure(bg="#059669")
            self.lbl_card_category.configure(text=f"🇹🇭 คำแปลภาษาไทย", bg="#059669", fg="#A7F3D0")
            self.lbl_card_word.configure(text=meaning, bg="#059669")
            self.lbl_card_sub.configure(text=f"ตัวอย่างประโยค:\n\"{example}\"", bg="#059669")
            self.lbl_card_hint.configure(text="🔄 แตะเพื่อพลิกกลับ", bg="#059669", fg="#A7F3D0")
            self.btn_tts.configure(bg="#047857")

    def process_card_review(self, remembered):
        if not self.words:
            return
        w_id = self.words[self.card_index][0]
        self.db.update_word_stats(w_id, remembered)

        self.card_index = (self.card_index + 1) % len(self.words)
        self.is_flipped = False
        self.render_card()

    def build_quiz_view(self):
        view = tk.Frame(self.root, bg="#0F172A")
        self.views["quiz"] = view

        # Top Bar Timer & Progress
        quiz_top = tk.Frame(view, bg="#1E293B")
        quiz_top.pack(fill="x", pady=(4, 8), ipady=6, padx=2)

        self.lbl_quiz_progress = tk.Label(quiz_top, text="คำถามที่ 1 / 10", font=self.f_bold, fg="#94A3B8", bg="#1E293B")
        self.lbl_quiz_progress.pack(side="left", padx=10)

        self.lbl_quiz_score = tk.Label(quiz_top, text="คะแนน: 0", font=self.f_bold, fg="#10B981", bg="#1E293B")
        self.lbl_quiz_score.pack(side="right", padx=10)

        self.lbl_quiz_timer = tk.Label(view, text="⏱️ เวลาที่เหลือ: 15s", font=self.f_header, fg="#F59E0B", bg="#0F172A")
        self.lbl_quiz_timer.pack(pady=4)

        # Question Display Box
        q_box = tk.Frame(view, bg="#1E293B", bd=0)
        q_box.pack(fill="x", pady=8, ipady=12)

        lbl_q_type = tk.Label(q_box, text="คำศัพท์นี้มีความหมายตรงกับข้อใด?", font=self.f_normal, fg="#94A3B8", bg="#1E293B")
        lbl_q_type.pack()

        self.lbl_quiz_word = tk.Label(q_box, text="WORD", font=(self.fn_base, 22, "bold"), fg="white", bg="#1E293B")
        self.lbl_quiz_word.pack(pady=6)

        # Option Choice Buttons (4 Choices)
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                view, text="", font=self.f_bold, bg="#334155", fg="white",
                bd=0, cursor="hand2", anchor="w", padx=15,
                command=lambda idx=i: self.submit_quiz_answer(idx)
            )
            btn.pack(fill="x", pady=4, ipady=10)
            self.option_buttons.append(btn)

        # Quick Next / Restart Button
        self.btn_quiz_next = tk.Button(
            view, text="ข้อถัดไป ➔", font=self.f_bold, bg="#4F46E5", fg="white",
            bd=0, cursor="hand2", command=self.next_quiz_question
        )
        self.btn_quiz_next.pack(fill="x", pady=(12, 0), ipady=8)

    def reset_and_start_quiz(self):
        all_words = self.db.fetch_words()
        if len(all_words) < 4:
            messagebox.showwarning("คำศัพท์ไม่พอ", "ต้องมีคำศัพท์อย่างน้อย 4 คำในคลังเพื่อเริ่มการทดสอบ")
            self.show_view("home")
            return

        self.quiz_active = True
        self.quiz_score = 0
        self.quiz_current = 0
        self.quiz_total = 10
        self.quiz_pool = random.sample(all_words, min(len(all_words), self.quiz_total))
        self.quiz_total = len(self.quiz_pool)

        self.next_quiz_question()

    def next_quiz_question(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        if self.quiz_current >= self.quiz_total:
            self.finish_quiz_session()
            return

        self.current_quiz_word = self.quiz_pool[self.quiz_current]
        self.quiz_current += 1

        self.lbl_quiz_progress.configure(text=f"คำถามที่ {self.quiz_current} / {self.quiz_total}")
        self.lbl_quiz_score.configure(text=f"คะแนน: {self.quiz_score}")
        self.lbl_quiz_word.configure(text=self.current_quiz_word[1])

        # Prepare 4 Options
        correct_meaning = self.current_quiz_word[3]
        all_words = self.db.fetch_words()
        other_meanings = [w[3] for w in all_words if w[3] != correct_meaning]

        distractors = random.sample(other_meanings, min(3, len(other_meanings)))
        choices = distractors + [correct_meaning]
        random.shuffle(choices)

        for i, btn in enumerate(self.option_buttons):
            btn.configure(text=f"{chr(65+i)}.  {choices[i]}", bg="#334155", state="normal")

        # Start 15s Timer
        self.quiz_timer_sec = 15
        self.update_timer_loop()

    def update_timer_loop(self):
        self.lbl_quiz_timer.configure(text=f"⏱️ เวลาที่เหลือ: {self.quiz_timer_sec}s")
        if self.quiz_timer_sec > 0:
            self.quiz_timer_sec -= 1
            self.timer_job = self.root.after(1000, self.update_timer_loop)
        else:
            messagebox.showwarning("หมดเวลา!", "⏰ หมดเวลาสำหรับข้อนี้!")
            self.db.update_word_stats(self.current_quiz_word[0], False)
            self.next_quiz_question()

    def submit_quiz_answer(self, btn_index):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        selected_text = self.option_buttons[btn_index].cget("text")
        chosen_meaning = selected_text.split(".  ")[-1]
        correct_meaning = self.current_quiz_word[3]

        w_id = self.current_quiz_word[0]

        if chosen_meaning == correct_meaning:
            self.quiz_score += 1
            self.db.update_word_stats(w_id, True)
            self.option_buttons[btn_index].configure(bg="#10B981")
        else:
            self.db.update_word_stats(w_id, False)
            self.option_buttons[btn_index].configure(bg="#EF4444")

        # Auto trigger next after brief pause
        self.root.after(600, self.next_quiz_question)

    def finish_quiz_session(self):
        self.quiz_active = False
        self.db.save_quiz_result(self.quiz_score, self.quiz_total)

        accuracy = int((self.quiz_score / self.quiz_total) * 100) if self.quiz_total > 0 else 0
        xp_earned = self.quiz_score * 15

        msg = f"🎉 การทดสอบเสร็จสิ้น!\n\nคะแนนที่คุณได้: {self.quiz_score} / {self.quiz_total}\nความแม่นยำ: {accuracy}%\nได้รับ +{xp_earned} XP!"
        messagebox.showinfo("สรุปผลการทดสอบ", msg)
        self.show_view("stats")

    def build_manager_view(self):
        view = tk.Frame(self.root, bg="#0F172A")
        self.views["manager"] = view

        lbl_head = tk.Label(view, text="📚 คลังคำศัพท์และจัดการข้อมูล", font=self.f_header, fg="#818CF8", bg="#0F172A")
        lbl_head.pack(pady=(4, 6))

        # Search & Filter Bar
        sf_frame = tk.Frame(view, bg="#0F172A")
        sf_frame.pack(fill="x", pady=4)

        self.ent_search = tk.Entry(sf_frame, font=self.f_normal, bg="#1E293B", fg="white", insertbackground="white", bd=1)
        self.ent_search.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 4))
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh_manager_list())

        btn_search = tk.Button(sf_frame, text="🔍 ค้นหา", font=self.f_bold, bg="#4F46E5", fg="white", bd=0, command=self.refresh_manager_list)
        btn_search.pack(side="right", ipady=3, ipadx=8)

        # Treeview Table
        tree_frame = tk.Frame(view, bg="#1E293B")
        tree_frame.pack(fill="both", expand=True, pady=6)

        self.tree = ttk.Treeview(tree_frame, columns=("Word", "POS", "Meaning", "Category"), show="headings", height=12)
        self.tree.heading("Word", text="คำศัพท์")
        self.tree.heading("POS", text="ประเภท")
        self.tree.heading("Meaning", text="คำแปล")
        self.tree.heading("Category", text="หมวดหมู่")

        self.tree.column("Word", width=110)
        self.tree.column("POS", width=65)
        self.tree.column("Meaning", width=160)
        self.tree.column("Category", width=80)
        self.tree.pack(fill="both", expand=True)

        # Action Buttons Box
        act_box = tk.Frame(view, bg="#0F172A")
        act_box.pack(fill="x", pady=6)

        btn_add = tk.Button(act_box, text="➕ เพิ่มคำศัพท์ใหม่", font=self.f_bold, bg="#10B981", fg="white", bd=0, command=self.open_add_word_dialog)
        btn_add.pack(side="left", ipady=6, ipadx=10)

        btn_del = tk.Button(act_box, text="🗑️ ลบคำศัพท์", font=self.f_bold, bg="#EF4444", fg="white", bd=0, command=self.delete_selected_word)
        btn_del.pack(side="right", ipady=6, ipadx=10)

    def refresh_manager_list(self):
        query = self.ent_search.get().strip()
        words = self.db.fetch_words(search=query)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for w in words:
            w_id, word, pos, meaning, example, phonetic, category, is_learned, c_cnt, w_cnt = w
            self.tree.insert("", "end", iid=str(w_id), values=(word, pos, meaning, category))

    def delete_selected_word(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกคำศัพท์ที่ต้องการลบ")
            return
        w_id = int(sel[0])
        self.db.delete_word(w_id)
        self.refresh_manager_list()
        messagebox.showinfo("สำเร็จ", "ลบคำศัพท์เรียบร้อยแล้ว")

    def open_add_word_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("เพิ่มคำศัพท์ใหม่")
        win.geometry("340x440")
        win.configure(bg="#1E293B")
        win.grab_set()

        fields = [
            ("คำศัพท์ (English):", "word"),
            ("ประเภท (POS e.g. Verb, Noun):", "pos"),
            ("คำแปลภาษาไทย:", "meaning"),
            ("ตัวอย่างประโยค:", "example"),
            ("คำอ่าน (Phonetic):", "phonetic"),
            ("หมวดหมู่ (Category):", "category")
        ]

        entries = {}
        for lbl_text, key in fields:
            lbl = tk.Label(win, text=lbl_text, font=self.f_sub, fg="#94A3B8", bg="#1E293B", anchor="w")
            lbl.pack(fill="x", padx=15, pady=(4, 1))
            ent = tk.Entry(win, font=self.f_normal, bg="#0F172A", fg="white", insertbackground="white", bd=1)
            ent.pack(fill="x", padx=15, pady=(0, 2))
            entries[key] = ent

        def save():
            w = entries["word"].get().strip()
            p = entries["pos"].get().strip() or "Noun"
            m = entries["meaning"].get().strip()
            ex = entries["example"].get().strip() or "No example available."
            ph = entries["phonetic"].get().strip() or f"/{w.lower()}/"
            cat = entries["category"].get().strip() or "General"

            if not w or not m:
                messagebox.showwarning("คำเตือน", "กรุณากรอกคำศัพท์และคำแปลภาษาไทย")
                return

            if self.db.add_custom_word(w, p, m, ex, ph, cat):
                messagebox.showinfo("สำเร็จ", f"เพิ่มคำศัพท์ \"{w}\" เรียบร้อย!")
                win.destroy()
                self.refresh_manager_list()
            else:
                messagebox.showerror("ผิดพลาด", "คำศัพท์นี้มีอยู่ในระบบอยู่แล้ว")

        btn_save = tk.Button(win, text="💾 บันทึกคำศัพท์", font=self.f_bold, bg="#10B981", fg="white", bd=0, command=save)
        btn_save.pack(fill="x", padx=15, pady=15, ipady=6)

    def build_stats_view(self):
        view = tk.Frame(self.root, bg="#0F172A")
        self.views["stats"] = view

        lbl_head = tk.Label(view, text="📊 สถิติคะแนนและประวัติการสอบ", font=self.f_header, fg="#818CF8", bg="#0F172A")
        lbl_head.pack(pady=(4, 8))

        # Overall Profile Summary
        summary_box = tk.Frame(view, bg="#1E293B")
        summary_box.pack(fill="x", pady=4, ipady=8)

        self.lbl_stat_xp = tk.Label(summary_box, text="XP สะสม: 0", font=self.f_header, fg="#F59E0B", bg="#1E293B")
        self.lbl_stat_xp.pack(pady=2)

        self.lbl_stat_accuracy = tk.Label(summary_box, text="ความแม่นยำรวม: 0%", font=self.f_bold, fg="#10B981", bg="#1E293B")
        self.lbl_stat_accuracy.pack(pady=2)

        # Recent Quiz History Table
        lbl_hist = tk.Label(view, text="ประวัติการทดสอบ 10 ครั้งล่าสุด", font=self.f_bold, fg="#F8FAFC", bg="#0F172A")
        lbl_hist.pack(anchor="w", pady=(10, 4))

        hist_frame = tk.Frame(view, bg="#1E293B")
        hist_frame.pack(fill="both", expand=True, pady=4)

        self.tree_hist = ttk.Treeview(hist_frame, columns=("Date", "Score", "Accuracy"), show="headings", height=8)
        self.tree_hist.heading("Date", text="วันที่ / เวลา")
        self.tree_hist.heading("Score", text="คะแนน")
        self.tree_hist.heading("Accuracy", text="ความแม่นยำ")

        self.tree_hist.column("Date", width=180)
        self.tree_hist.column("Score", width=100)
        self.tree_hist.column("Accuracy", width=100)
        self.tree_hist.pack(fill="both", expand=True)

    def refresh_stats_view(self):
        xp, streak, quizzes, correct, wrong = self.db.get_profile()
        total_ans = correct + wrong
        acc = round((correct / total_ans) * 100, 1) if total_ans > 0 else 0.0

        self.lbl_stat_xp.configure(text=f"🏆 XP สะสมทั้งหมด: {xp} XP")
        self.lbl_stat_accuracy.configure(text=f"🎯 ความแม่นยำรวม: {acc}% (ตอบถูก {correct} / {total_ans} ข้อ)")

        # Render History Table
        for item in self.tree_hist.get_children():
            self.tree_hist.delete(item)

        history = self.db.get_quiz_history()
        for h in history:
            q_date, score, total_q, acc_pct = h
            self.tree_hist.insert("", "end", values=(q_date, f"{score} / {total_q}", f"{acc_pct}%"))

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VocabMasterApp(root)
        root.mainloop()
    except Exception as err:
        print(f"Error starting VocabMaster Desktop App: {err}", file=sys.stderr)