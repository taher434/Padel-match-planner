"""Tkinter window for Padel Match Planner. Start Flask before running this file."""

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import client


class PadelPlanner:
    """Keep the window's widgets, displayed matches, and selected match together."""

    def __init__(self, root):
        self.root = root
        self.root.title("Padel Match Planner")
        self.root.geometry("1120x650")
        self.root.minsize(1000, 580)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        self.selected_id = None
        self.matches = {}
        self.fields = {}
        self.city_filter = tk.StringVar()
        self.status = tk.StringVar(value="Ready. Start Flask, then click Refresh.")
        self.selection_text = tk.StringVar(value="New match")

        title = ttk.Frame(root, padding=(16, 14, 16, 8))
        title.grid(row=0, column=0, sticky="ew")
        ttk.Label(title, text="Padel Match Planner", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(title, text="Save local matches and find a match in your city.").pack(anchor="w", pady=(4, 0))

        self.build_form()
        self.build_match_list()
        ttk.Label(root, textvariable=self.status, padding=16, wraplength=960).grid(
            row=3, column=0, sticky="ew"
        )
        self.clear_form()

    def build_form(self):
        """Create the five match inputs and the record action buttons."""
        form = ttk.LabelFrame(self.root, text="Match details", padding=12)
        form.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 12))
        labels = [
            ("name", "Match name"),
            ("city", "City"),
            ("court", "Court"),
            ("match_date", "Date (YYYY-MM-DD)"),
            ("skill_level", "Skill level"),
        ]
        for column, (field, label) in enumerate(labels):
            form.columnconfigure(column, weight=1)
            ttk.Label(form, text=label).grid(row=0, column=column, sticky="w", padx=4)
            self.fields[field] = tk.StringVar()
            if field == "skill_level":
                entry = ttk.Combobox(
                    form, textvariable=self.fields[field], state="readonly",
                    values=["Beginner", "Intermediate", "Advanced"], width=18,
                )
            else:
                entry = ttk.Entry(form, textvariable=self.fields[field], width=18)
            entry.grid(row=1, column=column, sticky="ew", padx=4, pady=(4, 12))

        actions = ttk.Frame(form)
        actions.grid(row=2, column=0, columnspan=5, sticky="ew")
        self.add_button = ttk.Button(actions, text="Add Match", command=self.add_match)
        self.add_button.pack(side="left", padx=4)
        self.edit_button = ttk.Button(actions, text="Save Changes", command=self.edit_match)
        self.edit_button.pack(side="left", padx=4)
        self.delete_button = ttk.Button(actions, text="Delete Match", command=self.delete_match)
        self.delete_button.pack(side="left", padx=4)
        ttk.Button(actions, text="New / Clear Form", command=self.clear_form).pack(side="left", padx=4)
        ttk.Label(actions, textvariable=self.selection_text).pack(side="right", padx=4)

    def build_match_list(self):
        """Create the city filter and a scrollable table of saved matches."""
        frame = ttk.LabelFrame(self.root, text="Saved matches", padding=12)
        frame.grid(row=2, column=0, sticky="nsew", padx=16)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        filters = ttk.Frame(frame)
        filters.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(filters, text="Filter by city:").pack(side="left", padx=(0, 8))
        city_entry = ttk.Entry(filters, textvariable=self.city_filter, width=25)
        city_entry.pack(side="left", padx=(0, 8))
        city_entry.bind("<Return>", self.filter_matches)
        ttk.Button(filters, text="Filter", command=self.filter_matches).pack(side="left", padx=4)
        ttk.Button(filters, text="Show All", command=self.show_all).pack(side="left", padx=4)
        ttk.Button(filters, text="Refresh", command=self.refresh_matches).pack(side="left", padx=4)

        columns = ["id", "name", "city", "court", "match_date", "skill_level"]
        self.table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        headings = ["ID", "Match name", "City", "Court", "Date", "Skill level"]
        widths = [50, 220, 150, 180, 120, 130]
        for column, heading, width in zip(columns, headings, widths):
            self.table.heading(column, text=heading)
            self.table.column(column, width=width, minwidth=50)
        self.table.grid(row=1, column=0, sticky="nsew")
        self.table.bind("<<TreeviewSelect>>", self.select_match)

        vertical = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        vertical.grid(row=1, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=self.table.xview)
        horizontal.grid(row=2, column=0, sticky="ew")
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)

    def clear_form(self):
        """Leave edit mode and prepare an empty form for a new match."""
        self.selected_id = None
        for field in self.fields:
            self.fields[field].set("")
        self.fields["match_date"].set(date.today().isoformat())
        self.fields["skill_level"].set("Beginner")
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.add_button.configure(state="normal")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.selection_text.set("New match")

    def select_match(self, event=None):
        """Copy the selected record into the form and remember its real ID."""
        selection = self.table.selection()
        if not selection:
            return
        match = self.matches.get(selection[0])
        if match is None:
            return
        self.selected_id = match["id"]
        for field in self.fields:
            self.fields[field].set(match[field])
        self.add_button.configure(state="disabled")
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.selection_text.set(f"Editing match #{self.selected_id}")

    def read_form(self):
        """Collect named values; Flask is responsible for validating them."""
        values = {}
        for field in self.fields:
            values[field] = self.fields[field].get()
        return values

    def show_error(self, message):
        self.status.set(message)
        messagebox.showerror("Padel Match Planner", message, parent=self.root)

    def refresh_matches(self, success_message=""):
        """Replace the table only after a successful GET, allowing safe retries."""
        city = self.city_filter.get().strip()
        result = client.get_matches(city)
        if not result["success"]:
            message = result["message"]
            if success_message:
                message = success_message + " The list could not refresh. " + message
            self.show_error(message)
            return False

        for item in self.table.get_children():
            self.table.delete(item)
        self.matches = {}
        for match in result["matches"]:
            item = str(match["id"])
            self.matches[item] = match
            self.table.insert("", "end", iid=item, values=(
                match["id"], match["name"], match["city"], match["court"],
                match["match_date"], match["skill_level"],
            ))
        self.clear_form()
        if self.matches:
            summary = f"Showing {len(self.matches)} match(es). Select a row to edit or delete."
        else:
            summary = "No matches found. Add a match or try another city."
        if city:
            summary += f" City filter: {city}."
        self.status.set((success_message + " " + summary).strip())
        return True

    def filter_matches(self, event=None):
        self.refresh_matches()

    def show_all(self):
        self.city_filter.set("")
        self.refresh_matches()

    def finish_action(self, result):
        """Keep failed input, but clear a saved form before refreshing the list."""
        if not result["success"]:
            self.show_error(result["message"])
            return
        self.clear_form()
        self.refresh_matches(result["message"])

    def add_match(self):
        self.finish_action(client.add_match(self.read_form()))

    def edit_match(self):
        if self.selected_id is None:
            self.show_error("Select a match before saving changes.")
            return
        self.finish_action(client.update_match(self.selected_id, self.read_form()))

    def delete_match(self):
        if self.selected_id is None:
            self.show_error("Select a match before deleting.")
            return
        name = self.matches[str(self.selected_id)]["name"]
        confirmed = messagebox.askyesno(
            "Confirm deletion", f'Delete match #{self.selected_id}: "{name}"?',
            parent=self.root,
        )
        if confirmed:
            self.finish_action(client.delete_match(self.selected_id))


def main():
    root = tk.Tk()
    planner = PadelPlanner(root)
    root.after(100, planner.refresh_matches)
    root.mainloop()


if __name__ == "__main__":
    main()
