"""User-owned presentation for Codex chat panels and transcript tabs."""
import sublime
import sublime_plugin

CHAT_SYNTAX = "Packages/Codex/plugin/vendor/sublime_chat_ui/Syntaxes/ChatMarkdown.sublime-syntax"


def style_chat(view):
    if not view or not view.is_valid():
        return
    settings = view.settings()
    if settings.get("syntax") != CHAT_SYNTAX and not settings.get("codex_is_transcript"):
        return
    values = {
        "font_face": "JetBrainsMono NFM",
        "font_size": 15,
        "font_options": [],
        "line_padding_top": 3,
        "line_padding_bottom": 3,
        "word_wrap": True,
        "wrap_width": 0,
        "line_numbers": False,
        "gutter": True,
        "highlight_line": False,
        "draw_white_space": "none",
        "rulers": [],
        "margin": 12,
        "color_scheme": "Packages/User/Codex Dark.sublime-color-scheme",
    }
    for key, value in values.items():
        if settings.get(key) != value:
            settings.set(key, value)


def style_all():
    for window in sublime.windows():
        for view in window.views():
            style_chat(view)
        for name in window.panels():
            if name.startswith("output."):
                style_chat(window.find_output_panel(name[7:]))


def plugin_loaded():
    sublime.set_timeout(style_all, 0)
    sublime.load_settings("Preferences.sublime-settings").add_on_change("codex_chat_style", style_all)


def plugin_unloaded():
    sublime.load_settings("Preferences.sublime-settings").clear_on_change("codex_chat_style")


class CodexChatAppearance(sublime_plugin.EventListener):
    def on_activated(self, view):
        style_chat(view)

    def on_load(self, view):
        style_chat(view)

    def on_post_window_command(self, window, command_name, args):
        if command_name in ("show_panel", "codex_new_message", "codex_open_transcript_tab"):
            sublime.set_timeout(style_all, 0)
