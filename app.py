import requests
import time
import tkinter as tk
from tkinter import messagebox, ttk

def get_wikipedia_links(title, lang="zh", variant=None):
    if lang.startswith("zh"):
        url = "https://zh.wikipedia.org/w/api.php"
        var_val = variant if variant else "zh-tw"
    else:
        url = f"https://{lang}.wikipedia.org/w/api.php"
        var_val = None

    params = {
        "action": "query",
        "format": "json",
        "list": "backlinks",
        "bltitle": title,
        "blnamespace": 0,
        "bllimit": "max"
    }
    if var_val:
        params["variant"] = var_val

    headers = {
        "User-Agent": "WikiShortestPathBot/1.0 (educational purpose)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        backlinks = []
        
        for item in data.get("query", {}).get("backlinks", []):
            backlinks.append(item["title"])
            
        return backlinks
    except Exception as e:
        print(f"API Error: {e}")
        return []

def build_path(visited_start, visited_target, meeting_node):
    path_start = []
    curr = meeting_node
    while curr is not None:
        path_start.append(curr)
        curr = visited_start[curr]
    path_start.reverse()
    
    path_target = []
    curr = visited_target[meeting_node]
    while curr is not None:
        path_target.append(curr)
        curr = visited_target[curr]
        
    return path_start + path_target

def wiki_shortest_path(start_title, target_title, lang_code, update_callback=None):
    if start_title == target_title:
        return [start_title]
    
    api_lang = "zh" if lang_code.startswith("zh") else lang_code
    variant = lang_code if lang_code.startswith("zh") else None

    visited_start = {start_title: None}
    visited_target = {target_title: None}
    
    queue_start = [start_title]
    queue_target = [target_title]
    
    link_cache = {}
    
    def get_cached_links(title):
        if title not in link_cache:
            if update_callback:
                update_callback(f"Getting link of [{title}] by api.")
            link_cache[title] = get_wikipedia_links(title, lang=api_lang, variant=variant)
            time.sleep(0.3)
        return link_cache[title]

    while queue_start and queue_target:
        if len(queue_start) <= len(queue_target):
            current_queue = queue_start
            current_visited = visited_start
            other_visited = visited_target
            is_start_side = True
        else:
            current_queue = queue_target
            current_visited = visited_target
            other_visited = visited_start
            is_start_side = False
            
        next_level = []
        meeting_node = None
        intersect_found = False
        
        for current in current_queue:
            neighbors = get_cached_links(current)
            for neighbor in neighbors:
                if neighbor in other_visited:
                    current_visited[neighbor] = current
                    meeting_node = neighbor
                    intersect_found = True
                    break
                
                if neighbor not in current_visited:
                    current_visited[neighbor] = current
                    next_level.append(neighbor)
            
            if intersect_found:
                break
                
        if intersect_found:
            return build_path(visited_start, visited_target, meeting_node)
            
        if is_start_side:
            queue_start = next_level
        else:
            queue_target = next_level
            
    return None

COLORS = {
    "bg": "#F5F7F8",
    "card": "#FFFFFF",
    "primary": "#D280E6",
    "accent": "#C850C2",
    "text": "#333333",
    "border": "#DCDCDC"
}

class WikiSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wiki Search")
        self.root.geometry("750x600")
        self.root.configure(bg=COLORS["bg"])
        
        self.default_font = ("Segoe UI", 11)
        self.title_font = ("Segoe UI", 13, "bold")
        
        self._setup_styles()
        self._setup_ui()
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=self.default_font)

    def _setup_ui(self):
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Wiki Search", bg=COLORS["primary"], 
                 fg="white", font=("Segoe UI", 16, "bold"), pady=15).pack()
        
        container = tk.Frame(self.root, bg=COLORS["bg"], padx=20, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        settings_frame = tk.LabelFrame(container, text="Settings", bg=COLORS["bg"], 
                                        font=self.title_font, padx=15, pady=15, fg=COLORS["primary"])
        settings_frame.pack(fill=tk.X, pady=5)

        tk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky="w", pady=5)
        self.lang_combobox = ttk.Combobox(settings_frame, values=["zh-tw", "zh-cn", "en", "jp"], width=10, font=self.default_font, state="readonly")
        self.lang_combobox.set("en")
        self.lang_combobox.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        tk.Label(settings_frame, text="Start:").grid(row=1, column=0, sticky="w", pady=5)
        self.start_entry = tk.Entry(settings_frame, width=20, font=self.default_font)
        self.start_entry.insert(0, "Taiwan")
        self.start_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(settings_frame, text="Target:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.target_entry = tk.Entry(settings_frame, width=20, font=self.default_font)
        self.target_entry.insert(0, "Taipei")
        self.target_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        self.search_btn = tk.Button(settings_frame, text="Start pathfinding", bg=COLORS["primary"], fg="white", 
                                    font=self.title_font, relief="flat", padx=15, pady=5, command=self.start_search)
        self.search_btn.grid(row=0, column=2, columnspan=2, padx=(20, 0), sticky="ew")

        result_frame = tk.LabelFrame(container, text="Log", bg=COLORS["bg"], 
                                      font=self.title_font, padx=15, pady=15, fg=COLORS["primary"])
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_text = tk.Text(result_frame, font=("Segoe UI", 10), wrap=tk.WORD, height=12)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def log(self, message):
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()

    def start_search(self):
        lang = self.lang_combobox.get()
        start_title = self.start_entry.get().strip()
        target_title = self.target_entry.get().strip()

        if not start_title or not target_title:
            messagebox.showwarning("Warning", "Please enter contents.")
            return

        self.result_text.delete("1.0", tk.END)
        self.log(f"Language: {lang} | From {start_title} -> {target_title}\n")

        self.search_btn.config(state=tk.DISABLED)
        
        try:
            path = wiki_shortest_path(start_title, target_title, lang, update_callback=self.log)
            if path:
                self.log("\n Path fonud!")
                self.log(" -> ".join(path))
            else:
                self.log("\n Sorry, I can't find a path.")
        except Exception as e:
            self.log(f"\n Error :( >> {e}")
        finally:
            self.search_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = WikiSearchApp(root)
    root.mainloop()