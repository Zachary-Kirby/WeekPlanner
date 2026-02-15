#!/usr/bin/env python3
import gi
import time
import datetime
from typing import cast, Optional
import random
import json



#By Zachary Kirby. Claude Sonnet 4.5 used with qwen3 coder 30b for extra guidence
#with what functionality exists since documentation is a nightmare
#Gnome Python API used to sanity check AI results since AI hallucinates functionality for GTK 50% of the time


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GObject # type: ignore

Days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

class WeekPlanner(Gtk.ApplicationWindow):
  def __init__(self, **kwargs):
    global Days
    super().__init__(**kwargs, title="Week Planner")
    day = datetime.datetime.now().strftime("%A")
    dates = [(datetime.datetime.now()+datetime.timedelta(days=i-3)).strftime("%m/%d/%Y") for i in range(11)]
    print(dates)
    print("not caching")
    current_day_index = Days.index(day)
    provider = Gtk.CssProvider()
    provider.load_from_path("style.css")
    default_display = Gdk.Display.get_default()
    self.entries: list[DraggableTextBox] = []
    if default_display:
      Gtk.StyleContext.add_provider_for_display(default_display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    self.row = Gtk.Box(vexpand=True,hexpand=True, spacing=0, homogeneous=False,halign=Gtk.Align.FILL)
    self.dayLabels = [Gtk.Label(hexpand=True, valign=Gtk.Align.START) for i in range(11)]
    self.dateLabels = [Gtk.Label(hexpand=True, valign=Gtk.Align.START) for i in range(11)]
    self.columns = [Gtk.Box(halign=Gtk.Align.FILL, orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.FILL, vexpand=True) for i in range(11)]
    self.item_lists = [TargetList(dates[i], halign=Gtk.Align.FILL, orientation=Gtk.Orientation.VERTICAL, hexpand=True, valign=Gtk.Align.FILL, vexpand=True) for i in range(11)]
    self.dayLabels[3].add_css_class("current_day_header")
    self.dateLabels[3].add_css_class("current_day_header")
    
    for i in range(11):
      self.item_lists[i].add_css_class("list")
      self.dayLabels[i].set_markup(f"<b>{Days[(i+current_day_index-3)%7]}</b>")
      self.dateLabels[i].set_markup(f"<b>{dates[i]}</b>")
      add_item_button = Gtk.Button(label="+", halign=Gtk.Align.FILL, hexpand=True)
      remove_item_button = Gtk.Button(label="-", halign=Gtk.Align.FILL, hexpand=True)
      self.columns[i].append(self.dayLabels[i])
      self.columns[i].append(self.dateLabels[i])
      control_buttons = Gtk.Box(halign=Gtk.Align.FILL, hexpand=True)
      control_buttons.append(add_item_button)
      control_buttons.append(remove_item_button)
      self.columns[i].append(control_buttons)
      self.columns[i].append(self.item_lists[i])
      add_item_button.connect("clicked", self.add_new_item, self.item_lists[i])
      remove_item_button.connect("clicked", self.remove_item, self.item_lists[i])
      self.row.append(self.columns[i])
    
    self.set_child(self.row)
    
    self.connect("close_request", self.requested_close)
    
    self.load()
    #self.connect("realize", lambda w: self.load())
  
  def add_new_item(self, _widget: Gtk.Widget, list_box: Gtk.Box):
    text_entry_box = DraggableTextBox(wrap_mode=Gtk.WrapMode.WORD, width_request=128, height_request=24*1.5)
    list_box.append(text_entry_box)
    text_entry_box.grab_focus()
    buffer = text_entry_box.get_buffer()
    end_iter = buffer.get_end_iter()
    buffer.place_cursor(end_iter)
    text_entry_box.set_cursor_visible(True)
    self.entries.append(text_entry_box)
  
  def remove_item(self, _widget: Gtk.Widget, list_box: Gtk.Box):
    last_child = cast(DraggableTextBox, list_box.get_last_child())
    if last_child:
      self.entries.remove(last_child)
      list_box.remove(last_child)
  
  def requested_close(self, something):
    self.save()
  
  def save(self, filePath="WeekPlanner.json"):
    #TODO figure out how to save each item on the planner to a json file with the associated date
    data: dict[str, list] = {}
    for textEntry in self.entries:
      parent: TargetList = cast(TargetList, textEntry.get_parent())
      if parent and parent.date:
        if data.get(parent.date, None) == None:
          data[parent.date] = []
        data[parent.date].append(textEntry.get_buffer().props.text)
    with open(filePath, "w") as f:
      f.write(json.dumps(data)) 
  
  def load(self, filePath="WeekPlanner.json"):
    data: dict[str, list[str]] = {}
    with open(filePath, "r") as f:
      data = json.loads(f.read())
    for i in range(11):
      item_list = self.item_lists[i]
      if item_list.date == None: continue
      for items in data.get(item_list.date, []):
        textBox = DraggableTextBox(wrap_mode=Gtk.WrapMode.WORD, width_request=128, height_request=24*1.5)
        textBox.props.buffer.set_text(items)
        textBox.set_cursor_visible(True)
        textBox.set_accepts_tab(False)
        item_list.append(textBox)
        self.entries.append(textBox)


class DraggableTextBox(Gtk.TextView):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    
    self.add_css_class("entry")
    self.set_accepts_tab(False)
    dragController = Gtk.DragSource()
    dragController.connect("prepare", self.on_drag_prepare)
    dragController.connect("drag-begin", self.on_drag_begin)
    self.add_controller(dragController)
    self.get_buffer().connect("changed", self.insertingText)
  
  def insertingText(self, text: Gtk.TextBuffer):
    if text.props.text.startswith("!!"):
      self.add_css_class("priority")
    else:
      self.remove_css_class("priority")
  
  def on_drag_prepare(self, _ctrl, _x, _y):
    item = Gdk.ContentProvider.new_for_value(self)
    return item
  
  def on_drag_begin(self, ctrl, _drag):
    icon = Gtk.WidgetPaintable.new(self)
    ctrl.set_icon(icon, 0, 0)

class TargetList(Gtk.Box):
  def __init__(self, date: Optional[str]=None, **kwargs):
    super().__init__(**kwargs)
    
    self.date: Optional[str] = date
    dropController = Gtk.DropTarget.new(
      type=GObject.TYPE_NONE, actions=Gdk.DragAction.COPY
    )
    dropController.set_gtypes([DraggableTextBox])
    dropController.connect("drop", self.on_drop)
    self.add_controller(dropController)
  
  def on_drop(self, _ctrl, value, _x, _y):
    if isinstance(value, DraggableTextBox):
      parent: Gtk.Box | None = cast(Gtk.Box, value.get_parent())
      if parent:
        parent.remove(value)
      self.append(value)

def on_activate(app):
  # Create window
  win = WeekPlanner(application=app)
  win.present()


# Create a new application
app = Gtk.Application(application_id="io.github.ZacharyKirby.WeekPlanner")
app.connect("activate", on_activate)

# Run the application
app.run(None)

