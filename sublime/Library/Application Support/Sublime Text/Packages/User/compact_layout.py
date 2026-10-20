import sublime
import sublime_plugin

def plugin_loaded():
    for window in sublime.windows():
        window.set_minimap_visible(False)

class CompactLayoutListener(sublime_plugin.EventListener):
    def on_new_window(self, window):
        window.set_minimap_visible(False)
