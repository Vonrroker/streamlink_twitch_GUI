from contextlib import contextmanager
from kivy import lang
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from config import envs

from main import App

root_path = envs["root_path"]


@contextmanager
def touch(btn):
    t = UnitTestTouch(*btn)
    t.touch_down()
    yield
    t.touch_up()


@contextmanager
def window_loop():
    EventLoop.ensure_window()
    yield EventLoop.window.children[0]


class BoxGraphicUnitTest(GraphicUnitTest):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        app = App()

        app.kv_directory = f"{root_path}"
        app.kv_file = "app.kv"
        app.mod = "testing"
        app.load_kv()

        self.box = app.build()
        self.render(self.box)


class TestMyBox(BoxGraphicUnitTest):
    def test_start_raw_app(self):
        lang._delayed_start = None
        a = App()
        Clock.schedule_once(a.stop, 0.1)
        a.run()

    def test_criacao_componentes_iniciais(self):
        with window_loop() as window:
            assert window.children[0] == self.box.scrollview_streams
            assert window.children[0].children[0] == self.box.grid_streams
            assert (
                window.children[0].children[0].children[0]
                == self.box.grid_streams.children[0]
            )
            assert window.children[1].children[1].children[0] == self.box.checkbox_auto
            assert window.children[1].children[0] == self.box.button_bottomtop
            assert window.children[1].children[2] == self.box.button_refresh

    def test_press_downup_deve_rolar_tela_a_extremo_oposto(self):
        assert self.box.scrollview_streams.scroll_y == 1
        with touch(self.box.button_bottomtop.center):
            assert self.box.scrollview_streams.scroll_y == 0
        with touch(self.box.button_bottomtop.center):
            assert self.box.scrollview_streams.scroll_y == 1

    def test_press_icondownarrow_boximg_deve_mostrar_titulo_da_live(self):
        assert (
            self.box.grid_streams.children[0].label_channel_infos.text
            == "Name_20 - Nome do Jogo_20 - 0"
        )
        assert self.box.grid_streams.children[0].label_status.text == ""
        # with touch(self.box.grid_streams.children[0].button_show_status.center):
        #     assert self.box.grid_streams.children[0].label_status.text == "Título da live_13"