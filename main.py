import re
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

# Força o modo horizontal (Landscape)
Window.size = (900, 500)


def set_bg_color(widget, r, g, b, a=1):
    with widget.canvas.before:
        Color(r, g, b, a)
        widget.rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(
        size=lambda instance, value: setattr(instance.rect, "size", value),
        pos=lambda instance, value: setattr(instance.rect, "pos", value),
    )


# --- COLUNA DE ROLAGEM DE NÚMEROS (SELETOR ESTILO RELÓGIO) ---
class ScrollColumn(BoxLayout):

    def __init__(self, title, max_val, on_select_callback, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.selected_val = 0
        self.buttons = []
        self.on_select_callback = on_select_callback

        # Título da Coluna (Horas, Minutos, Segundos)
        lbl = Label(
            text=title,
            font_size="16sp",
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint_y=0.15,
        )
        self.add_widget(lbl)

        # ScrollView para rolar os números para cima/baixo
        scroll = ScrollView(
            size_hint_y=0.85, do_scroll_x=False, do_scroll_y=True
        )
        container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=4, padding=(5, 5)
        )
        container.bind(minimum_height=container.setter("height"))

        for i in range(max_val + 1):
            btn = Button(
                text=f"{i:02d}",
                size_hint_y=None,
                height=48,
                font_size="20sp",
                bold=True,
                background_color=(
                    (1, 0.5, 0, 1) if i == 0 else (0.2, 0.2, 0.2, 1)
                ),
            )
            btn.bind(on_release=lambda x, val=i: self.select_val(val))
            self.buttons.append(btn)
            container.add_widget(btn)

        scroll.add_widget(container)
        self.add_widget(scroll)

    def select_val(self, val):
        self.selected_val = val
        for i, b in enumerate(self.buttons):
            if i == val:
                b.background_color = (1, 0.5, 0, 1)  # Destaque Laranja
            else:
                b.background_color = (0.2, 0.2, 0.2, 1)
        self.on_select_callback()


# --- ECRÃ 1: PAINEL INICIAL ---
class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation="vertical", padding=30, spacing=20
        )
        set_bg_color(layout, 0.08, 0.08, 0.08)

        lbl = Label(
            text="GOLDAZI'S PAINEL",
            font_size="36sp",
            bold=True,
            color=(1, 0.15, 0.15, 1),
        )
        sub = Label(
            text="Utilitários de Sistema (Mobile)",
            font_size="18sp",
            color=(0.8, 0.8, 0.8, 1),
        )

        btn_grid = GridLayout(cols=2, spacing=20, size_hint_y=0.5)
        btn_start = Button(
            text="TEMPORIZADOR",
            background_color=(1, 0.5, 0, 1),
            font_size="20sp",
            bold=True,
        )
        btn_start.bind(
            on_release=lambda x: setattr(
                self.manager, "current", "action_menu"
            )
        )

        btn_exit = Button(
            text="FECHAR PAINEL",
            background_color=(0.3, 0.3, 0.3, 1),
            font_size="20sp",
        )
        btn_exit.bind(on_release=lambda x: App.get_running_app().stop())

        btn_grid.add_widget(btn_start)
        btn_grid.add_widget(btn_exit)

        layout.add_widget(lbl)
        layout.add_widget(sub)
        layout.add_widget(btn_grid)
        self.add_widget(layout)


# --- ECRÃ 2: ESCOLHA DA FUNÇÃO ---
class ActionMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation="vertical", padding=20, spacing=15
        )
        set_bg_color(layout, 0.08, 0.08, 0.08)

        title = Label(
            text="O temporizador é para...",
            font_size="24sp",
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint_y=0.2,
        )
        layout.add_widget(title)

        grid = GridLayout(cols=2, spacing=15, size_hint_y=0.6)
        actions = [
            ("Encerrar PC", 0),
            ("Reiniciar PC", 1),
            ("Suspender PC", 2),
            ("Apenas Contagem", 3),
        ]

        for text, act_id in actions:
            btn = Button(
                text=text,
                background_color=(1, 0.4, 0, 1),
                font_size="18sp",
                bold=True,
            )
            btn.bind(on_release=lambda x, a=act_id: self.select_action(a))
            grid.add_widget(btn)

        layout.add_widget(grid)

        bot_layout = BoxLayout(spacing=10, size_hint_y=0.2)
        btn_back = Button(
            text="[ S / F ] Voltar ao Painel",
            background_color=(0.3, 0.3, 0.3, 1),
        )
        btn_back.bind(
            on_release=lambda x: setattr(self.manager, "current", "main_menu")
        )
        bot_layout.add_widget(btn_back)

        layout.add_widget(bot_layout)
        self.add_widget(layout)

    def select_action(self, action_id):
        self.manager.get_screen("time_input").action_id = action_id
        self.manager.current = "time_input"


# --- ECRÃ 3: SELEÇÃO DE TEMPO POR ROLAGEM ---
class TimeInputScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action_id = 3

        layout = BoxLayout(
            orientation="vertical", padding=15, spacing=10
        )
        set_bg_color(layout, 0.08, 0.08, 0.08)

        # Mostrador Superior do Tempo Selecionado
        self.lbl_time_display = Label(
            text="00:00:00",
            font_size="42sp",
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint_y=0.2,
        )
        layout.add_widget(self.lbl_time_display)

        # Área Central: 3 Colunas de Rolagem (Horas | Minutos | Segundos)
        picker_layout = BoxLayout(
            orientation="horizontal", spacing=15, size_hint_y=0.55
        )

        self.col_hours = ScrollColumn("HORAS", 23, self.update_total_time)
        self.col_mins = ScrollColumn("MINUTOS", 59, self.update_total_time)
        self.col_secs = ScrollColumn("SEGUNDOS", 59, self.update_total_time)

        picker_layout.add_widget(self.col_hours)
        picker_layout.add_widget(self.col_mins)
        picker_layout.add_widget(self.col_secs)

        layout.add_widget(picker_layout)

        # Botões de Navegação Inferiores
        nav_box = GridLayout(cols=4, spacing=10, size_hint_y=0.25)

        btn_ok = Button(
            text="INICIAR",
            background_color=(0, 0.7, 0.2, 1),
            font_size="18sp",
            bold=True,
        )
        btn_ok.bind(on_release=self.start_timer)

        btn_s = Button(
            text="[ S ] Voltar", background_color=(0.8, 0.4, 0, 1)
        )
        btn_s.bind(
            on_release=lambda x: setattr(
                self.manager, "current", "action_menu"
            )
        )

        btn_f = Button(
            text="[ F ] Painel", background_color=(0.3, 0.3, 0.3, 1)
        )
        btn_f.bind(
            on_release=lambda x: setattr(self.manager, "current", "main_menu")
        )

        btn_t = Button(
            text="[ T ] Sair", background_color=(0.8, 0.1, 0.1, 1)
        )
        btn_t.bind(on_release=lambda x: App.get_running_app().stop())

        nav_box.add_widget(btn_ok)
        nav_box.add_widget(btn_s)
        nav_box.add_widget(btn_f)
        nav_box.add_widget(btn_t)

        layout.add_widget(nav_box)
        self.add_widget(layout)

    def update_total_time(self):
        h = self.col_hours.selected_val
        m = self.col_mins.selected_val
        s = self.col_secs.selected_val
        self.lbl_time_display.text = f"{h:02d}:{m:02d}:{s:02d}"

    def get_selected_seconds(self):
        return (
            (self.col_hours.selected_val * 3600)
            + (self.col_mins.selected_val * 60)
            + self.col_secs.selected_val
        )

    def start_timer(self, instance):
        total_sec = self.get_selected_seconds()
        if total_sec > 0:
            timer_screen = self.manager.get_screen("timer")
            timer_screen.start_timer(total_sec, self.action_id)
            self.manager.current = "timer"


# --- ECRÃ 4: TEMPORIZADOR EM CONTAGEM ---
class TimerScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_seconds = 0
        self.initial_time = 0
        self.paused = False
        self.event = None

        layout = BoxLayout(
            orientation="vertical", padding=15, spacing=10
        )
        set_bg_color(layout, 0.05, 0.05, 0.05)

        self.lbl_header = Label(
            text="CONTAGEM DECRESCENTE",
            font_size="20sp",
            bold=True,
            color=(1, 0.8, 0.2, 1),
            size_hint_y=0.15,
        )
        layout.add_widget(self.lbl_header)

        self.lbl_time = Label(
            text="00:00",
            font_size="75sp",
            bold=True,
            color=(1, 0.15, 0.15, 1),
            size_hint_y=0.55,
        )
        layout.add_widget(self.lbl_time)

        controls = GridLayout(cols=6, spacing=8, size_hint_y=0.3)

        btn_p = Button(
            text="[ P ] Pausa", background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_p.bind(on_release=self.toggle_pause)

        btn_r = Button(
            text="[ R ] Reiniciar", background_color=(0.8, 0.5, 0, 1)
        )
        btn_r.bind(on_release=self.restart_timer)

        btn_s = Button(
            text="[ S ] Tempo", background_color=(0.3, 0.6, 0.3, 1)
        )
        btn_s.bind(
            on_release=lambda x: self.stop_and_navigate("time_input")
        )

        btn_v = Button(
            text="[ V ] Função", background_color=(0.6, 0.4, 0.2, 1)
        )
        btn_v.bind(
            on_release=lambda x: self.stop_and_navigate("action_menu")
        )

        btn_f = Button(
            text="[ F ] Painel", background_color=(0.3, 0.3, 0.3, 1)
        )
        btn_f.bind(on_release=lambda x: self.stop_and_navigate("main_menu"))

        btn_t = Button(
            text="[ T ] Sair", background_color=(0.8, 0.1, 0.1, 1)
        )
        btn_t.bind(on_release=lambda x: App.get_running_app().stop())

        for b in [btn_p, btn_r, btn_s, btn_v, btn_f, btn_t]:
            controls.add_widget(b)

        layout.add_widget(controls)
        self.add_widget(layout)

    def start_timer(self, seconds, action_id):
        self.total_seconds = seconds
        self.initial_time = seconds
        self.paused = False
        self.update_display()

        if self.event:
            self.event.cancel()
        self.event = Clock.schedule_interval(self.tick, 1)

    def tick(self, dt):
        if not self.paused:
            if self.total_seconds > 0:
                self.total_seconds -= 1
                self.update_display()
            else:
                self.lbl_time.text = "FIM!"
                if self.event:
                    self.event.cancel()

    def update_display(self):
        hrs, rem = divmod(self.total_seconds, 3600)
        mins, secs = divmod(rem, 60)
        if hrs > 0:
            self.lbl_time.text = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        else:
            self.lbl_time.text = f"{mins:02d}:{secs:02d}"

    def toggle_pause(self, instance):
        self.paused = not self.paused
        self.lbl_header.text = (
            "[ PAUSADO ]" if self.paused else "CONTAGEM DECRESCENTE"
        )

    def restart_timer(self, instance):
        self.total_seconds = self.initial_time
        self.paused = False
        self.update_display()

    def stop_and_navigate(self, screen_name):
        if self.event:
            self.event.cancel()
        self.manager.current = screen_name


# --- APLICAÇÃO PRINCIPAL ---
class GoldaziTimerApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(ActionMenuScreen(name="action_menu"))
        sm.add_widget(TimeInputScreen(name="time_input"))
        sm.add_widget(TimerScreen(name="timer"))
        return sm


if __name__ == "__main__":
    GoldaziTimerApp().run()
