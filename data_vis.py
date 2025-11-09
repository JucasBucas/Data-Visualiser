import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import seaborn as sns
from datetime import datetime
import traceback
from matplotlib.widgets import Cursor

plt.style.use('default')
sns.set_theme(style="whitegrid")

class DataVisualizer:
    def __init__(self, root):
        self.root = root
        self.data = None
        self.fig = None
        self.canvas = None
        self.toolbar = None
        self.is_fullscreen = False
        self.original_geometry = None
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title(" Data Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f7fa")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background="#f5f7fa")
        style.configure('TLabel', background="#f5f7fa", foreground="#2c3e50", font=("Segoe UI", 10))
        style.configure('Title.TLabel', background="#f5f7fa", foreground="#3498db", font=("Segoe UI", 18, "bold"))
        style.configure('TButton', font=("Segoe UI", 10))
        style.configure('Action.TButton', font=("Segoe UI", 10, "bold"))
        style.configure('Header.TButton', font=("Segoe UI", 12, "bold"))
        style.configure('TLabelframe', background="#ffffff", foreground="#2c3e50")
        style.configure('TLabelframe.Label', background="#ffffff", foreground="#2c3e50", font=("Segoe UI", 10, "bold"))
        style.configure('TCombobox', fieldbackground="#ffffff")
        
        style.map('TButton',
                  background=[('active', '#e1e8f0')],
                  foreground=[('active', '#2c3e50')])
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(title_frame, text="📊 Advanced Data Visualizer", style="Title.TLabel")
        title.pack(side=tk.LEFT)
        
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=5)
        
        left_panel = ttk.Frame(paned_window)
        paned_window.add(left_panel, weight=1)
        
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=2)
        
        file_frame = ttk.LabelFrame(left_panel, text=" Data Input ", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        load_btn = ttk.Button(file_frame, text="📁 Load Data File", command=self.load_file, style="Header.TButton")
        load_btn.pack(pady=5)
        
        preview_frame = ttk.LabelFrame(left_panel, text=" Data Preview ", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_container, 
            height=8, 
            width=80,
            bg="#ffffff",
            fg="#2c3e50",
            insertbackground="#3498db",
            selectbackground="#3498db",
            selectforeground="white",
            font=("Consolas", 9)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        viz_frame = ttk.LabelFrame(left_panel, text=" Visualization Settings ", padding="10")
        viz_frame.pack(fill=tk.X, pady=5)
        
        type_frame = ttk.Frame(viz_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Chart Type:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.chart_type_var = tk.StringVar(value="Bar")
        chart_types = ["Bar", "Line", "Pie", "Scatter", "Histogram", "Boxplot", "Heatmap"]
        chart_combo = ttk.Combobox(type_frame, textvariable=self.chart_type_var, 
                                  values=chart_types, state="readonly", width=15)
        chart_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        chart_combo.bind('<<ComboboxSelected>>', self.on_chart_type_change)
        
        col_frame = ttk.Frame(viz_frame)
        col_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(col_frame, text="X Column:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.column_choices = ttk.Combobox(col_frame, values=[], state="readonly", width=20)
        self.column_choices.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(col_frame, text="Y Column:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.column_choices2 = ttk.Combobox(col_frame, values=[], state="readonly", width=20)
        self.column_choices2.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        self.options_frame = ttk.Frame(viz_frame)
        self.options_frame.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(viz_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        plot_btn = ttk.Button(btn_frame, text="📈 Generate Chart", command=self.plot_chart, style="Header.TButton")
        plot_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(btn_frame, text="💾 Save Chart", command=self.save_chart, style="Action.TButton")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="🗑️ Clear Chart", command=self.clear_chart, style="Action.TButton")
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        chart_frame = ttk.LabelFrame(right_panel, text=" Chart Display ", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        chart_container_frame = ttk.Frame(chart_frame)
        chart_container_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar = ttk.Scrollbar(chart_container_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(chart_container_frame, orient=tk.HORIZONTAL)
        
        self.chart_canvas = tk.Canvas(
            chart_container_frame, 
            bg='white',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.chart_canvas.yview)
        h_scrollbar.config(command=self.chart_canvas.xview)
        
        self.scrollable_frame = ttk.Frame(self.chart_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))
        )
        
        self.chart_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        chart_container_frame.grid_rowconfigure(0, weight=1)
        chart_container_frame.grid_columnconfigure(0, weight=1)
        
        nav_frame = ttk.Frame(chart_frame)
        nav_frame.pack(fill=tk.X, pady=(5, 0))
        
        zoom_in_btn = ttk.Button(nav_frame, text="🔍 Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        zoom_out_btn = ttk.Button(nav_frame, text="🔍 Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        pan_btn = ttk.Button(nav_frame, text="✋ Pan", command=self.toggle_pan)
        pan_btn.pack(side=tk.LEFT, padx=2)
        
        reset_btn = ttk.Button(nav_frame, text="🔄 Reset View", command=self.reset_view)
        reset_btn.pack(side=tk.LEFT, padx=2)
        
        fullscreen_btn = ttk.Button(nav_frame, text="⛶ Fullscreen", command=self.toggle_fullscreen)
        fullscreen_btn.pack(side=tk.LEFT, padx=2)
        
        status_frame = ttk.Frame(main_frame, height=25)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready to load data")
        status_bar = ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN,
            background="#e1e8f0",
            foreground="#2c3e50",
            font=("Segoe UI", 9)
        )
        status_bar.pack(fill=tk.BOTH)
        
        self.pan_enabled = False
        
        self.chart_canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.chart_canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.chart_canvas.bind("<Button-5>", self._on_mouse_wheel)
        
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen() if self.is_fullscreen else None)
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling for both vertical and horizontal scrolling"""
        if event.state & 0x1:
            self.chart_canvas.xview_scroll(-1 * int(event.delta/120), "units")
        else:   
            self.chart_canvas.yview_scroll(-1 * int(event.delta/120), "units")
    
    def zoom_in(self):
        """Zoom in on the chart"""
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.zoom()
            self.status_var.set("Zoom mode activated - select area to zoom in")
    
    def zoom_out(self):
        """Zoom out on the chart"""
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.home() 
            self.status_var.set("Zoomed out")
    
    def toggle_pan(self):
        """Toggle pan/zoom mode"""
        if hasattr(self, 'toolbar') and self.toolbar:
            if self.pan_enabled:
                self.toolbar.pan()
                self.pan_enabled = False
                self.status_var.set("Pan mode deactivated")
            else:
                self.toolbar.pan()
                self.pan_enabled = True
                self.status_var.set("Pan mode activated - click and drag to pan")
    
    def reset_view(self):
        """Reset the chart view to original"""
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.home()
            self.status_var.set("View reset to original")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if not self.is_fullscreen:
            self.original_geometry = self.root.geometry()
            self.root.attributes('-fullscreen', True)
            self.is_fullscreen = True
            self.status_var.set("Fullscreen mode - press ESC to exit")
        else:
            self.exit_fullscreen()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        self.root.attributes('-fullscreen', False)
        if self.original_geometry:
            self.root.geometry(self.original_geometry)
        self.is_fullscreen = False
        self.status_var.set("Exited fullscreen mode")
    
    def on_chart_type_change(self, event):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
            
        chart_type = self.chart_type_var.get()
        
        if chart_type == "Histogram":
            bins_label = ttk.Label(self.options_frame, text="Number of bins:")
            bins_label.grid(row=0, column=0, padx=5, sticky=tk.W)
            
            self.bins_var = tk.StringVar(value="10")
            bins_entry = ttk.Entry(self.options_frame, textvariable=self.bins_var, width=10)
            bins_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
            
        elif chart_type == "Heatmap":
            corr_label = ttk.Label(self.options_frame, text="Show Correlation Matrix")
            corr_label.grid(row=0, column=0, padx=5, sticky=tk.W)
            
            self.corr_var = tk.BooleanVar(value=True)
            corr_check = ttk.Checkbutton(self.options_frame, variable=self.corr_var)
            corr_check.grid(row=0, column=1, padx=5, sticky=tk.W)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("All Data Files", "*.csv *.xlsx *.xls *.json *.txt"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("JSON Files", "*.json"),
            ("Text Files", "*.txt")
        ])
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            elif file_path.endswith('.txt'):
                self.data = pd.read_csv(file_path, sep=None, engine='python')
            else:
                messagebox.showerror("Unsupported Format", "File format not supported.")
                return

            columns = list(self.data.columns)
            self.column_choices['values'] = columns
            self.column_choices2['values'] = columns
            
            if len(columns) > 0:
                self.column_choices.set(columns[0])
                if len(columns) > 1:
                    self.column_choices2.set(columns[1])
                else:
                    self.column_choices2.set('')
            
            self.update_preview()
            
            self.status_var.set(f"Loaded {file_path} - {len(self.data)} rows, {len(columns)} columns")
            
        except Exception as e:
            error_msg = f"Failed to load file:\n{str(e)}"
            self.status_var.set("Error loading file")
            messagebox.showerror("Error", error_msg)
            print(traceback.format_exc())
    
    def update_preview(self):
        if self.data is not None:
            preview_content = f"Data Shape: {self.data.shape}\n\n"
            preview_content += f"Columns: {list(self.data.columns)}\n\n"
            preview_content += "First 10 rows:\n"
            preview_content += self.data.head(10).to_string()
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, preview_content)
    
    def plot_chart(self):
        if self.data is None:
            messagebox.showwarning("No Data", "Please load a file first.")
            return
            
        chart_type = self.chart_type_var.get()
        col1 = self.column_choices.get()
        
        if not col1:
            messagebox.showwarning("Selection Error", "Please select at least one column.")
            return
            
        self.clear_chart()
        
        try:
            plt.style.use('default')
            self.fig, ax = plt.subplots(figsize=(10, 6))
            
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
            
            if chart_type == "Bar":
                col2 = self.column_choices2.get()
                if col2:
                    self.data.groupby(col1)[col2].mean().plot(kind='bar', ax=ax, color=colors[0])
                    ax.set_ylabel(col2)
                else:
                    self.data[col1].value_counts().plot(kind='bar', ax=ax, color=colors[0])
                ax.set_xlabel(col1)
                
            elif chart_type == "Line":
                col2 = self.column_choices2.get()
                if col2:
                    self.data.plot(x=col1, y=col2, kind='line', ax=ax, color=colors[1])
                    ax.set_ylabel(col2)
                else:
                    self.data[col1].plot(ax=ax, color=colors[1])
                ax.set_xlabel(col1)
                
            elif chart_type == "Pie":
                self.data[col1].value_counts().plot.pie(autopct='%1.1f%%', ax=ax, colors=colors)
                ax.set_ylabel('')
                
            elif chart_type == "Scatter":
                col2 = self.column_choices2.get()
                if not col2:
                    messagebox.showwarning("Selection Error", "Scatter plot requires two columns.")
                    return
                self.data.plot.scatter(x=col1, y=col2, ax=ax, color=colors[4])
                
            elif chart_type == "Histogram":
                bins = int(self.bins_var.get()) if hasattr(self, 'bins_var') else 10
                self.data[col1].plot.hist(bins=bins, ax=ax, color=colors[2])
                ax.set_xlabel(col1)
                
            elif chart_type == "Boxplot":
                self.data[col1].plot.box(ax=ax)
                ax.set_ylabel(col1)
                
            elif chart_type == "Heatmap":
                if hasattr(self, 'corr_var') and self.corr_var.get():
                    numeric_data = self.data.select_dtypes(include=[np.number])
                    if numeric_data.empty:
                        messagebox.showwarning("Data Error", "No numeric columns for correlation heatmap.")
                        return
                    corr = numeric_data.corr()
                    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                else:
                    messagebox.showwarning("Not Implemented", "General heatmap not yet implemented.")
                    return
            
            ax.set_title(f"{chart_type} Chart of {col1}", fontsize=14, fontweight='bold', color='#2c3e50')
            ax.set_facecolor('#f8f9fa')
            self.fig.patch.set_facecolor('#ffffff')
            plt.tight_layout()
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.scrollable_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.scrollable_frame)
            self.toolbar.update()
            self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            self.scrollable_frame.update_idletasks()
            self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))
            
            self.status_var.set(f"Generated {chart_type} chart - Use scrollbars to navigate")
            
        except Exception as e:
            error_msg = f"Error creating chart:\n{str(e)}"
            self.status_var.set("Chart generation failed")
            messagebox.showerror("Plot Error", error_msg)
            print(traceback.format_exc())
    
    def save_chart(self):
        if self.fig is None:
            messagebox.showwarning("No Chart", "Please generate a chart first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("PDF Document", "*.pdf"),
                ("SVG Image", "*.svg")
            ],
            title="Save chart as..."
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
                self.status_var.set(f"Chart saved to {file_path}")
                messagebox.showinfo("Saved", f"Chart saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save chart:\n{str(e)}")
    
    def clear_chart(self):
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
            
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            
        self.pan_enabled = False

def main():
    root = tk.Tk()
    app = DataVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()