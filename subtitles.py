import pvleopard
import sys
import os
import json
from functools import cmp_to_key

if len(sys.argv) != 2:
    print("Usage: python script.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]
split_result = input_file.rsplit('.', 1)
output_file = split_result[0] + "-Subtitle" + "." + split_result[1]
sub_file = split_result[0] + ".json"

########################################################################################

FONT_SIZE = 66
Y_AXIS = "(h-text_h)/2+120"
THICKNESS = "8"

class Statement:
    def __init__(self, start, end=None, word=None): self.start, self.end, self.word = start, end, word
    def to_dict(self): return {"start": self.start,"end": self.end,"word": self.word}
    def __str__(self): return json.dumps(self.to_dict(), ensure_ascii=False)
    def __repr__(self): return self.__str__()
    def to_json(self): return self.__str__()
    @staticmethod
    def from_dict(data): return Statement(float(data['start']), float(data['end']), data['word'])
    @staticmethod
    def from_json(json_str): return Statement.from_dict(json.loads(json_str))
    
    def getText(self): 
        word = self.word.replace("'", "'\\\\\\\\\\\\''")
        return "drawtext=fontfile=KOMIKAX_.ttf:text='{}':fontcolor=white:fontsize={}:x=(w-text_w)/2:y={}:enable='between(t,{},{})'".format(word, FONT_SIZE, Y_AXIS, self.start, self.end)

########################################################################################

KEY_PATH = ".key.txt"

def saveSub(words):
    with open(sub_file,"w") as f:
        statement_data = [stmt.to_dict() for stmt in words]
        json.dump(statement_data, f, ensure_ascii=False)

def readSub():
    with open(sub_file,"rb") as f:
        statement_data = json.load(f)
        return [Statement.from_dict(data) for data in statement_data]

def generateSub():
    with open(KEY_PATH, 'r') as file: ACCESS_KEY = file.read()
    leopard = pvleopard.create(access_key=ACCESS_KEY)
    _, words = leopard.process_file(input_file)
    
    lineWords = [ Statement(word.start_sec, word.end_sec, word.word.replace('"',"")) for word in words ]
    saveSub(lineWords)

    return lineWords

lineWords = readSub() if os.path.isfile(sub_file) else generateSub()

########################################################################################

import tkinter as tk
from tkinter import *

class WordEditor:
    def __init__(self, root, line_words):
        self.root = root
        self.last_row = []

        self.line_words = sorted(line_words, key=cmp_to_key(self.compare))

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def merge_data(self, index):
        cur = self.line_words.pop(index)
        nex = self.line_words.pop(index)
        new_word = Statement(cur.start, nex.end, (cur.word + " " + nex.word).strip())
        self.line_words.insert(index, new_word)

        self.display()
    
    def adjust_start(self, index):
        prev = self.line_words[index-1]
        cur = self.line_words[index]
        cur.start = prev.end
        self.display()

    def adjust_end(self, index):
        cur = self.line_words[index]
        nex = self.line_words[index+1]
        cur.end = nex.start
        self.display()

    def compare(self, item1, item2):
        if item1.start < item2.start: return -1
        elif item1.start > item2.start: return 1
        else: return 0

    def add_data(self, index, is_last):
        if is_last:

            start = self.last_row[1].get()
            if ':' in start:
                sec, frame = start.split(':')
                start = float(sec) + (float(frame) / 30)
            else: start = float(start)

            end = self.last_row[2].get()
            if ':' in end:
                sec, frame = end.split(':')
                end = float(sec) + (float(frame) / 30)
            else: end = float(end)

            word = Statement(start, end, self.last_row[3].get())
            self.line_words.append(word)
    
            self.line_words = sorted(self.line_words, key=cmp_to_key(self.compare))
            self.display()

        else:
            cur = self.line_words[index]
            nex = self.line_words[index + 1] if index < len(self.line_words)-1 else Statement(0.0,0.0,"")
            self.display(sl=len(lineWords), last=Statement(cur.end,nex.start,""))

    def edit_data(self, index, is_last):
        if is_last:
            word = self.line_words[int(self.last_row[0].get())]

            start = self.last_row[1].get()
            if ':' in start:
                sec, frame = start.split(':')
                word.start = float(sec) + (float(frame) / 30)
            else: word.start = float(start)

            end = self.last_row[2].get()
            if ':' in end:
                sec, frame = end.split(':')
                word.end = float(sec) + (float(frame) / 30)
            else: word.end = float(end)

            word.word = self.last_row[3].get()
            self.display()
        else:
            self.display(sl=index, last=self.line_words[index])

    def draw_row(self, index, sl, word, is_last=False):
        last_none = word is None

        edit_state = 'normal' if is_last else 'readonly'

        sl_text = StringVar(self.frame)
        sl_text.set(sl)
        sl_col = Label(self.frame, width=4, textvariable=sl_text, relief='ridge', anchor="w")
        sl_col.grid(row=index, column=0)

        start_text = StringVar(self.frame)
        start_text.set(word.start)
        start_col = Entry(self.frame, textvariable=start_text, width=20, relief='ridge', state=edit_state)
        start_col.grid(row=index, column=1)

        color = "#f00" if not is_last and index < len(lineWords) - 1 and lineWords[index].end > lineWords[index+1].start else "#fff"
        end_text = StringVar(self.frame)
        end_text.set(word.end)
        end_col = Entry(self.frame, textvariable=end_text, width=20, relief='ridge', state=edit_state, fg=color)
        end_col.grid(row=index, column=2)

        color = "#f00" if word.end - word.start <= 0.1 else "#fff"
        dur_col = Label(self.frame, width=20, text=word.end-word.start, relief='ridge', anchor="w", fg=color)
        dur_col.grid(row=index, column=3)

        word_text = StringVar(self.frame)
        word_text.set(word.word)
        word_col = Entry(self.frame, textvariable=word_text, width=30, relief='ridge', state=edit_state)
        word_col.grid(row=index, column=4)
        
        edit_status = 'disabled' if is_last and last_none else 'active'

        edit_text = 'Update' if is_last else 'Edit'
        edit_col = tk.Button(self.frame, width=4, text=edit_text, relief='ridge', anchor="w",command=lambda k=index: self.edit_data(k, is_last), state=edit_status)
        edit_col.grid(row=index, column=5)

        merge_status = 'disabled' if index >= len(self.line_words) - 1 else 'active'
        merge_col = tk.Button(self.frame, width=8, text='Merge Down', relief='ridge', anchor="w",command=lambda k=index: self.merge_data(k), state=merge_status)
        merge_col.grid(row=index, column=6)

        add_col = tk.Button(self.frame, width=4, text="Add", relief='ridge', anchor="w",command=lambda k=index: self.add_data(k, is_last), state=edit_status)
        add_col.grid(row=index, column=7)

        adjust_start_status = 'disabled' if index >= len(self.line_words) or index == 0 else 'active'
        adjust_start_col = tk.Button(self.frame, width=8, text='Adjust Start', relief='ridge', anchor="w",command=lambda k=index: self.adjust_start(k), state=adjust_start_status)
        adjust_start_col.grid(row=index, column=8)

        adjust_end_status = 'disabled' if index >= len(self.line_words) - 1 else 'active'
        adjust_end_col = tk.Button(self.frame, width=8, text='Adjust End', relief='ridge', anchor="w",command=lambda k=index: self.adjust_end(k), state=adjust_end_status)
        adjust_end_col.grid(row=index, column=9)

        if is_last: self.last_row = [sl_text, start_text, end_text, word_text]

    def display(self, sl=-1, last=None):
        self.frame.destroy()
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.last_row = [None, None, None, None]
        
        for index, word in enumerate(self.line_words):
            self.draw_row(index, index, word)

        if sl >= 0 and last is not None:
            self.draw_row(len(self.line_words), sl, last, is_last=True)

my_w = tk.Tk()
# my_w.attributes('-fullscreen', True)
editor = WordEditor(my_w, lineWords)
editor.display()
my_w.mainloop()

# def __init__(self, start, end=None, word=None): self.start, self.end, self.word = start, end, word
lineWords = editor.line_words
for word in lineWords: word.word = word.word.replace('"',"")

saveSub(lineWords)

########################################################################################

def getDrawText(words): return ",".join([ word.getText() for word in words ])

command = "ffmpeg -i " + input_file + " -vf \"" + getDrawText(lineWords) + "\" -codec:a copy " + output_file

try: return_code = os.system(command)
except Exception as e: print("An error occurred:", e)

########################################################################################
