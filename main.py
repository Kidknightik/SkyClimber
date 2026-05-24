import pygame
import sys
import math
import random

screenw = 960
screenh = 540
fps = 60

white = (255, 255, 255)
black = (0, 0, 0)
skycolor1 = (18, 18, 55)
skycolor2 = (55, 25, 75)
playercolor = (220, 100, 150)
dashcolor = (150, 180, 255)
platcolor = (95, 195, 145)
platedge = (65, 150, 105)
spikecolor = (210, 75, 75)
goalcolor = (255, 220, 50)
starcolor = (255, 255, 210)
trailcolor = (175, 135, 215)
textcolor = (235, 235, 255)
deathcolor = (255, 60, 60)
hintcolor = (170, 170, 195)
goldcolor = (255, 200, 0)
silvercolor = (180, 180, 180)

gravity = 0.45
maxfall = 14.0
movespeed = 4.5
minjump = -5.0
maxjump = -13.0
jumpholdmax = 14
dashspeed = 13.0
dashtime = 12
coyotetime = 6
jumpbuffer = 8

level1 = {}
level1["start"] = (50, 460)
level1["goal"] = (820, 130, 28, 40)
level1["spikes"] = []
level1["spikes"].append((290, 500, 60, 10))
level1["spikes"].append((490, 500, 60, 10))
level1["platforms"] = []
level1["platforms"].append((0, 510, 960, 30))
level1["platforms"].append((180, 415, 140, 18))
level1["platforms"].append((370, 335, 140, 18))
level1["platforms"].append((560, 255, 140, 18))
level1["platforms"].append((720, 170, 180, 18))

level2 = {}
level2["start"] = (50, 460)
level2["goal"] = (880, 115, 28, 40)
level2["spikes"] = []
level2["spikes"].append((180, 500, 60, 10))
level2["spikes"].append((640, 500, 60, 10))
level2["platforms"] = []
level2["platforms"].append((0, 510, 180, 30))
level2["platforms"].append((240, 450, 90, 15))
level2["platforms"].append((390, 385, 90, 15))
level2["platforms"].append((540, 315, 90, 15))
level2["platforms"].append((390, 240, 90, 15))
level2["platforms"].append((240, 170, 90, 15))
level2["platforms"].append((90, 220, 90, 15))
level2["platforms"].append((40, 330, 90, 15))
level2["platforms"].append((800, 510, 160, 30))
level2["platforms"].append((690, 410, 90, 15))
level2["platforms"].append((590, 325, 90, 15))
level2["platforms"].append((710, 235, 90, 15))
level2["platforms"].append((840, 155, 130, 18))

level3 = {}
level3["start"] = (40, 460)
level3["goal"] = (870, 115, 28, 40)
level3["spikes"] = []
level3["spikes"].append((140, 500, 60, 10))
level3["platforms"] = []
level3["platforms"].append((0, 510, 140, 30))
level3["platforms"].append((200, 460, 75, 12))
level3["platforms"].append((320, 400, 75, 12))
level3["platforms"].append((440, 340, 75, 12))
level3["platforms"].append((560, 280, 75, 12))
level3["platforms"].append((680, 220, 75, 12))
level3["platforms"].append((800, 155, 75, 12))
level3["platforms"].append((860, 255, 75, 12))
level3["platforms"].append((780, 355, 75, 12))
level3["platforms"].append((660, 440, 75, 12))
level3["platforms"].append((280, 510, 680, 30))

levels = []
levels.append(level1)
levels.append(level2)
levels.append(level3)


class Player:
    pw = 20
    ph = 28

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.pw, self.ph)
        self.speedx = 0.0
        self.speedy = 0.0
        self.onground = False
        self.onwall = 0
        self.coyote = 0
        self.jumpbuf = 0
        self.dashes = 1
        self.dashframes = 0
        self.dashspeedx = 0.0
        self.dashspeedy = 0.0
        self.facing = 1
        self.trail = []
        self.dead = False
        self.jumpholding = False
        self.jumpframes = 0

    def startjump(self):
        self.jumpbuf = jumpbuffer

    def releasejump(self):
        self.jumpholding = False
        if self.speedy < minjump:
            self.speedy = minjump

    def dash(self, dx, dy):
        if self.dashes <= 0 or self.dashframes > 0:
            return
        self.dashes -= 1
        if dx == 0 and dy == 0:
            dx = self.facing
        dist = math.hypot(dx, dy)
        self.dashspeedx = dx / dist * dashspeed
        self.dashspeedy = dy / dist * dashspeed
        self.dashframes = dashtime

    def update(self, platlist, spikelist, goalrect):
        if self.dead:
            return None

        keys = pygame.key.get_pressed()

        jumpkey = keys[pygame.K_z] or keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]

        if self.dashframes > 0:
            self.dashframes -= 1
            self.speedx = self.dashspeedx
            self.speedy = self.dashspeedy
        else:
            goright = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            goleft = keys[pygame.K_LEFT] or keys[pygame.K_a]
            dx = int(bool(goright)) - int(bool(goleft))
            if dx != 0:
                self.facing = dx
            self.speedx = dx * movespeed
            if self.onwall and not self.onground and self.speedy > 0:
                self.speedy = min(self.speedy, 2.0)

            if self.jumpholding and self.jumpframes > 0 and self.speedy < 0:
                if jumpkey:
                    self.jumpframes -= 1
                else:
                    self.jumpholding = False
                    if self.speedy < minjump:
                        self.speedy = minjump

            self.speedy = min(self.speedy + gravity, maxfall)

        if self.onground:
            self.coyote = coyotetime
            self.dashes = 1
        elif self.coyote > 0:
            self.coyote -= 1

        if self.jumpbuf > 0:
            self.jumpbuf -= 1

        if self.jumpbuf > 0 and self.coyote > 0:
            self.speedy = maxjump
            self.coyote = 0
            self.jumpbuf = 0
            self.jumpholding = True
            self.jumpframes = jumpholdmax
        elif self.jumpbuf > 0 and self.onwall and not self.onground:
            self.speedy = maxjump
            self.speedx = -self.onwall * movespeed * 2
            self.jumpbuf = 0
            self.jumpholding = True
            self.jumpframes = jumpholdmax

        self.trail.append(self.rect.center)
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.rect.x += int(self.speedx)
        self.onwall = 0
        for p in platlist:
            if self.rect.colliderect(p):
                if self.speedx > 0:
                    self.rect.right = p.left
                    self.onwall = 1
                elif self.speedx < 0:
                    self.rect.left = p.right
                    self.onwall = -1
                self.speedx = 0

        self.rect.y += int(self.speedy)
        self.onground = False
        for p in platlist:
            if self.rect.colliderect(p):
                if self.speedy > 0:
                    self.rect.bottom = p.top
                    self.onground = True
                    self.dashframes = 0
                    self.jumpholding = False
                elif self.speedy < 0:
                    self.rect.top = p.bottom
                self.speedy = 0

        for s in spikelist:
            if self.rect.colliderect(s):
                self.dead = True
                return "dead"

        if self.rect.top > screenh + 60:
            self.dead = True
            return "dead"

        if self.rect.colliderect(goalrect):
            return "goal"

        return None


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screenw, screenh))
        pygame.display.set_caption("Sky Climber")
        self.makeicon()
        self.clock = pygame.time.Clock()

        self.bigfont = pygame.font.SysFont("Arial", 44, bold=True)
        self.midfont = pygame.font.SysFont("Arial", 26)
        self.smallfont = pygame.font.SysFont("Arial", 18)
        self.tinyfont = pygame.font.SysFont("Arial", 14)

        self.stars = []
        for i in range(120):
            sx = random.randint(0, screenw)
            sy = random.randint(0, screenh)
            self.stars.append((sx, sy))

        self.bg = self.makebg()

        self.state = "menu"
        self.levelnum = 0
        self.deaths = 0
        self.player = None
        self.platlist = []
        self.spikelist = []
        self.goalrect = None
        self.particles = []
        self.deathtimer = 0
        self.respawning = False

        self.starttime = 0
        self.totaltime = 0
        self.besttime = 0
        self.timerrunning = False

        self.leveltimes = []
        self.levelstarttime = 0
        self.bestleveltimes = []
        self.bestleveltimes.append(0)
        self.bestleveltimes.append(0)
        self.bestleveltimes.append(0)

    def makeicon(self):
        ico = pygame.Surface((32, 32))
        ico.fill((18, 18, 55))
        pygame.draw.rect(ico, playercolor, (9, 9, 12, 16))
        pygame.draw.circle(ico, goalcolor, (24, 8), 5)
        pygame.display.set_icon(ico)

    def makebg(self):
        surf = pygame.Surface((screenw, screenh))
        for y in range(screenh):
            t = y / screenh
            r = int(skycolor1[0] * (1 - t) + skycolor2[0] * t)
            g = int(skycolor1[1] * (1 - t) + skycolor2[1] * t)
            b = int(skycolor1[2] * (1 - t) + skycolor2[2] * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (screenw, y))
        for i in range(len(self.stars)):
            sx = self.stars[i][0]
            sy = self.stars[i][1]
            pygame.draw.circle(surf, starcolor, (sx, sy), 1)
        return surf

    def loadlevel(self, num):
        lv = levels[num]
        self.platlist = []
        for p in lv["platforms"]:
            self.platlist.append(pygame.Rect(p[0], p[1], p[2], p[3]))
        self.spikelist = []
        for s in lv["spikes"]:
            self.spikelist.append(pygame.Rect(s[0], s[1], s[2], s[3]))
        gx = lv["goal"][0]
        gy = lv["goal"][1]
        gw = lv["goal"][2]
        gh = lv["goal"][3]
        self.goalrect = pygame.Rect(gx, gy, gw, gh)
        sx = lv["start"][0]
        sy = lv["start"][1]
        self.player = Player(sx, sy)
        self.particles = []
        self.levelstarttime = pygame.time.get_ticks()

    def startgame(self):
        self.levelnum = 0
        self.deaths = 0
        self.respawning = False
        self.leveltimes = []
        self.starttime = pygame.time.get_ticks()
        self.timerrunning = True
        self.loadlevel(0)
        self.state = "play"

    def restartgame(self):
        self.startgame()

    def spawnparticles(self, x, y, color):
        for i in range(22):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 9)
            dot = {}
            dot["x"] = float(x)
            dot["y"] = float(y)
            dot["vx"] = math.cos(angle) * speed
            dot["vy"] = math.sin(angle) * speed - 2
            dot["life"] = random.randint(18, 38)
            dot["color"] = color
            self.particles.append(dot)

    def updateparticles(self):
        newlist = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.25
            p["life"] -= 1
            if p["life"] > 0:
                newlist.append(p)
        self.particles = newlist

    def drawparticles(self):
        for p in self.particles:
            alpha = p["life"] / 38
            r = int(5 * alpha)
            if r < 1:
                r = 1
            px = int(p["x"])
            py = int(p["y"])
            pygame.draw.circle(self.screen, p["color"], (px, py), r)

    def drawstarshape(self, cx, cy, rout, rin, color):
        pts = []
        for i in range(10):
            angle = math.pi / 5 * i - math.pi / 2
            if i % 2 == 0:
                r = rout
            else:
                r = rin
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            pts.append((px, py))
        pygame.draw.polygon(self.screen, color, pts)

    def drawplatforms(self):
        for p in self.platlist:
            pygame.draw.rect(self.screen, platcolor, p, border_radius=3)
            pygame.draw.rect(self.screen, platedge, p, 2, border_radius=3)
            pygame.draw.line(self.screen, white, (p.left + 3, p.top + 1), (p.right - 3, p.top + 1))

    def drawspikes(self):
        for s in self.spikelist:
            count = s.width // 10
            for i in range(count):
                x0 = s.left + i * 10
                pts = []
                pts.append((x0, s.bottom))
                pts.append((x0 + 5, s.top))
                pts.append((x0 + 10, s.bottom))
                pygame.draw.polygon(self.screen, spikecolor, pts)

    def drawgoal(self):
        t = pygame.time.get_ticks() / 600
        glow = int(abs(math.sin(t)) * 45)
        r = min(255, goalcolor[0] + glow)
        g = min(255, goalcolor[1] + glow // 2)
        b = 50
        col = (r, g, b)
        pygame.draw.rect(self.screen, col, self.goalrect, border_radius=5)
        pygame.draw.rect(self.screen, white, self.goalrect, 2, border_radius=5)
        self.drawstarshape(self.goalrect.centerx, self.goalrect.top - 13, 10, 4, goalcolor)

    def drawplayer(self):
        pl = self.player
        if pl.dead:
            return
        for i in range(len(pl.trail)):
            tx = pl.trail[i][0]
            ty = pl.trail[i][1]
            alpha = int(155 * i / max(len(pl.trail), 1))
            s = pygame.Surface((pl.pw, pl.ph), pygame.SRCALPHA)
            s.fill((trailcolor[0], trailcolor[1], trailcolor[2], alpha))
            self.screen.blit(s, (tx - pl.pw // 2, ty - pl.ph // 2))

        if pl.dashframes > 0:
            col = dashcolor
        else:
            col = playercolor
        pygame.draw.rect(self.screen, col, pl.rect, border_radius=5)

        if pl.facing > 0:
            ex = pl.rect.left + 13
        else:
            ex = pl.rect.left + 4
        ey = pl.rect.top + 8
        pygame.draw.circle(self.screen, white, (ex, ey), 3)
        pygame.draw.circle(self.screen, black, (ex + pl.facing, ey), 2)

        if pl.dashes > 0:
            pygame.draw.circle(self.screen, goalcolor, (pl.rect.centerx, pl.rect.bottom + 5), 4)

    def gettimestr(self, ms):
        if ms < 0:
            ms = 0
        secs = ms // 1000
        millis = (ms % 1000) // 10
        minutes = secs // 60
        secs = secs % 60
        return str(minutes) + ":" + str(secs).zfill(2) + "." + str(millis).zfill(2)

    def drawui(self):
        self.screen.blit(self.midfont.render("Deaths: " + str(self.deaths), True, deathcolor), (10, 8))
        self.screen.blit(self.smallfont.render("Level " + str(self.levelnum + 1) + " of " + str(len(levels)), True, textcolor), (10, 38))

        if self.player and not self.player.dead:
            if self.player.dashes > 0:
                self.screen.blit(self.smallfont.render("Dash: ready", True, goalcolor), (10, 60))
            else:
                self.screen.blit(self.smallfont.render("Dash: used", True, (130, 130, 130)), (10, 60))

        self.drawtimer()

        hint = self.tinyfont.render("WASD/Arrows: move  Z/Space: jump (hold=higher)  X/Shift: dash  R: restart", True, hintcolor)
        self.screen.blit(hint, (screenw // 2 - hint.get_width() // 2, screenh - 20))

    def drawtimer(self):
        if self.timerrunning:
            totalms = pygame.time.get_ticks() - self.starttime
            levelms = pygame.time.get_ticks() - self.levelstarttime
        else:
            totalms = self.totaltime
            levelms = 0

        panelx = screenw - 220
        panely = 6
        panelw = 214
        panelh = 90

        panel = pygame.Surface((panelw, panelh), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        self.screen.blit(panel, (panelx, panely))

        totalstr = self.gettimestr(totalms)
        totalsurf = self.midfont.render(totalstr, True, white)
        self.screen.blit(totalsurf, (panelx + panelw // 2 - totalsurf.get_width() // 2, panely + 6))

        if self.besttime > 0:
            beststr = self.gettimestr(self.besttime)
            bestsurf = self.tinyfont.render("PB: " + beststr, True, goldcolor)
            self.screen.blit(bestsurf, (panelx + panelw // 2 - bestsurf.get_width() // 2, panely + 34))

        if self.timerrunning:
            levelstr = self.gettimestr(levelms)
            lvlsurf = self.smallfont.render("Lvl: " + levelstr, True, hintcolor)
            self.screen.blit(lvlsurf, (panelx + panelw // 2 - lvlsurf.get_width() // 2, panely + 52))

        if len(self.leveltimes) > 0:
            splits = ""
            for i in range(len(self.leveltimes)):
                t = self.leveltimes[i]
                splits = splits + "L" + str(i + 1) + ": " + self.gettimestr(t) + "  "
            splitsurf = self.tinyfont.render(splits.strip(), True, silvercolor)
            self.screen.blit(splitsurf, (panelx + panelw // 2 - splitsurf.get_width() // 2, panely + 72))

    def drawmenu(self):
        self.screen.blit(self.bg, (0, 0))
        self.drawstarshape(screenw // 2, screenh // 2 - 130, 30, 12, goalcolor)

        title = self.bigfont.render("SKY CLIMBER", True, goalcolor)
        self.screen.blit(title, (screenw // 2 - title.get_width() // 2, screenh // 2 - 105))

        lines = []
        lines.append("Reach the star on each level!")
        lines.append("Hold jump longer = jump higher!")
        lines.append("Use dash (X / Shift) to fly over gaps.")

        for i in range(len(lines)):
            s = self.smallfont.render(lines[i], True, textcolor)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 - 42 + i * 24))

        if (pygame.time.get_ticks() // 550) % 2 == 1:
            s = self.midfont.render("Press ENTER to start", True, white)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 + 55))

        if self.besttime > 0:
            beststr = self.gettimestr(self.besttime)
            s = self.smallfont.render("PB: " + beststr, True, goldcolor)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 + 90))

            if len(self.bestleveltimes) > 0:
                splits = "Splits: "
                for i in range(len(levels)):
                    t = self.bestleveltimes[i]
                    if t > 0:
                        splits = splits + "L" + str(i + 1) + " " + self.gettimestr(t) + "  "
                sv = self.tinyfont.render(splits.strip(), True, silvercolor)
                self.screen.blit(sv, (screenw // 2 - sv.get_width() // 2, screenh // 2 + 115))

        ctrl = self.tinyfont.render("WASD/Arrows: move  |  Z/Space: jump (hold longer = higher)  |  X/Shift: dash  |  R: restart", True, hintcolor)
        self.screen.blit(ctrl, (screenw // 2 - ctrl.get_width() // 2, screenh - 28))

    def drawwinscreen(self):
        self.screen.blit(self.bg, (0, 0))
        self.drawparticles()
        self.drawstarshape(screenw // 2, screenh // 2 - 100, 60, 25, goalcolor)

        t = self.bigfont.render("YOU WIN!", True, goalcolor)
        self.screen.blit(t, (screenw // 2 - t.get_width() // 2, screenh // 2 - 45))

        timestr = self.gettimestr(self.totaltime)
        d = self.midfont.render("Total: " + timestr + "   Deaths: " + str(self.deaths), True, white)
        self.screen.blit(d, (screenw // 2 - d.get_width() // 2, screenh // 2 + 10))

        if self.besttime > 0 and self.totaltime <= self.besttime:
            pb = self.smallfont.render("New PB!", True, goldcolor)
            self.screen.blit(pb, (screenw // 2 - pb.get_width() // 2, screenh // 2 + 42))

        if len(self.leveltimes) > 0:
            y = screenh // 2 + 68
            for i in range(len(self.leveltimes)):
                lt = self.leveltimes[i]
                bl = self.bestleveltimes[i]
                lstr = "Level " + str(i + 1) + ": " + self.gettimestr(lt)
                if bl > 0 and lt < bl:
                    lcolor = goldcolor
                    lstr = lstr + "  (best!)"
                elif bl > 0:
                    diff = lt - bl
                    lstr = lstr + "  (+" + self.gettimestr(diff) + ")"
                    lcolor = deathcolor
                else:
                    lcolor = silvercolor
                ls = self.smallfont.render(lstr, True, lcolor)
                self.screen.blit(ls, (screenw // 2 - ls.get_width() // 2, y))
                y += 26

        r = self.midfont.render("ENTER or R - play again", True, white)
        self.screen.blit(r, (screenw // 2 - r.get_width() // 2, screenh // 2 + 160))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_r:
                        if self.state == "play" or self.state == "win":
                            self.restartgame()

                    if self.state == "menu":
                        if event.key == pygame.K_RETURN:
                            self.startgame()

                    elif self.state == "win":
                        if event.key == pygame.K_RETURN:
                            self.startgame()

                    elif self.state == "play" and not self.respawning:
                        if event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.player.startjump()
                        if event.key == pygame.K_x or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            keys = pygame.key.get_pressed()
                            goright = keys[pygame.K_RIGHT] or keys[pygame.K_d]
                            goleft = keys[pygame.K_LEFT] or keys[pygame.K_a]
                            godown = keys[pygame.K_DOWN] or keys[pygame.K_s]
                            goup = keys[pygame.K_UP] or keys[pygame.K_w]
                            dx = int(bool(goright)) - int(bool(goleft))
                            dy = int(bool(godown)) - int(bool(goup))
                            self.player.dash(dx, dy)

                if event.type == pygame.KEYUP:
                    if self.state == "play":
                        if event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                            if self.player != None:
                                self.player.releasejump()

            if self.state == "play":
                self.updateparticles()

                if self.respawning:
                    self.deathtimer -= 1
                    if self.deathtimer <= 0:
                        self.loadlevel(self.levelnum)
                        self.respawning = False
                else:
                    result = self.player.update(self.platlist, self.spikelist, self.goalrect)
                    if result == "dead":
                        self.deaths += 1
                        self.spawnparticles(self.player.rect.centerx, self.player.rect.centery, playercolor)
                        self.respawning = True
                        self.deathtimer = 42
                        self.levelstarttime = pygame.time.get_ticks()
                    elif result == "goal":
                        self.spawnparticles(self.goalrect.centerx, self.goalrect.centery, goalcolor)

                        leveltime = pygame.time.get_ticks() - self.levelstarttime
                        self.leveltimes.append(leveltime)

                        if self.bestleveltimes[self.levelnum] == 0 or leveltime < self.bestleveltimes[self.levelnum]:
                            self.bestleveltimes[self.levelnum] = leveltime

                        self.levelnum += 1
                        if self.levelnum >= len(levels):
                            self.totaltime = pygame.time.get_ticks() - self.starttime
                            self.timerrunning = False
                            if self.besttime == 0 or self.totaltime < self.besttime:
                                self.besttime = self.totaltime
                            self.state = "win"
                        else:
                            self.loadlevel(self.levelnum)

            if self.state == "menu":
                self.drawmenu()
            elif self.state == "win":
                self.drawwinscreen()
            elif self.state == "play":
                self.screen.blit(self.bg, (0, 0))
                self.drawplatforms()
                self.drawspikes()
                self.drawgoal()
                self.drawplayer()
                self.drawparticles()
                self.drawui()

                if self.respawning and self.deathtimer > 20:
                    xtext = self.bigfont.render("X", True, deathcolor)
                    self.screen.blit(xtext, (screenw // 2 - xtext.get_width() // 2, screenh // 2 - 30))

            pygame.display.flip()
            self.clock.tick(fps)


game = Game()
game.run()
