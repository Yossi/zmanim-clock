import datetime
import math
try:
    import weather
except ImportError:
    print('weather unavailable')
import pygame
import pygame.gfxdraw
import pygame_textinput
import bisect
import zmanim
from pyluach import dates, parshios
from settings import zipcode
import argparse



translations = {'Dawn (Alot Hashachar) ': 'עלות השחר'[::-1],
                'Dawn (Alot Hashachar) | Fast Begins ': 'עלות השחר - צום מתחיל'[::-1],
                'Earliest Tallit and Tefillin (Misheyakir) ': 'משיכיר'[::-1],
                'Earliest Tallit (Misheyakir) ': 'משיכיר'[::-1],
                'Sunrise (Hanetz Hachamah) ': 'הנץ החמה'[::-1],
                'Latest Shema ': 'סוף זמן קריאת שמע'[::-1],
                'Latest Shacharit ': 'סוף זמן תפילה'[::-1],
# Finish Eating Chametz before
# Sell and Burn Chametz before
# Nullify Chametz before
                'Midday (Chatzot Hayom) ': 'חצות היום'[::-1],
                'Earliest Mincha (Mincha Gedolah) ': 'מנחה גדולה'[::-1],
                'Mincha Ketanah (“Small Mincha”) ': 'מנחה קטנה'[::-1],
                'Plag Hamincha (“Half of Mincha”) ': 'פלג המנחה'[::-1],
                'Plag Hamincha (“Half of Mincha”) | Earliest time to kindle Chanukah Menorah ': 'פלג המנחה - מנורה'[::-1],
                'Candle Lighting ': 'הדלקת נרות'[::-1],
                'Candle Lighting | Fast Begins ': 'הדלקת נרות - צום מתחיל'[::-1],
                'Sunset (Shkiah) ': 'שקיעת החמה'[::-1],
                'Sunset (Shkiah) | Fast Begins ': 'שקיעת החמה - צום מתחיל'[::-1],
                'Sunset (Shkiah) | Earliest time to kindle Chanukah Menorah ': 'שקיעת החמה - מנורה'[::-1],
                'Candle Lighting after ': 'הדלקת נרות אחרי'[::-1],
                'Shabbat Ends ': 'מוצאי שבת'[::-1],
                'Shabbat Ends | Earliest time to kindle Chanukah Menorah ': 'מוצאי שבת - מנורה'[::-1],
                'Holiday Ends ': 'מוצאי יום טוב'[::-1],
                'Shabbat/Holiday Ends ': 'מוצאי שבת ויום טוב'[::-1],
                'Shabbat/Holiday/Fast Ends ': 'מוצאי שבת ויום טוב - צום נגמר'[::-1],
                'Holiday/Fast Ends ': 'מוצאי יום טוב - צום נגמר'[::-1],
                'Nightfall (Tzeit Hakochavim) ': 'צאת הכוכבים'[::-1],
                'Nightfall (Tzeit Hakochavim) | Fast Ends ': 'צאת הכוכבים - צום נגמר'[::-1],
                'Midnight (Chatzot HaLailah) ': 'חצות לילה'[::-1],
                'Shaah Zmanit (proportional hour) ': 'שעה זמנית'[::-1]
}

class Clock():
    def __init__(self, window_size=(960,540), do_weather=False, hide_mouse=False):
        self.BG_COLOR = (64,64,64) # greyish
        self.TEXT_COLOR = (0,255,0) # green
        self.DAY_COLOR = '#FCF5E5' # off white
        self.NIGHT_COLOR = '#546BAB' # darkish blue
        self.CLOCK_TICK_COLOR = (0,0,0) # black
        self.CLOCK_HOUR_COLOR = (0,0,0) # black
        self.CLOCK_MINUTE_COLOR = (0,0,0) # black
        self.DIAL_TICK_COLOR = (0,0,0) # black
        self.ZMAN_TICK_COLOR = (255,0,0) # red
        self.DIAL_HOUR_COLOR = (0,0,0) # black
        self.CLEAR_WEATHER_COLOR = (0,255,0) # green
        self.PRECIPITATION_COLOR = (255,0,0) # red
        self.PIP_COLOR = (255,255,255) # white

        self.do_weather = do_weather

        self.page_number_value = ''

        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        self.tickclock = pygame.time.Clock()
        pygame.mouse.set_visible(not hide_mouse)

        self.xmax = pygame.display.Info().current_w
        self.ymax = pygame.display.Info().current_h

        self.font = pygame.font.Font('NotoSansHebrew.ttf', int(self.ymax/40))
        self.bigfont = pygame.font.Font('NotoSansHebrew.ttf', int(self.ymax/2.5))

        self.manager = pygame_textinput.TextInputManager(validator = lambda input: set(input) <= set('0123456789'))
        self.page_number_text = pygame_textinput.TextInputVisualizer()
        self.page_number_text.manager=self.manager
        self.page_number_text.font_object=self.bigfont
        self.page_number_text.font_color = self.TEXT_COLOR
        self.page_number_text.cursor_width = 0


        self.quarter_screen = self.xmax / 4
        self.clock_rect = pygame.Rect((self.quarter_screen*.2, self.quarter_screen*.2), (self.quarter_screen*.8, self.quarter_screen*.8))
        self.zman_dial_rect = pygame.Rect((self.quarter_screen*2, self.quarter_screen*.2), (self.quarter_screen*2*.8, self.quarter_screen*.8))
        self.minutecast_rect = pygame.Rect((0, 0), (self.xmax, self.ymax/50))
        self.zmanim_list_rect = pygame.Rect((0, self.ymax/50), (0, 0))


    def drawLineWidth(self, surface, color, p1, p2, width):
        # from https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line

        # delta vector
        d = (p2[0] - p1[0], p2[1] - p1[1])

        # distance between the points
        dis = math.hypot(*d)

        # # normalized vector
        # n = (d[0]/dis, d[1]/dis)

        # # perpendicular vector
        # p = (-n[1], n[0])

        # # scaled perpendicular vector (vector from p1 & p2 to the polygon's points)
        # sp = (p[0]*width/2, p[1]*width/2)

        sp = (-d[1]*width/(2*dis), d[0]*width/(2*dis))

        # points
        p1_1 = (p1[0] - sp[0], p1[1] - sp[1])
        p1_2 = (p1[0] + sp[0], p1[1] + sp[1])
        p2_1 = (p2[0] - sp[0], p2[1] - sp[1])
        p2_2 = (p2[0] + sp[0], p2[1] + sp[1])

        # draw the polygon
        pygame.gfxdraw.aapolygon(surface, (p1_1, p1_2, p2_2, p2_1), color)
        pygame.gfxdraw.filled_polygon(surface, (p1_1, p1_2, p2_2, p2_1), color)


    def get_page_number_value(self, events):
        try:
            self.page_number_value = int(self.page_number_text.value)
            if not self.page_number_value:
                self.page_number_text.value = ''
        except ValueError:
            self.page_number_value = ''

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                print(event.unicode)

            if event.type == pygame.KEYDOWN and event.unicode == '+':
                if self.page_number_value:
                    self.page_number_value += 1
                self.page_number_text.value = str(self.page_number_value)

            if event.type == pygame.KEYDOWN and event.unicode == '-':
                if self.page_number_value:
                    self.page_number_value -= 1
                if not self.page_number_value:
                    self.page_number_value = ''
                self.page_number_text.value = str(self.page_number_value)

        self.page_number_text.update(events)


    def clock(self, hour, minute):
        clock = pygame.Surface(self.clock_rect.size)
        clock.fill(self.BG_COLOR)
        clock.set_colorkey(self.BG_COLOR)
        center_x, center_y = clock.get_width()/2, clock.get_height()/2
        radius = center_x
        pygame.draw.circle(clock, self.DAY_COLOR, (center_x, center_y), radius)

        for tick in range(0, 12):
            θ = tick * math.pi/6
            edge_x = radius * math.sin(θ)
            edge_y = radius * -math.cos(θ)
            pygame.draw.aaline(clock, self.CLOCK_TICK_COLOR, (center_x + edge_x*.8, center_y + edge_y*.8), (center_x + edge_x*.95, center_y + edge_y*.95))

        θ = hour * math.pi/6 + minute * math.pi/360
        edge_x = radius * math.sin(θ)
        edge_y = radius * -math.cos(θ)
        self.drawLineWidth(clock, self.CLOCK_HOUR_COLOR, (center_x, center_y), (center_x + edge_x*.6, center_y + edge_y*.6), 7) # hour
        pygame.draw.circle(clock, self.CLOCK_HOUR_COLOR, (center_x + edge_x*.6, center_y + edge_y*.6), 7/2)

        θ = minute * math.pi/30
        edge_x = radius * math.sin(θ)
        edge_y = radius * -math.cos(θ)
        self.drawLineWidth(clock, self.CLOCK_MINUTE_COLOR, (center_x, center_y), (center_x + edge_x*.75, center_y + edge_y*.75), 5) # minute
        pygame.draw.circle(clock, self.CLOCK_MINUTE_COLOR, (center_x + edge_x*.75, center_y + edge_y*.75), 5/2)

        return clock


    def zman_dial(self, zman_time):
        dial = pygame.Surface(self.zman_dial_rect.size)
        dial.fill(self.BG_COLOR)
        dial.set_colorkey(self.BG_COLOR)
        center_x, center_y = dial.get_width()/2, dial.get_height()
        radius = center_x
        center_y -= 1
        pygame.draw.circle(dial, (self.DAY_COLOR if 6 < zman_time['hour'] < 18 else self.NIGHT_COLOR), (center_x, center_y), radius)

        for tick in range(0, 13):
            θ = tick * math.pi/12
            edge_x = -radius * math.cos(θ)
            edge_y = -radius * math.sin(θ)
            pygame.draw.aaline(dial, self.DIAL_TICK_COLOR, (center_x + edge_x*.85, center_y + edge_y*.85), (center_x + edge_x*.98, center_y + edge_y*.98))

        for red_tick in (0, 3, 4, 6, 6.5, 9.5, 10.75, 12) if 6 < zman_time['hour'] < 18 else (0, 0.5, 6, 10, 11, 12):
            θ = red_tick * math.pi/12
            edge_x = -radius * math.cos(θ)
            edge_y = -radius * math.sin(θ)
            self.drawLineWidth(dial, self.ZMAN_TICK_COLOR, (center_x + edge_x*.90, center_y + edge_y*.90), (center_x + edge_x*.98, center_y + edge_y*.98), 2)

        θ = ((18+zman_time['hour'])%12 + zman_time['minute']/60) * math.pi/12
        edge_x = -radius * math.cos(θ)
        edge_y = -radius * math.sin(θ)
        self.drawLineWidth(dial, self.DIAL_HOUR_COLOR, (center_x, center_y), (center_x + edge_x*.7, center_y + edge_y*.7), 7)
        pygame.draw.circle(dial, self.DIAL_HOUR_COLOR, (center_x + edge_x*.7, center_y + edge_y*.7), 7/2)

        return dial


    def minutecast(self, weather_data):
        minutecast = pygame.Surface(self.minutecast_rect.size)
        minutecast.fill(self.BG_COLOR)
        minutecast.set_colorkey(self.BG_COLOR)

        minute_width = self.minutecast_rect.width//120

        clear = pygame.Surface((minute_width-1, self.minutecast_rect.height-2))
        clear.fill(self.CLEAR_WEATHER_COLOR)
        rain = pygame.Surface((minute_width-1, self.minutecast_rect.height-2))
        rain.fill(self.PRECIPITATION_COLOR)
        dot = pygame.Surface((1, 2))
        dot.fill(self.PIP_COLOR)

        for x, minute in enumerate(weather_data):
            forecast = clear if minute == '.' else rain
            minutecast.blit(forecast, (x*minute_width, 0))
            if not (x+1) % 15:
                minutecast.blit(dot, ((x+1)*minute_width-1, self.minutecast_rect.height-2))

        return minutecast


    def zmanim_list(self, zman_text):
        zmanim_list = [self.font.render(f'{translations.get(zman, zman).strip()} - {time.strip()}', True, self.TEXT_COLOR, self.BG_COLOR) for zman, time in zman_text.items()]
        zman_width = max(zmanim_list, key=lambda x: x.get_rect().width).get_rect().width
        zman_height = self.font.get_linesize() * len(zmanim_list)
        self.zmanim_list_rect.update(self.zmanim_list_rect.topleft, (zman_width, zman_height))
        zmanim_text = pygame.Surface(self.zmanim_list_rect.size)
        zmanim_text.fill(self.BG_COLOR)
        zmanim_text.set_colorkey(self.BG_COLOR)
        zmanim_text.blits(
            ((line, ((zman_width-line.get_rect().width)/2, self.font.get_linesize()*n)) for n, line in enumerate(zmanim_list))
        )

        return zmanim_text


    def clock_text(self, datetime_string):
        clock_text = self.font.render(datetime_string, True, self.TEXT_COLOR, self.BG_COLOR)
        clock_text.set_colorkey(self.BG_COLOR)
        self.clock_text_rect = clock_text.get_rect()

        return clock_text


    def date_text(self, zman_string):
        date_text = self.font.render(zman_string[::-1], True, self.TEXT_COLOR, self.BG_COLOR)
        date_text.set_colorkey(self.BG_COLOR)
        self.date_text_rect = date_text.get_rect()

        return date_text


    def assemble(self):
        if self.do_weather:
            weather_data = weather.get_weather()
            minutecast = self.minutecast(weather_data)
        else:
            minutecast = pygame.Surface((0,0))

        now = datetime.datetime.now()

        zman_text = zmanim.chabad_org(zipcode, datetime.datetime.today().strftime('%m/%d/%Y'))

        events = zmanim.get_events(zman_text)

        def parsha_string(day):
            parsha = parshios.getparsha_string(day, hebrew=True)
            if parsha:
                return f'{parsha} - '
            return ''

        today = dates.HebrewDate.today()
        today_zman_string = f'{parsha_string(today)}{today:%*A - %*d %*B}'
        tomorrow = today + 1
        tomorrow_zman_string = f'{parsha_string(tomorrow)}{tomorrow:%*A - %*d %*B}'

        if now.time() < events[(18,00)].time():
            zman_string = today_zman_string
        elif events[(18,00)].time() < now.time() < events[(18,30)].time():
            zman_string = today_zman_string + ' < ' + tomorrow_zman_string
        elif events[(18,30)].time() < now.time():
            zman_string = tomorrow_zman_string


        zman_lookup = zmanim.get_times(zipcode, datetime.datetime.today().strftime('%m/%d/%Y'))
        keys = list(zman_lookup.keys())
        next_key_index = bisect.bisect_right(keys, now.strftime('%H:%M:%S'))
        next_time = keys[next_key_index] if next_key_index < len(keys) else keys[0]

        zman_time = zman_lookup[next_time]

        self.screen.fill(self.BG_COLOR)


        clock = self.clock(hour=now.hour, minute=now.minute)
        zman_dial = self.zman_dial(zman_time)

        zmanim_list = self.zmanim_list(zman_text)


        width_spacing = (self.screen.get_width() - clock.get_width() - zmanim_list.get_width() - zman_dial.get_width())/4
        self.clock_rect.x = width_spacing
        self.zmanim_list_rect.x = width_spacing*2 + self.clock_rect.width
        self.zman_dial_rect.x = width_spacing*3 + self.clock_rect.width + self.zmanim_list_rect.width


        clock_text = self.clock_text(now.strftime("%A %m/%d/%Y, %I:%M:%S %p"))
        self.clock_text_rect.move_ip(self.clock_rect.centerx-(self.clock_text_rect.width)/2,
                                    (self.clock_rect.top - self.minutecast_rect.bottom - self.font.get_linesize())/2 + self.minutecast_rect.bottom)

        date_text = self.date_text(zman_string)
        self.date_text_rect.move_ip(self.zman_dial_rect.centerx-(self.date_text_rect.width)/2,
                                   (self.zman_dial_rect.top - self.minutecast_rect.bottom - self.font.get_linesize())/2 + self.minutecast_rect.bottom)


        page_text = self.page_number_text.surface
        page_text_rect = page_text.get_rect()
        page_text_rect.move_ip(self.xmax/2 - page_text_rect.centerx,
                               self.ymax - self.bigfont.get_linesize())


        self.screen.blits((
            (clock, self.clock_rect),
            (zman_dial, self.zman_dial_rect),
            (minutecast, self.minutecast_rect),
            (clock_text, self.clock_text_rect),
            (date_text, self.date_text_rect),
            (zmanim_list, self.zmanim_list_rect),
            (page_text, page_text_rect)
        ))

        pygame.display.flip()


    def run(self):
        self.running = True

        while self.running:
            events = pygame.event.get()

            self.get_page_number_value(events)

            self.assemble()
            self.tickclock.tick(5) # make this be 1/60 for an update every minute only


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', nargs=2, type=int, default=(960,540))
    parser.add_argument('-w', '--weather', action='store_true', help='hit minutecast api for weather predictions')
    parser.add_argument('-m', '--mouse', action='store_true', help='hide mouse pointer')
    args = parser.parse_args()

    c = Clock(args.resolution, args.weather, args.mouse)
    c.run()
