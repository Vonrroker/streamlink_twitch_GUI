from kivy.config import Config

Config.set('graphics', 'window_state', 'maximized')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
from credencial import cred
from os import system
from subprocess import Popen, check_output


class BoxMain(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = PopUpProgress()
        self.hand_area = [[self.ids.btn_atualizar.size, self.ids.btn_atualizar.pos],
                          [self.ids.dwup.size, self.ids.dwup.pos],
                          [self.ids.chkauto.size, self.ids.chkauto.pos]
                          ]
        self.atualizar()
        Window.bind(mouse_pos=self.set_cursor)
        Window.bind(on_key_down=self.move)

    def move(self, *args):
        if args[1] == 274 and self.ids.scr.scroll_y > 0:
            self.ids.scr.scroll_y = self.ids.scr.scroll_y - 0.05
        elif args[1] == 273 and self.ids.scr.scroll_y < 1:
            self.ids.scr.scroll_y = self.ids.scr.scroll_y + 0.05

    def set_cursor(self, *args):
        pos_x = args[1][0]
        pos_y = args[1][1]
        is_area = [self.hand_area[i][1][0] < pos_x < (self.hand_area[i][0][0] + self.hand_area[i][1][0]) and
                   (self.hand_area[i][0][1] + self.hand_area[i][1][1]) > pos_y > self.hand_area[i][1][1]
                   for i in range(len(self.hand_area))
                   ]
        if any(is_area):
            Window.set_system_cursor('hand')
        else:
            Window.set_system_cursor('arrow')

    def atualizar(self):
        """
    Carrega na tela a imagem preview, Nome, nº de viewers e jogo de todos as streams ao vivo
    que você segue.
        """
        on_streans = UrlRequest(url='https://api.twitch.tv/kraken/streams/followed',
                                req_headers={'Accept': 'application/vnd.twitchtv.v5+json',
                                             'Client-ID': cred['client_id'],
                                             'Authorization': f'OAuth {cred["oauth_token"]}'
                                             }
                                )
        on_streans.wait()
        self.streams_on = [[x['channel']['name'],
                            x['game'],
                            x['viewers'],
                            x['channel']['status'],
                            x['preview']['large']
                            ]
                           for x in on_streans.result['streams']
                           ]
        self.ids.img1.clear_widgets()
        self.ids.img2.clear_widgets()
        for stream in self.streams_on:
            if self.streams_on.index(stream) % 2 == 0:
                self.ids.img1.add_widget(BoxImg(text=stream))
            else:
                self.ids.img2.add_widget(BoxImg(text=stream))

        if len(self.ids['img1'].children) > len(self.ids['img2'].children):
            self.ids.img2.add_widget(BoxLayout(size_hint_y=None, height=380))

    def play(self, go: str, qlt='best'):
        system('cls')
        if not self.ids.chkauto.active and qlt == 'best':
            resol = UrlRequest(url='https://api.twitch.tv/kraken/videos/followed?limit=90',
                               req_headers={'Accept': 'application/vnd.twitchtv.v5+json',
                                            'Client-ID': cred['client_id'],
                                            'Authorization': f'OAuth {cred["oauth_token"]}'
                                            }
                               )
            resol.wait()
            list_resol = next((x for x in resol.result['videos'] if
                               x['status'] == 'recording' and
                               x['channel']['name'] == go.lower()
                               ),
                              False
                              )
            self.popup_resol = PopUpResol(list(list_resol['resolutions'].keys())[:-1], go)
            self.popup_resol.open()
        else:
            self.popup.open()
            try:
                self.popup_resol.dismiss()
            except UnboundLocalError:
                print('O popup escolha de resoluçoes nao foi criado ainda')
            tmp = f"streamlink http://twitch.tv/{go} {qlt}"
            print(tmp)
            Popen(tmp, close_fds=True)


class PopUpProgress(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vlcs = check_output('tasklist /nh /fi "IMAGENAME eq vlc.exe" /fo csv').count(b'vlc.exe')

    def on_open(self):
        Clock.schedule_interval(self.next, .06)

    def next(self, dt):
        if check_output('tasklist /nh /fi "IMAGENAME eq vlc.exe" /fo csv').count(b'vlc.exe') != self.vlcs:
            self.dismiss()
            return False
        self.ids.pgb.value += 1
        if self.ids.pgb.value >= 50:
            self.ids.pgb.value = 0


class PopUpResol(Popup):
    def __init__(self, list_spn, go, **kwargs):
        super().__init__(**kwargs)
        self.ids.spn.values = list_spn
        self.go = go


class BoxImg(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.t = text
        self.stream = text[0]
        self.ids.asimg.source = text[4]
        self.ids.lbl.text = "{} - {} - {:,}[ref={}][color=ff0000]...[/color][/ref]".format(text[0].capitalize(),
                                                                                           text[1],
                                                                                           text[2],
                                                                                           text[0]).replace(',', '.')

    def info(self):
        if self.t[3] in self.ids.lbl.text:
            self.ids.lbl.text = self.ids.lbl.text.replace(self.t[3], '').replace('\n\n', '')
        else:
            self.ids.lbl.text += f'\n\n [color=ffc125]{self.t[3]}[/color]'


class Layout(App):
    title = 'Streams no VLC'

    def build(self):
        self.icon = 'twitch_PNG53.png'
        return BoxMain()


if __name__ == '__main__':
    Layout().run()
