#importing libary's
import pygame
import sys
import math
import random
import json
import os
import datetime

#setting up a virables
#screen size and fps
screenw = 960
screenh = 540
fps = 60

#colors for everything in the game
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

#physics and movement settings
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

#save file sits next to the .exe when frozen, next to main.py otherwise
if getattr(sys, "frozen", False):
    basedir = os.path.dirname(sys.executable)
else:
    basedir = os.path.dirname(os.path.abspath(__file__))
savefile = os.path.join(basedir, "saves.json")


#creating a levels.
#1 level
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

#2nd level
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

#3 level
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

#putting all levels into one list
levels = []
levels.append(level1)
levels.append(level2)
levels.append(level3)


#creating a player with an argument.
class Player:
    #player size in pixels
    pw = 20
    ph = 28

    def __init__(self, x, y):
        #hitbox of the player
        self.rect = pygame.Rect(x, y, self.pw, self.ph)
        #movement speed in x and y
        self.speedx = 0.0
        self.speedy = 0.0
        #state flags
        self.onground = False
        self.onwall = 0
        #timers for coyote time and jump buffer
        self.coyote = 0
        self.jumpbuf = 0
        #dash stuff
        self.dashes = 1
        self.dashframes = 0
        self.dashspeedx = 0.0
        self.dashspeedy = 0.0
        #direction player is looking
        self.facing = 1
        #trail positions for drawing
        self.trail = []
        self.dead = False
        #for variable height jump
        self.jumpholding = False
        self.jumpframes = 0

    #creating player function
    #jump function
    def startjump(self):
        #set jump buffer so jump registers even slightly before landing
        self.jumpbuf = jumpbuffer

    def releasejump(self):
        #stop holding jump and cut speed so short tap = low jump
        self.jumpholding = False
        if self.speedy < minjump:
            self.speedy = minjump

    def dash(self, dx, dy):
        #no dash available or already dashing - do nothing
        if self.dashes <= 0 or self.dashframes > 0:
            return
        self.dashes -= 1
        #dash straight forward if no direction pressed
        if dx == 0 and dy == 0:
            dx = self.facing
        #normalize direction and apply dash speed
        dist = math.hypot(dx, dy)
        self.dashspeedx = dx / dist * dashspeed
        self.dashspeedy = dy / dist * dashspeed
        self.dashframes = dashtime

    def update(self, platlist, spikelist, goalrect):
        #skip update if already dead
        if self.dead:
            return None

        keys = pygame.key.get_pressed()

        #any of these keys counts as jump held
        jumpkey = keys[pygame.K_z] or keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]

        if self.dashframes > 0:
            #during dash override speed with dash direction
            self.dashframes -= 1
            self.speedx = self.dashspeedx
            self.speedy = self.dashspeedy
        else:
            #normal movement
            goright = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            goleft = keys[pygame.K_LEFT] or keys[pygame.K_a]
            dx = int(bool(goright)) - int(bool(goleft))
            if dx != 0:
                self.facing = dx
            self.speedx = dx * movespeed
            #slow fall when touching wall (wall slide)
            if self.onwall and not self.onground and self.speedy > 0:
                self.speedy = min(self.speedy, 2.0)

            #variable jump height - holding key keeps going up longer
            if self.jumpholding and self.jumpframes > 0 and self.speedy < 0:
                if jumpkey:
                    self.jumpframes -= 1
                else:
                    self.jumpholding = False
                    if self.speedy < minjump:
                        self.speedy = minjump

            #apply gravity, cap at max fall speed
            self.speedy = min(self.speedy + gravity, maxfall)

        #reset coyote and dash when on ground
        if self.onground:
            self.coyote = coyotetime
            self.dashes = 1
        elif self.coyote > 0:
            self.coyote -= 1

        #count down jump buffer
        if self.jumpbuf > 0:
            self.jumpbuf -= 1

        #normal jump - buffer and coyote both active
        if self.jumpbuf > 0 and self.coyote > 0:
            self.speedy = maxjump
            self.coyote = 0
            self.jumpbuf = 0
            self.jumpholding = True
            self.jumpframes = jumpholdmax
        #wall jump - on wall, in air, buffer active
        elif self.jumpbuf > 0 and self.onwall and not self.onground:
            self.speedy = maxjump
            self.speedx = -self.onwall * movespeed * 2
            self.jumpbuf = 0
            self.jumpholding = True
            self.jumpframes = jumpholdmax

        #save position for trail effect
        self.trail.append(self.rect.center)
        if len(self.trail) > 8:
            self.trail.pop(0)

        #move horizontally and check wall collisions
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

        #move vertically and check floor/ceiling collisions
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

        #spike = instant death
        for s in spikelist:
            if self.rect.colliderect(s):
                self.dead = True
                return "dead"

        #fell off screen = dead
        if self.rect.top > screenh + 60:
            self.dead = True
            return "dead"

        #reached goal
        if self.rect.colliderect(goalrect):
            return "goal"

        return None


class Game:
    def __init__(self):
        #init pygame and create window
        pygame.init()
        self.screen = pygame.display.set_mode((screenw, screenh))
        pygame.display.set_caption("Sky Climber")
        self.makeicon()
        self.clock = pygame.time.Clock()

        #fonts for different text sizes
        self.bigfont = pygame.font.SysFont("Arial", 44, bold=True)
        self.midfont = pygame.font.SysFont("Arial", 26)
        self.smallfont = pygame.font.SysFont("Arial", 18)
        self.tinyfont = pygame.font.SysFont("Arial", 14)

        #random star positions for background
        self.stars = []
        for i in range(120):
            sx = random.randint(0, screenw)
            sy = random.randint(0, screenh)
            self.stars.append((sx, sy))

        #pre-render the background once so we dont redraw every frame
        self.bg = self.makebg()

        #game state machine
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

        #speedrun timer stuff
        self.starttime = 0
        self.totaltime = 0
        self.besttime = 0
        self.timerrunning = False

        #per-level split times
        self.leveltimes = []
        self.levelstarttime = 0
        self.bestleveltimes = []
        self.bestleveltimes.append(0)
        self.bestleveltimes.append(0)
        self.bestleveltimes.append(0)

        #run history loaded from saves.json
        self.runhistory = []
        self.loadsaves()

    def makeicon(self):
        #load logo.png as the window icon, fall back to drawn icon if file missing
        try:
            ico = pygame.image.load("logo.png")
            pygame.display.set_icon(ico)
        except:
            ico = pygame.Surface((32, 32))
            ico.fill((18, 18, 55))
            pygame.draw.rect(ico, playercolor, (9, 9, 12, 16))
            pygame.draw.circle(ico, goalcolor, (24, 8), 5)
            pygame.display.set_icon(ico)

    def makebg(self):
        #draw gradient sky line by line and put stars on top
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

    #--- save / load ---

    def loadsaves(self):
        #read saves.json and restore best times and run history
        try:
            with open(savefile, "r") as f:
                data = json.load(f)
            self.besttime = data.get("besttime", 0)
            bl = data.get("bestleveltimes", [0, 0, 0])
            #make sure list is always length 3
            while len(bl) < 3:
                bl.append(0)
            self.bestleveltimes = bl
            self.runhistory = data.get("runhistory", [])
        except:
            #no file yet or corrupted - start fresh
            self.besttime = 0
            self.bestleveltimes = [0, 0, 0]
            self.runhistory = []

    def savegame(self):
        #write best times and last 10 runs to saves.json after every completed run
        entry = {}
        entry["date"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        entry["totaltime"] = self.totaltime
        entry["deaths"] = self.deaths
        entry["splits"] = list(self.leveltimes)
        entry["pb"] = (self.totaltime == self.besttime)

        self.runhistory.append(entry)
        #keep only last 10 runs
        if len(self.runhistory) > 10:
            self.runhistory = self.runhistory[-10:]

        data = {}
        data["besttime"] = self.besttime
        data["bestleveltimes"] = self.bestleveltimes
        data["runhistory"] = self.runhistory

        try:
            with open(savefile, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def loadlevel(self, num):
        #load platforms, spikes, goal and spawn player for the given level
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
        #reset everything and begin from level 0
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
        #burst of 22 particles flying out in random directions
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
        #move particles, apply gravity, remove dead ones
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
        #draw each particle smaller and dimmer as life runs out
        for p in self.particles:
            alpha = p["life"] / 38
            r = int(5 * alpha)
            if r < 1:
                r = 1
            px = int(p["x"])
            py = int(p["y"])
            pygame.draw.circle(self.screen, p["color"], (px, py), r)

    def drawstarshape(self, cx, cy, rout, rin, color):
        #draw a 5-point star by alternating outer and inner radius points
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
        #green fill, darker border, white highlight line on top edge
        for p in self.platlist:
            pygame.draw.rect(self.screen, platcolor, p, border_radius=3)
            pygame.draw.rect(self.screen, platedge, p, 2, border_radius=3)
            pygame.draw.line(self.screen, white, (p.left + 3, p.top + 1), (p.right - 3, p.top + 1))

    def drawspikes(self):
        #draw triangles packed side by side to fill the spike zone
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
        #pulsing glow effect on the goal using sin wave
        t = pygame.time.get_ticks() / 600
        glow = int(abs(math.sin(t)) * 45)
        r = min(255, goalcolor[0] + glow)
        g = min(255, goalcolor[1] + glow // 2)
        b = 50
        col = (r, g, b)
        pygame.draw.rect(self.screen, col, self.goalrect, border_radius=5)
        pygame.draw.rect(self.screen, white, self.goalrect, 2, border_radius=5)
        #star shape floating above the goal rect
        self.drawstarshape(self.goalrect.centerx, self.goalrect.top - 13, 10, 4, goalcolor)

    def drawplayer(self):
        pl = self.player
        if pl.dead:
            return
        #draw ghost trail with increasing opacity for older positions
        for i in range(len(pl.trail)):
            tx = pl.trail[i][0]
            ty = pl.trail[i][1]
            alpha = int(155 * i / max(len(pl.trail), 1))
            s = pygame.Surface((pl.pw, pl.ph), pygame.SRCALPHA)
            s.fill((trailcolor[0], trailcolor[1], trailcolor[2], alpha))
            self.screen.blit(s, (tx - pl.pw // 2, ty - pl.ph // 2))

        #blue during dash, pink normally
        if pl.dashframes > 0:
            col = dashcolor
        else:
            col = playercolor
        pygame.draw.rect(self.screen, col, pl.rect, border_radius=5)

        #draw eye on correct side based on facing direction
        if pl.facing > 0:
            ex = pl.rect.left + 13
        else:
            ex = pl.rect.left + 4
        ey = pl.rect.top + 8
        pygame.draw.circle(self.screen, white, (ex, ey), 3)
        pygame.draw.circle(self.screen, black, (ex + pl.facing, ey), 2)

        #small dot below player shows dash is ready
        if pl.dashes > 0:
            pygame.draw.circle(self.screen, goalcolor, (pl.rect.centerx, pl.rect.bottom + 5), 4)

    def gettimestr(self, ms):
        #convert milliseconds to m:ss.mm string
        if ms < 0:
            ms = 0
        secs = ms // 1000
        millis = (ms % 1000) // 10
        minutes = secs // 60
        secs = secs % 60
        return str(minutes) + ":" + str(secs).zfill(2) + "." + str(millis).zfill(2)

    def drawui(self):
        #top left - death counter and level number
        self.screen.blit(self.midfont.render("Deaths: " + str(self.deaths), True, deathcolor), (10, 8))
        self.screen.blit(self.smallfont.render("Level " + str(self.levelnum + 1) + " of " + str(len(levels)), True, textcolor), (10, 38))

        #dash status indicator
        if self.player and not self.player.dead:
            if self.player.dashes > 0:
                self.screen.blit(self.smallfont.render("Dash: ready", True, goalcolor), (10, 60))
            else:
                self.screen.blit(self.smallfont.render("Dash: used", True, (130, 130, 130)), (10, 60))

        self.drawtimer()

        #controls hint at bottom of screen
        hint = self.tinyfont.render("WASD/Arrows: move  Z/Space: jump (hold=higher)  X/Shift: dash  R: restart", True, hintcolor)
        self.screen.blit(hint, (screenw // 2 - hint.get_width() // 2, screenh - 20))

    def drawtimer(self):
        #use live time while running, frozen time on win screen
        if self.timerrunning:
            totalms = pygame.time.get_ticks() - self.starttime
            levelms = pygame.time.get_ticks() - self.levelstarttime
        else:
            totalms = self.totaltime
            levelms = 0

        #semi-transparent panel in top-right corner
        panelx = screenw - 220
        panely = 6
        panelw = 214
        panelh = 90

        panel = pygame.Surface((panelw, panelh), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        self.screen.blit(panel, (panelx, panely))

        #total run time - big and centered
        totalstr = self.gettimestr(totalms)
        totalsurf = self.midfont.render(totalstr, True, white)
        self.screen.blit(totalsurf, (panelx + panelw // 2 - totalsurf.get_width() // 2, panely + 6))

        #personal best below if one exists
        if self.besttime > 0:
            beststr = self.gettimestr(self.besttime)
            bestsurf = self.tinyfont.render("PB: " + beststr, True, goldcolor)
            self.screen.blit(bestsurf, (panelx + panelw // 2 - bestsurf.get_width() // 2, panely + 34))

        #current level time
        if self.timerrunning:
            levelstr = self.gettimestr(levelms)
            lvlsurf = self.smallfont.render("Lvl: " + levelstr, True, hintcolor)
            self.screen.blit(lvlsurf, (panelx + panelw // 2 - lvlsurf.get_width() // 2, panely + 52))

        #completed level split times at the bottom of the panel
        if len(self.leveltimes) > 0:
            splits = ""
            for i in range(len(self.leveltimes)):
                t = self.leveltimes[i]
                splits = splits + "L" + str(i + 1) + ": " + self.gettimestr(t) + "  "
            splitsurf = self.tinyfont.render(splits.strip(), True, silvercolor)
            self.screen.blit(splitsurf, (panelx + panelw // 2 - splitsurf.get_width() // 2, panely + 72))

    def drawmenu(self):
        #background, big star, title
        self.screen.blit(self.bg, (0, 0))
        self.drawstarshape(screenw // 2, screenh // 2 - 130, 30, 12, goalcolor)

        title = self.bigfont.render("SKY CLIMBER", True, goalcolor)
        self.screen.blit(title, (screenw // 2 - title.get_width() // 2, screenh // 2 - 105))

        #tutorial hints in the middle
        lines = []
        lines.append("Reach the star on each level!")
        lines.append("Hold jump longer = jump higher!")
        lines.append("Use dash (X / Shift) to fly over gaps.")

        for i in range(len(lines)):
            s = self.smallfont.render(lines[i], True, textcolor)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 - 42 + i * 24))

        #blinking press enter text - toggles every 550ms
        if (pygame.time.get_ticks() // 550) % 2 == 1:
            s = self.midfont.render("Press ENTER to start", True, white)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 + 55))

        #show personal best if player has finished before
        if self.besttime > 0:
            beststr = self.gettimestr(self.besttime)
            s = self.smallfont.render("PB: " + beststr, True, goldcolor)
            self.screen.blit(s, (screenw // 2 - s.get_width() // 2, screenh // 2 + 90))

            #best split times per level
            if len(self.bestleveltimes) > 0:
                splits = "Splits: "
                for i in range(len(levels)):
                    t = self.bestleveltimes[i]
                    if t > 0:
                        splits = splits + "L" + str(i + 1) + " " + self.gettimestr(t) + "  "
                sv = self.tinyfont.render(splits.strip(), True, silvercolor)
                self.screen.blit(sv, (screenw // 2 - sv.get_width() // 2, screenh // 2 + 115))

        #last 3 runs from history shown on the right side of the menu
        if len(self.runhistory) > 0:
            hx = screenw - 210
            hy = 10
            hlabel = self.tinyfont.render("Last runs:", True, hintcolor)
            self.screen.blit(hlabel, (hx, hy))
            hy += 18
            #show most recent first
            shown = self.runhistory[-3:][::-1]
            for entry in shown:
                col = goldcolor if entry.get("pb") else silvercolor
                tstr = self.gettimestr(entry["totaltime"])
                line = entry["date"] + "  " + tstr + "  x" + str(entry["deaths"])
                ls = self.tinyfont.render(line, True, col)
                self.screen.blit(ls, (hx, hy))
                hy += 16

        ctrl = self.tinyfont.render("WASD/Arrows: move  |  Z/Space: jump (hold longer = higher)  |  X/Shift: dash  |  R: restart", True, hintcolor)
        self.screen.blit(ctrl, (screenw // 2 - ctrl.get_width() // 2, screenh - 28))

    def drawwinscreen(self):
        #win screen with big star and final stats
        self.screen.blit(self.bg, (0, 0))
        self.drawparticles()
        self.drawstarshape(screenw // 2, screenh // 2 - 100, 60, 25, goalcolor)

        t = self.bigfont.render("YOU WIN!", True, goalcolor)
        self.screen.blit(t, (screenw // 2 - t.get_width() // 2, screenh // 2 - 45))

        timestr = self.gettimestr(self.totaltime)
        d = self.midfont.render("Total: " + timestr + "   Deaths: " + str(self.deaths), True, white)
        self.screen.blit(d, (screenw // 2 - d.get_width() // 2, screenh // 2 + 10))

        #new PB banner if this run was faster
        if self.besttime > 0 and self.totaltime <= self.besttime:
            pb = self.smallfont.render("New PB!", True, goldcolor)
            self.screen.blit(pb, (screenw // 2 - pb.get_width() // 2, screenh // 2 + 42))

        #split comparison - gold if better than best, red if worse
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

        #run history table on the right of win screen - last 5 runs
        if len(self.runhistory) > 0:
            hx = screenw - 220
            hy = 10
            hlabel = self.smallfont.render("Run history:", True, hintcolor)
            self.screen.blit(hlabel, (hx, hy))
            hy += 22
            shown = self.runhistory[-5:][::-1]
            for entry in shown:
                col = goldcolor if entry.get("pb") else silvercolor
                tstr = self.gettimestr(entry["totaltime"])
                line1 = entry["date"] + "  " + tstr
                line2 = "deaths: " + str(entry["deaths"])
                #splits line
                spstr = ""
                for si in range(len(entry.get("splits", []))):
                    spstr = spstr + "L" + str(si + 1) + ":" + self.gettimestr(entry["splits"][si]) + " "
                ls1 = self.tinyfont.render(line1, True, col)
                ls2 = self.tinyfont.render(line2 + "  " + spstr.strip(), True, hintcolor)
                self.screen.blit(ls1, (hx, hy))
                hy += 14
                self.screen.blit(ls2, (hx, hy))
                hy += 18

        r = self.midfont.render("ENTER or R - play again", True, white)
        self.screen.blit(r, (screenw // 2 - r.get_width() // 2, screenh // 2 + 160))

    def run(self):
        #main game loop
        while True:
            #handle all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    #escape always quits
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    #R restarts from any state
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
                        #jump keys - just buffer the jump
                        if event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.player.startjump()
                        #dash - read direction at the moment of press
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
                    #releasing jump cuts the jump arc short
                    if self.state == "play":
                        if event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                            if self.player != None:
                                self.player.releasejump()

            if self.state == "play":
                self.updateparticles()

                if self.respawning:
                    #count down respawn delay then reload level
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

                        #save split time and update best if needed
                        leveltime = pygame.time.get_ticks() - self.levelstarttime
                        self.leveltimes.append(leveltime)

                        if self.bestleveltimes[self.levelnum] == 0 or leveltime < self.bestleveltimes[self.levelnum]:
                            self.bestleveltimes[self.levelnum] = leveltime

                        self.levelnum += 1
                        if self.levelnum >= len(levels):
                            #all levels done - go to win screen, update PB, auto-save
                            self.totaltime = pygame.time.get_ticks() - self.starttime
                            self.timerrunning = False
                            if self.besttime == 0 or self.totaltime < self.besttime:
                                self.besttime = self.totaltime
                            self.savegame()
                            self.state = "win"
                        else:
                            self.loadlevel(self.levelnum)

            #draw the right screen based on state
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

                #show big X for a moment after death
                if self.respawning and self.deathtimer > 20:
                    xtext = self.bigfont.render("X", True, deathcolor)
                    self.screen.blit(xtext, (screenw // 2 - xtext.get_width() // 2, screenh // 2 - 30))

            #push frame to screen and cap fps
            pygame.display.flip()
            self.clock.tick(fps)


game = Game()
game.run()
