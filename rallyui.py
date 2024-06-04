import rallydb as rb
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# CHANGELOG
# change variable names
# fix some warnings
# ability to save the selected stages to the SaveSlots.cfg file
# add radiobuttons for selecting weather for custom rally
#
# TODO
# radiobuttons override the stage object weather, but kinda difficult to show inside the listbox, mabye do another window, only shows for one stage at the time? kinda shit
# exporting custom rally works
# daily/weekly counter
# button to output stages to file?
#
# make rallyui standalone?
# if searching for stage, activate the right country
# don't trust comments

# integrate some kind of creating and loading custom rally from SaveSlots.cfg?
# add weather, while highlighting a stage, select weather underneath in a checkbox

class App:
    # every line in file
    stages_from_file: list[rb.Stage] = []
    # every selected object right window
    selected_stages_obj: list[rb.Stage] = []
    # used in if statement
    selected_stages: list[str] = []
    # results list, left side, objects
    results_vector: list[rb.Stage] = []

    all_locations: list[str] = list(rb.Stage.location_stage_names.keys())
    all_groups: list[str] = list(rb.Stage.car_names.keys())
    all_stages = list(rb.Stage.location_stage_names.values())
    stages_list = []
    for stages in all_stages:
        for stage in stages:
            stages_list.append(stage)
    # this is the only way surely...
    user_input_stage = ""

    def __init__(self, root):
        self.filepath = ""
        self.root = root
        self.root.title("RallyUI")
        #root.geometry("800x600") ??
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.get_file_path)
        self.file_menu.add_command(label="Load as custom rally", command=self.load_custom_rally)
        self.file_menu.add_command(label="Export as custom rally", command=self.export_custom_rally)
        self.file_menu.add_command(label="Help/About", command=self.show_help)
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for listboxes and buttons
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Results Listbox frame
        self.results_frame = ttk.Frame(self.top_frame)
        self.results_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        self.results_listbox = tk.Listbox(self.results_frame, selectmode=tk.SINGLE, width=60, height=15, font=("courier", 12))
        self.results_listbox.bind('<FocusIn>', self.on_focus_in)
        self.results_listbox.bind('<FocusOut>', self.on_focus_out)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button frame for add/remove buttons
        self.button_frame = ttk.Frame(self.top_frame)
        self.button_frame.pack(side=tk.LEFT, padx=10, pady=5)

        self.results_button = tk.Button(self.button_frame, text='add>>', command=self.add_stage)
        self.results_button.pack(side=tk.TOP, pady=5, anchor='center')

        self.selected_button = tk.Button(self.button_frame, text='<<remove', command=self.remove_stage)
        self.selected_button.pack(side=tk.TOP, pady=5, anchor='center')

        self.clear_button = tk.Button(self.button_frame, text="Clear all", command=self.clear_selections)
        self.clear_button.pack(side=tk.TOP, pady=5)

        # Selected Listbox frame
        self.selected_frame = ttk.Frame(self.top_frame)
        self.selected_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        self.selected_listbox = tk.Listbox(self.selected_frame, selectmode=tk.SINGLE, width=60, height=15, font=("courier", 12))
        self.selected_listbox.bind('<FocusIn>', self.on_focus_in)
        self.selected_listbox.bind('<FocusOut>', self.on_focus_out)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Middle frame for total time labels
        self.middle_frame = ttk.Frame(self.main_frame)
        self.middle_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.selected_stages_time_label = tk.Label(self.middle_frame, text="total time->", font=("courier", 12))
        self.selected_stages_time_label.pack(side=tk.LEFT, padx=5)

        self.total_time_label = tk.Label(self.middle_frame, text="total time", font=("courier", 12))
        self.total_time_label.pack(side=tk.LEFT, padx=40)

        self.sum_of_best_label = tk.Label(self.middle_frame, text="sum of best->", font=("courier", 12))
        self.sum_of_best_label.pack(side=tk.LEFT, padx=0)

        self.selected_stages_time = tk.Label(self.middle_frame, text="sum of best", font=("courier", 12))
        self.selected_stages_time.pack(side=tk.LEFT, padx=40)

        # radiobuttons

        # Middle frame for radiobuttons
        #self.middle_frame = ttk.Frame(self.main_frame)
        #self.middle_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.radio_var = tk.StringVar(value="morning") 
        radio_buttons = ["morning", "afternoon", "sunset", "rain", "fog", "night"]
        for option in radio_buttons:
            radio_button = ttk.Radiobutton(self.middle_frame, text=option, variable=self.radio_var, value=option)
            radio_button.pack(side=tk.LEFT, anchor='w', pady=2)


        # Bottom frame for other controls
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.clear_user_input = tk.Button(self.bottom_frame, text="reset search", command=self.clear_input)
        self.clear_user_input.pack(side=tk.LEFT, padx=10)

        self.label_entry = tk.Label(self.bottom_frame, text="search for stagename:")
        self.label_entry.pack(side=tk.LEFT, padx=10)

        self.entry = tk.Entry(self.bottom_frame)
        self.entry.pack(side=tk.LEFT, padx=10)
        self.entry.bind('<Return>', self.on_enter)
        self.entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.entry.bind('<FocusOut>', self.on_entry_focus_out)

        self.text = tk.Label(self.bottom_frame, text="use arrow keys or hjkl\nto add or remove stages")
        self.text.pack(side=tk.LEFT, padx=10)

        # Checkbutton frames
        self.checkbutton_frames = []
        for i in range(4):
            frame = ttk.Frame(self.main_frame)
            frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
            self.checkbutton_frames.append(frame)
        # Checkbutton frames with borders
        self.checkbutton_frames = []
        labels = ["Locations", "Groups", "Weather", "Direction"]
        for i in range(4):
            frame = ttk.LabelFrame(self.main_frame, text=labels[i], padding=10)
            frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
            self.checkbutton_frames.append(frame)

        # Populate checkbutton frames
        self.populate_checkbuttons()

        # Key bindings
        root.bind('<Up>', self.navigate)
        root.bind('<Down>', self.navigate)
        root.bind('<Right>', self.add_stage)
        root.bind('<Left>', self.remove_stage)
        root.bind('h', self.remove_stage)
        root.bind('l', self.add_stage)
        root.bind('j', self.navigate)
        root.bind('k', self.navigate)
        self.results_listbox.select_set(0)
        self.results_listbox.activate(0)

        self.update_all_stages()

    def populate_checkbuttons(self):
        categories = [
            (App.all_locations, 0),
            (App.all_groups, 1),
            (["dry", "wet"], 2),
            (["forward", "reverse"], 3)
        ]

        for labels, index in categories:
            self.check_vars = {}
            for label in labels:
                var = tk.BooleanVar()
                self.check_vars[label] = var
                checkbutton = tk.Checkbutton(self.checkbutton_frames[index], text=label, variable=var, command=lambda var=var, label=label: self.toggle_action(var, label))
                checkbutton.pack(side=tk.LEFT, padx=10, pady=5)

    def on_focus_in(self, event):
        self.bind_navigation_keys()

    def on_focus_out(self, event):
        self.unbind_navigation_keys()

    def on_entry_focus_in(self, event):
        self.unbind_navigation_keys()

    def on_entry_focus_out(self, event):
        self.bind_navigation_keys()

    def bind_navigation_keys(self):
        self.root.bind('<Up>', self.navigate)
        self.root.bind('<Down>', self.navigate)
        self.root.bind('<Right>', self.add_stage)
        self.root.bind('<Left>', self.remove_stage)
        self.root.bind('h', self.navigate)
        self.root.bind('j', self.navigate)
        self.root.bind('k', self.navigate)
        self.root.bind('l', self.navigate)

    def unbind_navigation_keys(self):
        self.root.unbind('<Up>')
        self.root.unbind('<Down>')
        self.root.unbind('<Right>')
        self.root.unbind('<Left>')
        self.root.unbind('h')
        self.root.unbind('j')
        self.root.unbind('k')
        self.root.unbind('l')

    def navigate(self, event):
        focused_widget = self.root.focus_get()
        if isinstance(focused_widget, tk.Listbox):
            if event.keysym in ['Up', 'k']:
                self.move_up(focused_widget)
            elif event.keysym in ['Down', 'j']:
                self.move_down(focused_widget)
            elif event.keysym in ['l']:
                self.add_stage()
            elif event.keysym in ['h']:
                self.remove_stage()

    def move_up(self, listbox):
        current_selection = listbox.curselection()
        if current_selection:
            current_index = current_selection[0]
            if current_index > 0:
                listbox.select_clear(current_index)
                listbox.select_set(current_index - 1)
                listbox.activate(current_index - 1)
                listbox.see(current_index - 1)

    def move_down(self, listbox):
        current_selection = listbox.curselection()
        if current_selection:
            current_index = current_selection[0]
            if current_index < listbox.size() - 1:
                listbox.select_clear(current_index)
                listbox.select_set(current_index + 1)
                listbox.activate(current_index + 1)
                listbox.see(current_index + 1)

    def show_help(self):
        # TODO
        # better help / instruction message
        messagebox.showinfo("Help", "Add search options with the boxes,\nadd stages to the right window with arrow keyes or with the move>> button\nThe search function only works if the corresponding country is selected.")

    def get_file_path(self):
        self.filepath = filedialog.askopenfilename()
        print(f"trying to open file: {self.filepath}")
        # reset all arrays
        App.stages_from_file.clear()
        App.selected_stages_obj.clear()
        App.selected_stages.clear()
        App.results_vector.clear()
        self.read_file()

    def read_file(self):
        if not self.filepath:
            self.filepath = "Leaderboards.txt"
        with open(self.filepath ,'r') as file:
            lines = file.readlines()
        for line in lines:
            if "daily" in line or "weekly" in line:
               continue
            try:
                App.stages_from_file.append(rb.Stage(line))
            except TypeError:
                continue
        self.update_all_stages()

    # do menu for loaded custom rally
    # select the custom rally to configure -> save again
    # maybe do only save to custom rally?
    def load_custom_rally(self) -> list[str]:
        with open("SaveSlots.cfg", "r") as file:
            lines = file.readlines()
        return lines

    def export_custom_rally(self):
        # TODO
        # check if only one country is selected

        custom_rallies = self.load_custom_rally()

        string = ""
        print("exporting custom rally..")
        try:
            rb.eprint("getting location..")
            location = App.selected_stages_obj[0].location
        except IndexError:
            rb.eprint("IndexError..aborting")
            return
        string += f"{location.upper()}|"
        for stage in App.selected_stages_obj:
            string += f"{stage.stage_number}.{stage.weather},"
        string = string[:-1]
        string += "\r"
        # write this to file
        print("writing to file..")
        print(string)

        count = 0
        with open("SaveSlots.cfg", "w") as file:
            for line in custom_rallies:
                if line in ["\n", "\r\n"]:
                    continue
                file.write(line)
                count += 1
            print("count after custom rally file: ", count)
            if count < 10:
                file.write(string)
                count += 1
                print(f"count after new rally: {count}")
                while count <= 10:
                    file.write("\n")
                    count += 1
            else:
                print("already 10 custom rallies..aborting")
                return


    def update_all_stages(self):
        # left side
        self.results_listbox.delete(0, tk.END)
        self.results_vector.clear()
        for object in App.stages_from_file:
            if (object.location in App.selected_stages and
                object.group in App.selected_stages and
                object.weather in App.selected_stages and
                object.direction in App.selected_stages and
                (not App.user_input_stage or App.user_input_stage in object.stage)
            ):

                time = object.time.get_time()
                string: str = f"{object.location:<10} {object.stage:<17} {object.group:<7}{object.direction:<3} {object.weather:<3} {time}"
                # <3 :)
                self.results_listbox.insert(tk.END, string)
                self.results_vector.append(object)
            else:
                continue
        self.update_total_time()
        self.update_stage_time()
        self.results_listbox.select_set(0)
        self.results_listbox.activate(0)

    # some buttons need event
    def add_stage(self, event=None):
        index = 0
        #print(self.radio_var.get())
        focused_widget = self.root.focus_get()
        if focused_widget == self.results_listbox:
            selected_idx = self.results_listbox.get(tk.ACTIVE)
            try:
                index = self.results_listbox.curselection()[0]
            except IndexError:
                rb.eprint("DEBUG: nothing to select")
            if selected_idx:
                self.selected_listbox.insert(tk.END, selected_idx)
                App.results_vector[index].weather = self.radio_var.get()
                App.selected_stages_obj.append(App.results_vector[index])
                #print(App.results_vector[index].weather)
            self.update_stage_time()

    def remove_stage(self, event=None):
        selected_idx = self.selected_listbox.curselection()
        try:
            index = self.selected_listbox.curselection()[0]
            if selected_idx:
                self.selected_listbox.delete(selected_idx)
                App.selected_stages_obj.pop(index)
            self.update_stage_time()
            if index <= 0:
                self.selected_listbox.select_set(0)
            else:
                self.selected_listbox.select_set(index - 1)
                self.selected_listbox.activate(0)
        except IndexError:
            rb.eprint("DEBUG: nothing to remove")

    def clear_selections(self):
        self.selected_listbox.delete(0, tk.END)
        App.selected_stages_obj.clear()
        self.update_stage_time()

    def update_stage_time(self):
        total_time = 0
        hours, minutes, seconds, ms = 0, 0, 0, 0
        for stage in App.selected_stages_obj:
            if stage.time_ms >= 356400000:
                continue
            total_time += stage.time_ms
        try:
            hours, minutes, seconds, ms = rb.Time.convert_race_time(total_time)
        except TypeError:
            print("error converting number in Leaderboards file to time")
        total_time_str = f"{hours}:{minutes:02d}:{seconds:02d}.{ms:03d}"
        self.selected_stages_time.config(text=total_time_str)

    def update_total_time(self):
        total_time = 0
        hours, minutes, seconds, ms = 0, 0, 0, 0
        for stage in self.results_vector:
            total_time += stage.time_ms
            try:
                hours, minutes, seconds, ms = rb.Time.convert_race_time(total_time)
            except TypeError:
                continue
        total_time_str = f"{hours}:{minutes:02d}:{seconds:02d}.{ms:03d}"
        self.total_time_label.config(text=total_time_str)

    def toggle_action(self, var, label):
        if var.get():
            App.selected_stages.append(label)
        else:
            App.selected_stages.remove(label)
        self.update_all_stages()
        self.results_listbox.select_set(0)
        self.results_listbox.activate(0)

    def on_enter(self, event):
        user_input: str = self.entry.get()
        user_list: list[str] = []
        user_list.append(user_input)
        print(f"user: {user_input}")
        try:
            search_results: list[str] = rb.find_stage(user_list)
            App.user_input_stage = search_results[0]
            print(f"search: {search_results}")
            self.update_all_stages()
        except SystemError:
            pass

    def clear_input(self):
        self.entry.delete(0, tk.END)
        App.user_input_stage = ""
        self.update_all_stages()

def main():
    root = tk.Tk()
    app = App(root)
    app.read_file()
    root.mainloop()

if __name__ == "__main__":
    main()
