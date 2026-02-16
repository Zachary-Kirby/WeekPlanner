# Dependencies for GTK can be found at
https://pygobject.gnome.org/getting_started.html


# If an icon in the desktop apps menu is desired

### Ubuntu 24.04

By no means am I an expert using .desktop files, but
edit paths Exec to absolute path to the python file
edit Icon to the absolut path to the icon you want
edit Path to the directory you want to save the save data to

run the following
```bash
echo "\
[Desktop Entry]
Type=Application
Version=1.5
Name=Week Planner
Comment=Plan a week ahead and see overdue items
Icon=PATH TO YOUR ICON/icon.png
Exec=PATH TO THE PYTHON FILE/WeekPlanner.py
Path=PATH TO THE FOLDER TO SAVE TO" > ~/.local/share/applications/io.github.ZacharyKirby.WeekPlanner.desktop
sudo update-desktop-database
```

You must provide your own icon file.