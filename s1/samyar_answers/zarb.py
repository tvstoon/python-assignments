import pygame, sys, os, math, random, time, sqlite3, array
from pathlib import Path

# ---------------------------------------------------------------------------
# INIT
# ---------------------------------------------------------------------------
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
try:
    pygame.mixer.init()
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False

WIDTH, HEIGHT = 1280, 720
FPS = 60

NAVY = (12, 20, 48)
ROYAL_BLUE = (30, 60, 140)
GOLD = (230, 180, 60)
PURPLE = (110, 60, 160)
EMERALD = (40, 140, 80)
RED = (200, 60, 60)
WHITE = (245, 245, 255)
GRAY = (90, 100, 120)
DARK = (20, 25, 40)
GREEN = (70, 200, 100)
LBLUE = (120, 180, 230)
BLACK = (0, 0, 0)
CREAM = (240, 230, 200)

RARITY_COLORS = {
    'Common': (150, 160, 180),
    'Rare': (80, 160, 230),
    'Epic': (170, 100, 230),
    'Legendary': (240, 180, 60),
}

# ---------------------------------------------------------------------------
# CARD DEFINITIONS
# ---------------------------------------------------------------------------
CARD_DEFS = {
    'squire':      {'name': 'Squire',        'rarity': 'Common',    'cost': 2, 'type': 'melee',    'hp': 100, 'dmg': 12, 'range': 45,  'aspd': 1.0, 'spd': 70, 'targets': 'ground', 'color': (150,170,200), 'desc': 'Cheap melee fighter.'},
    'knight':      {'name': 'Knight',        'rarity': 'Common',    'cost': 3, 'type': 'melee',    'hp': 160, 'dmg': 20, 'range': 45,  'aspd': 1.2, 'spd': 60, 'targets': 'ground', 'color': (100,140,200), 'desc': 'Sturdy melee warrior.'},
    'archer':      {'name': 'Archer',        'rarity': 'Common',    'cost': 3, 'type': 'ranged',   'hp': 90,  'dmg': 15, 'range': 220, 'aspd': 1.1, 'spd': 55, 'targets': 'both',   'color': (80,180,110),  'desc': 'Ranged attacker.'},
    'wisp':        {'name': 'Sky Wisp',      'rarity': 'Common',    'cost': 2, 'type': 'flying',   'hp': 70,  'dmg': 10, 'range': 45,  'aspd': 0.9, 'spd': 90, 'targets': 'both',   'flying': True, 'color': (180,220,255), 'desc': 'Fast flying harasser.'},
    'heal_spell':  {'name': 'Healing Light', 'rarity': 'Common',    'cost': 3, 'type': 'spell_heal','heal': 100, 'aoe': 100, 'color': (240,240,150), 'desc': 'Heals allied units in radius.'},
    'apprentice':  {'name': 'Apprentice',    'rarity': 'Rare',      'cost': 4, 'type': 'mage',     'hp': 80,  'dmg': 25, 'range': 200, 'aspd': 1.5, 'spd': 50, 'targets': 'both',   'aoe': 40, 'color': (160,120,220), 'desc': 'Ranged AoE caster.'},
    'shield_guard':{'name': 'Shield Guardian','rarity': 'Rare',     'cost': 4, 'type': 'tank',     'hp': 320, 'dmg': 10, 'range': 45,  'aspd': 1.5, 'spd': 40, 'targets': 'ground', 'color': (140,140,160), 'desc': 'Massive damage sponge.'},
    'healer':      {'name': 'Priestess',     'rarity': 'Rare',      'cost': 4, 'type': 'healer',   'hp': 100, 'dmg': 0,  'range': 180, 'aspd': 2.0, 'spd': 50, 'targets': 'heal',   'heal': 30, 'color': (240,220,120), 'desc': 'Heals nearby allies.'},
    'fireball':    {'name': 'Fireball',      'rarity': 'Rare',      'cost': 4, 'type': 'spell',    'dmg': 120, 'aoe': 80, 'color': (240,120,60), 'desc': 'Deals area damage.'},
    'war_banner':  {'name': 'War Banner',    'rarity': 'Rare',      'cost': 3, 'type': 'structure', 'hp': 250, 'dmg': 15, 'range': 180, 'aspd': 1.5, 'spd': 0, 'targets': 'both', 'color': (200,150,60), 'desc': 'Defensive tower spawn.'},
    'assassin':    {'name': 'Shadow Assassin','rarity': 'Epic',     'cost': 5, 'type': 'melee',    'hp': 140, 'dmg': 55, 'range': 45,  'aspd': 0.9, 'spd': 100,'targets': 'ground', 'color': (80,60,120), 'desc': 'High damage striker.'},
    'lightning':   {'name': 'Chain Lightning','rarity': 'Epic',     'cost': 5, 'type': 'spell',    'dmg': 90, 'aoe': 100, 'color': (150,200,255), 'desc': 'Large area damage.'},
    'champion':    {'name': 'Knight Champion','rarity': 'Epic',     'cost': 6, 'type': 'melee',    'hp': 450, 'dmg': 40, 'range': 50,  'aspd': 1.3, 'spd': 55, 'targets': 'ground', 'color': (100,160,230), 'desc': 'Elite tank-fighter.'},
    'phoenix':     {'name': 'Phoenix',       'rarity': 'Legendary', 'cost': 6, 'type': 'flying',   'hp': 200, 'dmg': 35, 'range': 180, 'aspd': 1.2, 'spd': 80, 'targets': 'both',   'flying': True, 'color': (255,140,50), 'desc': 'Flying firebird.'},
    'dragon':      {'name': 'Ruby Dragon',   'rarity': 'Legendary', 'cost': 7, 'type': 'flying',   'hp': 380, 'dmg': 45, 'range': 220, 'aspd': 1.6, 'spd': 70, 'targets': 'both',   'flying': True, 'aoe': 50, 'color': (220,80,60), 'desc': 'Powerful flying dragon.'},
}

DEFAULT_DECK = ['squire', 'knight', 'archer', 'wisp', 'fireball', 'heal_spell', 'war_banner', 'apprentice']
ALL_CARDS = list(CARD_DEFS.keys())

# ---------------------------------------------------------------------------
# CAMPAIGN
# ---------------------------------------------------------------------------
REGIONS = [
    {
        'id': 1, 'name': 'Emerald Forest', 'color': (40,140,80),
        'families': [1,2,5,10],
        'battles': [
            {'name': 'Forest Edge',       'diff': 1},
            {'name': 'Whispering Glade',  'diff': 1},
            {'name': 'Ancient Grove',     'diff': 2},
            {'name': 'Elder Treant (Boss)','diff': 2, 'boss': True},
        ]
    },
    {
        'id': 2, 'name': 'Golden Desert', 'color': (200,160,60),
        'families': [1,2,5,10,3,4],
        'battles': [
            {'name': 'Dune Outpost',      'diff': 2},
            {'name': 'Sunken Oasis',      'diff': 2},
            {'name': 'Scorpion Den',      'diff': 3},
            {'name': 'Sun Pharaoh (Boss)','diff': 3, 'boss': True},
        ]
    },
    {
        'id': 3, 'name': 'Frozen Highlands', 'color': (120,180,230),
        'families': [1,2,5,10,3,4,6,7],
        'battles': [
            {'name': 'Frost Ridge',       'diff': 3},
            {'name': 'Ice Cavern',        'diff': 3},
            {'name': 'Glacier Pass',      'diff': 3},
            {'name': 'Frost Titan (Boss)','diff': 4, 'boss': True},
        ]
    },
    {
        'id': 4, 'name': 'Inferno Realm', 'color': (220,80,60),
        'families': [1,2,5,10,3,4,6,7,8,9],
        'battles': [
            {'name': 'Cinder Wastes',     'diff': 3},
            {'name': 'Molten Chasm',      'diff': 4},
            {'name': 'Ember Throne',      'diff': 4},
            {'name': 'Inferno Wyrm (Boss)','diff': 4, 'boss': True},
        ]
    },
    {
        'id': 5, 'name': 'Crown Kingdom', 'color': (230,180,60),
        'families': [1,2,3,4,5,6,7,8,9,10],
        'battles': [
            {'name': 'Royal Gate',        'diff': 4},
            {'name': 'Hall of Kings',     'diff': 4},
            {'name': 'Shattered Crown',   'diff': 4},
            {'name': 'Shadow King (Boss)','diff': 4, 'boss': True},
        ]
    },
]

# ---------------------------------------------------------------------------
# UTIL
# ---------------------------------------------------------------------------
def get_data_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~/.local/share')
    d = Path(base) / 'MultiplyRoyale'
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        d = Path('.')
    return d

_FONT_CACHE = {}
def get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = pygame.font.SysFont('segoeui,arial,sans', size, bold=bold)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]

def draw_text(surf, text, pos, size=20, color=WHITE, bold=False, center=False):
    f = get_font(size, bold)
    img = f.render(str(text), True, color)
    r = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surf.blit(img, r)
    return r

def make_sound(freq, dur, vol=0.15):
    if not AUDIO_OK: return None
    try:
        sr = 22050
        n = int(sr * dur)
        buf = array.array('h')
        for i in range(n):
            s = int(32767 * vol * math.sin(2*math.pi*freq*i/sr) *
                    max(0, 1 - i/n))
            buf.append(s)
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

SFX = {}
def init_sfx():
    SFX['click']    = make_sound(600, 0.06, 0.2)
    SFX['correct']  = make_sound(880, 0.15, 0.25)
    SFX['wrong']    = make_sound(180, 0.25, 0.25)
    SFX['deploy']   = make_sound(440, 0.12, 0.2)
    SFX['hit']      = make_sound(260, 0.05, 0.1)
    SFX['victory']  = make_sound(660, 0.4, 0.3)
    SFX['defeat']   = make_sound(140, 0.5, 0.3)

def play_sfx(name):
    s = SFX.get(name)
    if s and AUDIO_OK:
        try:
            s.play()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
class SaveDB:
    def __init__(self, path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        c = self.conn.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS player (id INTEGER PRIMARY KEY, level INT DEFAULT 1, xp INT DEFAULT 0, gold INT DEFAULT 150, region INT DEFAULT 1, battles_won INT DEFAULT 0);
            CREATE TABLE IF NOT EXISTS cards (card_id TEXT PRIMARY KEY, level INT DEFAULT 1, dupes INT DEFAULT 0, unlocked INT DEFAULT 1);
            CREATE TABLE IF NOT EXISTS deck (slot INTEGER PRIMARY KEY, card_id TEXT);
            CREATE TABLE IF NOT EXISTS facts (a INT, b INT, attempts INT DEFAULT 0, correct INT DEFAULT 0, incorrect INT DEFAULT 0, total_time REAL DEFAULT 0, last_ts REAL DEFAULT 0, mastery INT DEFAULT 0, streak INT DEFAULT 0, PRIMARY KEY(a,b));
            CREATE TABLE IF NOT EXISTS campaign (region INT, battle INT, won INT DEFAULT 0, PRIMARY KEY(region, battle));
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        ''')
        self.conn.commit()
        c.execute("INSERT OR IGNORE INTO player (id) VALUES (1)")
        self.conn.commit()
        for cid in CARD_DEFS:
            c.execute("INSERT OR IGNORE INTO cards (card_id) VALUES (?)", (cid,))
        self.conn.commit()
        c.execute("SELECT COUNT(*) FROM deck")
        if c.fetchone()[0] == 0:
            for i, cid in enumerate(DEFAULT_DECK):
                c.execute("INSERT INTO deck (slot, card_id) VALUES (?,?)", (i, cid))
        self.conn.commit()
        for a in range(1, 13):
            for b in range(1, 13):
                c.execute("INSERT OR IGNORE INTO facts (a,b) VALUES (?,?)", (a,b))
        self.conn.commit()

    def get_player(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM player WHERE id=1")
        return dict(c.fetchone())

    def update_player(self, **kw):
        if not kw: return
        sets = ', '.join(f"{k}=?" for k in kw)
        vals = list(kw.values()) + [1]
        self.conn.execute(f"UPDATE player SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def get_card(self, cid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM cards WHERE card_id=?", (cid,))
        row = c.fetchone()
        return dict(row) if row else {'card_id': cid, 'level': 1, 'dupes': 0, 'unlocked': 1}

    def all_cards(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM cards")
        return {r['card_id']: dict(r) for r in c.fetchall()}

    def update_card(self, cid, **kw):
        if not kw: return
        sets = ', '.join(f"{k}=?" for k in kw)
        vals = list(kw.values()) + [cid]
        self.conn.execute(f"UPDATE cards SET {sets} WHERE card_id=?", vals)
        self.conn.commit()

    def get_deck(self):
        c = self.conn.cursor()
        c.execute("SELECT slot, card_id FROM deck ORDER BY slot")
        deck = [r['card_id'] for r in c.fetchall()]
        while len(deck) < 8:
            deck.append(DEFAULT_DECK[len(deck)])
        return deck[:8]

    def set_deck(self, deck):
        c = self.conn.cursor()
        c.execute("DELETE FROM deck")
        for i, cid in enumerate(deck[:8]):
            c.execute("INSERT INTO deck (slot, card_id) VALUES (?,?)", (i, cid))
        self.conn.commit()

    def get_fact(self, a, b):
        c = self.conn.cursor()
        c.execute("SELECT * FROM facts WHERE a=? AND b=?", (a,b))
        row = c.fetchone()
        return dict(row) if row else {'a':a,'b':b,'attempts':0,'correct':0,'incorrect':0,'total_time':0,'last_ts':0,'mastery':0,'streak':0}

    def update_fact(self, a, b, **kw):
        if not kw: return
        sets = ', '.join(f"{k}=?" for k in kw)
        vals = list(kw.values()) + [a, b]
        self.conn.execute(f"UPDATE facts SET {sets} WHERE a=? AND b=?", vals)
        self.conn.commit()

    def all_facts(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM facts")
        return [dict(r) for r in c.fetchall()]

    def get_setting(self, key, default=None):
        c = self.conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        if row is None: return default
        try:
            return json.loads(row['value'])
        except Exception:
            return row['value']

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)",
                          (key, json.dumps(value)))
        self.conn.commit()

    def is_won(self, region, battle):
        c = self.conn.cursor()
        c.execute("SELECT won FROM campaign WHERE region=? AND battle=?", (region, battle))
        r = c.fetchone()
        return bool(r and r['won'])

    def set_won(self, region, battle, won=1):
        self.conn.execute("INSERT OR REPLACE INTO campaign (region, battle, won) VALUES (?,?,?)",
                          (region, battle, won))
        self.conn.commit()

    def is_region_unlocked(self, rid):
        if rid == 1: return True
        for b_idx, b in enumerate(REGIONS[rid-2]['battles']):
            if b.get('boss') and self.is_won(rid-1, b_idx):
                return True
        return False

    def region_progress(self, rid):
        battles = REGIONS[rid-1]['battles']
        done = sum(1 for i in range(len(battles)) if self.is_won(rid, i))
        return done, len(battles)

    def reset(self):
        self.conn.execute("DELETE FROM player")
        self.conn.execute("DELETE FROM cards")
        self.conn.execute("DELETE FROM deck")
        self.conn.execute("DELETE FROM facts")
        self.conn.execute("DELETE FROM campaign")
        self.conn.execute("DELETE FROM settings")
        self.conn.commit()
        self._init()

# ---------------------------------------------------------------------------
# MULTIPLICATION ENGINE
# ---------------------------------------------------------------------------
class MultEngine:
    def __init__(self, db):
        self.db = db

    def _weight(self, fact):
        attempts = fact['attempts']
        incorrect = fact['incorrect']
        correct = fact['correct']
        mastery = fact['mastery']
        last_ts = fact['last_ts'] or 0
        age = time.time() - last_ts if last_ts > 0 else 1e9
        w = 1.0
        if attempts == 0:
            w += 8.0
        else:
            acc = correct / max(1, attempts)
            w += (1 - acc) * 6.0
            w += (5 - mastery) * 1.5
        w += incorrect * 1.5
        if attempts >= 3 and mastery >= 4:
            w *= 0.3
        w += min(3.0, age / 86400.0)
        w += random.random() * 2.0
        return max(0.05, w)

    def select_question(self, allowed_families):
        facts = self.db.all_facts()
        pool = []
        for f in facts:
            a, b = f['a'], f['b']
            if a in allowed_families or b in allowed_families:
                if a > 12 or b > 12: continue
                pool.append(f)
        if not pool:
            a = random.choice(allowed_families)
            b = random.randint(1, 10)
            return a, b
        weighted = [(f, self._weight(f)) for f in pool]
        total = sum(w for _, w in weighted)
        r = random.random() * total
        acc = 0
        for f, w in weighted:
            acc += w
            if acc >= r:
                return f['a'], f['b']
        return pool[0]['a'], pool[0]['b']

    def make_options(self, a, b, n=4):
        ans = a * b
        opts = {ans}
        tries = 0
        while len(opts) < n and tries < 60:
            tries += 1
            variant = random.choice([
                ans + random.choice([-a, a, -b, b, -1, 1, -2, 2, -10, 10]),
                a * random.choice([max(1, b-1), b+1, b+2]),
                random.choice([a,b]) * random.randint(1,10),
            ])
            if 0 <= variant <= 144 and variant != ans:
                opts.add(variant)
        opts = list(opts)
        random.shuffle(opts)
        return opts

    def record(self, a, b, correct, response_time, assisted=False):
        f = self.db.get_fact(a, b)
        attempts = f['attempts'] + 1
        ncorrect = f['correct'] + (1 if correct else 0)
        nincorrect = f['incorrect'] + (0 if correct else 1)
        total_time = f['total_time'] + response_time
        streak = (f['streak'] + 1) if correct else 0
        mastery = f['mastery']
        if correct and response_time < 6 and not assisted:
            if streak >= 2:
                mastery = min(5, mastery + 1)
        elif not correct:
            mastery = max(0, mastery - 1)
        self.db.update_fact(
            a, b,
            attempts=attempts, correct=ncorrect, incorrect=nincorrect,
            total_time=total_time, last_ts=time.time(),
            mastery=mastery, streak=streak
        )

    def overall_stats(self):
        facts = self.db.all_facts()
        total = sum(f['attempts'] for f in facts)
        correct = sum(f['correct'] for f in facts)
        mastered = sum(1 for f in facts if f['mastery'] >= 4)
        return {
            'total': total, 'correct': correct,
            'accuracy': (correct / total * 100) if total else 0,
            'mastered': mastered
        }

# ---------------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------------
class Unit:
    def __init__(self, team, lane, x, y, cid, level=1):
        c = CARD_DEFS[cid]
        self.team = team
        self.lane = lane
        self.x = float(x)
        self.y = float(y)
        self.cid = cid
        self.name = c['name']
        self.color = c['color']
        self.flying = c.get('flying', False)
        self.type = c['type']
        lvl_m = 1.0 + (level - 1) * 0.1
        self.max_hp = c.get('hp', 100) * lvl_m
        self.hp = self.max_hp
        self.dmg = c.get('dmg', 0) * lvl_m
        self.range = c.get('range', 40)
        self.aspd = c.get('aspd', 1.0)
        self.spd = c.get('spd', 60)
        self.targets = c.get('targets', 'ground')
        self.aoe = c.get('aoe', 0)
        self.heal = c.get('heal', 0) * lvl_m
        self.attack_cd = 0.0
        self.alive = True
        self.radius = 16 if self.flying else 14
        self.hit_flash = 0.0

    def valid_target(self, t):
        if not getattr(t, 'alive', True): return False
        if t is self: return False
        if getattr(t, 'flying', False) and self.targets == 'ground': return False
        if not getattr(t, 'flying', False) and self.targets == 'air': return False
        return True

    def find_target(self, battle):
        if self.team == 'player':
            enemies = list(battle.enemy_units)
            structures = battle.enemy_towers + [battle.enemy_castle]
        else:
            enemies = list(battle.player_units)
            structures = battle.player_towers + [battle.player_castle]
        best = None
        best_d = float('inf')
        for e in enemies:
            if not e.alive: continue
            if not self.valid_target(e): continue
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d < best_d:
                best_d, best = d, e
        if best: return best, best_d
        for s in structures:
            if not s.alive: continue
            d = math.hypot(s.x - self.x, s.y - self.y)
            if d < best_d:
                best_d, best = d, s
        return best, best_d

    def update(self, dt, battle):
        if not self.alive: return
        self.attack_cd = max(0, self.attack_cd - dt)
        self.hit_flash = max(0, self.hit_flash - dt)

        if self.type == 'healer':
            allies = battle.player_units if self.team == 'player' else battle.enemy_units
            best = None
            best_hp = 1e9
            for a in allies:
                if not a.alive or a is self: continue
                if a.hp >= a.max_hp: continue
                d = math.hypot(a.x - self.x, a.y - self.y)
                if d <= self.range and a.hp < best_hp:
                    best = a
                    best_hp = a.hp
            if best and self.attack_cd <= 0:
                best.hp = min(best.max_hp, best.hp + self.heal)
                self.attack_cd = self.aspd
                battle.add_heal_effect(best.x, best.y)
            elif not best:
                self._advance(dt, battle)
            return

        target, dist = self.find_target(battle)
        if target is None:
            self._advance(dt, battle)
            return

        if dist <= self.range:
            if self.attack_cd <= 0:
                self._attack(target, battle)
                self.attack_cd = self.aspd
        else:
            dx = target.x - self.x
            dy = target.y - self.y
            d = math.hypot(dx, dy)
            if d > 0.1:
                mv = self.spd * dt
                self.x += dx / d * mv
                self.y += dy / d * mv

    def _advance(self, dt, battle):
        if self.spd <= 0: return
        direction = 1 if self.team == 'player' else -1
        self.x += direction * self.spd * dt

    def _attack(self, target, battle):
        if self.range > 100:
            battle.projectiles.append(
                Projectile(self.x, self.y, target, self.dmg, self.team, self.color, self.aoe))
        else:
            self._deal_damage(target, battle, self.dmg, self.aoe, self.color)
        battle.add_hit_effect(target.x, target.y, self.color)

    def _deal_damage(self, target, battle, dmg, aoe, color):
        if aoe > 0:
            if self.team == 'player':
                group = list(battle.enemy_units) + battle.enemy_towers + [battle.enemy_castle]
            else:
                group = list(battle.player_units) + battle.player_towers + [battle.player_castle]
            for e in group:
                if not getattr(e, 'alive', True): continue
                if math.hypot(e.x - target.x, e.y - target.y) <= aoe:
                    e.hp -= dmg
                    if getattr(e, 'hit_flash', None) is not None:
                        e.hit_flash = 0.15
                    if e.hp <= 0:
                        e.alive = False
                    battle.add_damage_number(e.x, e.y, int(dmg))
        else:
            if target.alive:
                target.hp -= dmg
                if hasattr(target, 'hit_flash'):
                    target.hit_flash = 0.15
                if target.hp <= 0:
                    target.alive = False
                battle.add_damage_number(target.x, target.y, int(dmg))


class Projectile:
    def __init__(self, x, y, target, dmg, team, color, aoe=0, speed=420):
        self.x = float(x); self.y = float(y)
        self.target = target
        self.dmg = dmg
        self.team = team
        self.color = color
        self.aoe = aoe
        self.speed = speed
        self.alive = True

    def update(self, dt, battle):
        if not self.alive: return
        if not getattr(self.target, 'alive', True):
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        d = math.hypot(dx, dy)
        mv = self.speed * dt
        if d <= mv:
            self._hit(battle)
            self.alive = False
        else:
            self.x += dx / d * mv
            self.y += dy / d * mv

    def _hit(self, battle):
        if self.aoe > 0:
            if self.team == 'player':
                group = list(battle.enemy_units) + battle.enemy_towers + [battle.enemy_castle]
            else:
                group = list(battle.player_units) + battle.player_towers + [battle.player_castle]
            for e in group:
                if not getattr(e, 'alive', True): continue
                if math.hypot(e.x - self.target.x, e.y - self.target.y) <= self.aoe:
                    e.hp -= self.dmg
                    if hasattr(e, 'hit_flash'): e.hit_flash = 0.15
                    if e.hp <= 0: e.alive = False
                    battle.add_damage_number(e.x, e.y, int(self.dmg))
        else:
            if getattr(self.target, 'alive', True):
                self.target.hp -= self.dmg
                if hasattr(self.target, 'hit_flash'): self.target.hit_flash = 0.15
                if self.target.hp <= 0: self.target.alive = False
                battle.add_damage_number(self.target.x, self.target.y, int(self.dmg))


class Tower:
    def __init__(self, x, y, team, lane):
        self.x = float(x); self.y = float(y)
        self.team = team
        self.lane = lane
        self.max_hp = 800
        self.hp = self.max_hp
        self.dmg = 30
        self.range = 220
        self.aspd = 1.2
        self.attack_cd = 0.0
        self.alive = True
        self.flying = False
        self.hit_flash = 0.0

    def update(self, dt, battle):
        if not self.alive: return
        self.attack_cd = max(0, self.attack_cd - dt)
        self.hit_flash = max(0, self.hit_flash - dt)
        enemies = battle.enemy_units if self.team == 'player' else battle.player_units
        best = None; best_d = float('inf')
        for e in enemies:
            if not e.alive: continue
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d <= self.range and d < best_d:
                best_d, best = d, e
        if best and self.attack_cd <= 0:
            battle.projectiles.append(Projectile(self.x, self.y, best, self.dmg, self.team, GOLD))
            self.attack_cd = self.aspd


class Castle:
    def __init__(self, x, y, team):
        self.x = float(x); self.y = float(y)
        self.team = team
        self.max_hp = 2200
        self.hp = self.max_hp
        self.alive = True
        self.flying = False
        self.hit_flash = 0.0

    def update(self, dt, battle):
        if not self.alive: return
        self.hit_flash = max(0, self.hit_flash - dt)


class Particle:
    def __init__(self, x, y, color, life=0.5, size=4, vel=None):
        self.x = x; self.y = y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.vx, self.vy = vel if vel else (random.uniform(-60,60), random.uniform(-60,60))
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 120 * dt


class DamageNumber:
    def __init__(self, x, y, amount, color=WHITE):
        self.x = x; self.y = y
        self.amount = amount
        self.life = 0.9
        self.color = color
        self.alive = True

    def update(self, dt):
        self.life -= dt
        self.y -= 40 * dt
        if self.life <= 0:
            self.alive = False


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------
AI_PARAMS = {
    1: {'interval': 3.0, 'save_energy': 1.5, 'aggression': 0.4},
    2: {'interval': 2.0, 'save_energy': 1.0, 'aggression': 0.6},
    3: {'interval': 1.3, 'save_energy': 0.7, 'aggression': 0.8},
    4: {'interval': 0.9, 'save_energy': 0.4, 'aggression': 1.0},
}

class AI:
    def __init__(self, difficulty, deck):
        self.difficulty = difficulty
        self.params = AI_PARAMS[difficulty]
        self.deck = deck[:]
        random.shuffle(self.deck)
        self.hand = self.deck[:4]
        self.deck = self.deck[4:]
        self.decision_timer = self.params['interval'] * 0.6

    def update(self, dt, battle):
        if battle.ended: return
        self.decision_timer -= dt
        if self.decision_timer > 0: return
        self.decision_timer = self.params['interval'] * random.uniform(0.85, 1.15)

        energy = battle.enemy_energy
        affordable = [(i, cid) for i, cid in enumerate(self.hand)
                      if CARD_DEFS[cid]['cost'] <= energy - self.params['save_energy']]
        if not affordable:
            affordable = [(i, cid) for i, cid in enumerate(self.hand)
                          if CARD_DEFS[cid]['cost'] <= energy]
        if not affordable:
            return

        # Score threats
        threat_lanes = [0, 0]
        for u in battle.player_units:
            if u.alive and u.x > 500:
                threat_lanes[u.lane] += 20
        threat_total = sum(threat_lanes)

        best_score = -1
        best_choice = None
        for idx, cid in affordable:
            c = CARD_DEFS[cid]
            score = 1.0
            score += c['cost'] * 0.2
            # Spell prioritization
            if c['type'] in ('spell', 'spell_heal'):
                if c['type'] == 'spell' and threat_total > 40:
                    score += 4.0
                elif c['type'] == 'spell_heal' and len([u for u in battle.enemy_units if u.hp < u.max_hp*0.5]) > 0:
                    score += 3.0
                else:
                    score += 0.3
            # Counter flying with archers / ranged
            if any(u.flying for u in battle.player_units) and c.get('targets') in ('both',):
                score += 2.0
            # Defensive response
            if threat_total > 50 and c.get('type') in ('melee', 'tank', 'ranged', 'mage'):
                score += 3.0
            # Pressure aggression
            if threat_total < 20 and c.get('type') in ('melee', 'flying', 'ranged'):
                score += self.params['aggression'] * 2.5
            score += random.uniform(0, 1.5)
            if score > best_score:
                best_score = score
                best_choice = (idx, cid)

        if best_choice is None:
            return
        idx, cid = best_choice

        # Choose lane
        if threat_lanes[0] > threat_lanes[1]:
            lane = 0
        elif threat_lanes[1] > threat_lanes[0]:
            lane = 1
        else:
            lane = random.choice([0, 1])

        # Deploy
        c = CARD_DEFS[cid]
        cost = c['cost']
        if battle.enemy_energy < cost:
            return
        battle.enemy_energy -= cost
        y = 240 if lane == 0 else 460
        if c['type'] in ('spell', 'spell_heal'):
            # Target an area near player cluster
            tx = 640
            if battle.player_units:
                pu = random.choice([u for u in battle.player_units if u.alive] or [None])
                if pu is not None:
                    tx = pu.x
            battle.cast_spell('enemy', cid, tx, 350)
        else:
            if c['type'] == 'structure':
                x = 780
            else:
                x = 700
            battle.spawn_unit('enemy', cid, lane, x, y)
        # rotate
        if self.deck:
            self.hand[idx] = self.deck.pop(0)
            self.deck.append(cid)
        else:
            self.deck.append(cid)


# ---------------------------------------------------------------------------
# BATTLE
# ---------------------------------------------------------------------------
class Battle:
    def __init__(self, game, region_id, battle_idx, difficulty):
        self.game = game
        self.region_id = region_id
        self.battle_idx = battle_idx
        self.difficulty = difficulty
        self.region = REGIONS[region_id - 1]
        self.battle_def = self.region['battles'][battle_idx]

        self.player_units = []
        self.enemy_units = []
        self.projectiles = []
        self.particles = []
        self.damage_numbers = []

        self.player_energy = 5.0
        self.enemy_energy = 5.0
        self.max_energy = 10

        lane_top_y = 185
        lane_bot_y = 435
        self.player_towers = [Tower(340, lane_top_y, 'player', 0), Tower(340, lane_bot_y, 'player', 1)]
        self.enemy_towers = [Tower(940, lane_top_y, 'enemy', 0), Tower(940, lane_bot_y, 'enemy', 1)]
        self.player_castle = Castle(100, 310, 'player')
        self.enemy_castle = Castle(1180, 310, 'enemy')

        self.match_time = 180.0
        self.ended = False
        self.result = None
        self.end_timer = 0.0

        deck = game.db.get_deck()
        self.player_deck = deck[:]
        self.player_hand = self.player_deck[:4]
        self.player_deck = self.player_deck[4:]

        enemy_deck_pool = DEFAULT_DECK[:]
        if difficulty >= 3:
            enemy_deck_pool = ['knight', 'archer', 'shield_guard', 'apprentice', 'fireball',
                                'healer', 'champion', 'dragon']
        elif difficulty >= 2:
            enemy_deck_pool = ['squire', 'knight', 'archer', 'apprentice', 'shield_guard',
                                'fireball', 'healer', 'phoenix']
        self.ai = AI(difficulty, enemy_deck_pool)

        self.selected_card_idx = -1
        self.question = None
        self.question_pending_action = None
        self.card_lockout = {}
        self.message = ""
        self.message_timer = 0.0
        self.help_timer = 8.0

        self.q_every_n = game.db.get_setting('question_freq', 1)
        self.q_counter = 0

        self.allowed_families = self.region['families']

        self.rewards = {'gold': 0, 'xp': 0}

    def add_particle(self, x, y, color, count=6):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def add_hit_effect(self, x, y, color):
        self.add_particle(x, y, color, 4)
        play_sfx('hit')

    def add_heal_effect(self, x, y):
        self.add_particle(x, y, GREEN, 5)

    def add_damage_number(self, x, y, amount):
        self.damage_numbers.append(DamageNumber(x, y, amount, GOLD if amount >= 30 else WHITE))

    def show_message(self, text, dur=2.0):
        self.message = text
        self.message_timer = dur

    def spawn_unit(self, team, cid, lane, x=None, y=None):
        if y is None:
            y = 185 if lane == 0 else 435
        if x is None:
            x = 180 if team == 'player' else 1100
        lvl = 1
        if team == 'player':
            lvl = self.game.db.get_card(cid).get('level', 1)
        u = Unit(team, lane, x, y, cid, lvl)
        if team == 'player':
            self.player_units.append(u)
        else:
            self.enemy_units.append(u)
        self.add_particle(x, y, u.color, 8)
        play_sfx('deploy')

    def cast_spell(self, team, cid, tx, ty):
        c = CARD_DEFS[cid]
        if c['type'] == 'spell':
            dmg = c['dmg'] * (1.0 + (self.game.db.get_card(cid).get('level',1)-1)*0.1 if team=='player' else 1.0)
            aoe = c['aoe']
            if team == 'player':
                group = list(self.enemy_units) + self.enemy_towers + [self.enemy_castle]
            else:
                group = list(self.player_units) + self.player_towers + [self.player_castle]
            for e in group:
                if not getattr(e, 'alive', True): continue
                if math.hypot(e.x - tx, e.y - ty) <= aoe:
                    e.hp -= dmg
                    if hasattr(e, 'hit_flash'): e.hit_flash = 0.2
                    if e.hp <= 0: e.alive = False
                    self.add_damage_number(e.x, e.y, int(dmg))
            self.add_particle(tx, ty, c['color'], 25)
        elif c['type'] == 'spell_heal':
            heal = c['heal'] * (1.0 + (self.game.db.get_card(cid).get('level',1)-1)*0.1 if team=='player' else 1.0)
            aoe = c['aoe']
            allies = self.player_units if team == 'player' else self.enemy_units
            for a in allies:
                if a.alive and math.hypot(a.x - tx, a.y - ty) <= aoe:
                    a.hp = min(a.max_hp, a.hp + heal)
            self.add_particle(tx, ty, GREEN, 25)

    def try_play_card(self, idx, world_x, world_y):
        if self.ended: return False
        if idx < 0 or idx >= 4: return False
        cid = self.player_hand[idx]
        c = CARD_DEFS[cid]
        if c['cost'] > self.player_energy:
            self.show_message("Not enough energy!")
            play_sfx('wrong')
            return False
        if self.card_lockout.get(cid, 0) > time.time():
            self.show_message("Card locked out!")
            return False
        # check frequency
        need_q = False
        if self.q_every_n > 0:
            self.q_counter += 1
            if self.q_counter >= self.q_every_n:
                self.q_counter = 0
                need_q = True
        if need_q and self.q_every_n > 0:
            a, b = self.game.mult.select_question(self.allowed_families)
            options = self.game.mult.make_options(a, b, 4)
            self.question = {
                'a': a, 'b': b, 'answer': a * b,
                'options': options,
                'start': time.time(),
                'feedback': None,
                'feedback_time': 0.0,
            }
            self.question_pending_action = {
                'idx': idx, 'cid': cid,
                'wx': world_x, 'wy': world_y,
            }
            self.selected_card_idx = -1
            return True
        else:
            self._execute_play(idx, cid, world_x, world_y)
            self.selected_card_idx = -1
            return True

    def _execute_play(self, idx, cid, wx, wy):
        c = CARD_DEFS[cid]
        cost = c['cost']
        if cost > self.player_energy:
            return
        self.player_energy -= cost
        if c['type'] in ('spell', 'spell_heal'):
            self.cast_spell('player', cid, wx, wy)
        else:
            lane = 0 if wy < 310 else 1
            y = 185 if lane == 0 else 435
            x = max(120, min(600, wx))
            self.spawn_unit('player', cid, lane, x, y)
        # rotate
        if self.player_deck:
            self.player_hand[idx] = self.player_deck.pop(0)
            self.player_deck.append(cid)
        else:
            self.player_deck.append(cid)

    def answer_question(self, choice):
        if not self.question: return
        q = self.question
        rt = time.time() - q['start']
        correct = (choice == q['answer'])
        self.game.mult.record(q['a'], q['b'], correct, rt, assisted=False)
        if correct:
            play_sfx('correct')
            q['feedback'] = 'correct'
            q['feedback_time'] = 0.4
        else:
            play_sfx('wrong')
            q['feedback'] = 'wrong'
            q['feedback_time'] = 1.3
            cid = self.question_pending_action['cid'] if self.question_pending_action else None
            if cid:
                self.card_lockout[cid] = time.time() + 3.0

    def _resolve_question(self):
        if not self.question: return
        q = self.question
        if q['feedback'] == 'correct':
            if self.question_pending_action:
                p = self.question_pending_action
                self._execute_play(p['idx'], p['cid'], p['wx'], p['wy'])
            self.question = None
            self.question_pending_action = None
        elif q['feedback'] == 'wrong':
            self.question = None
            self.question_pending_action = None

    def end_battle(self, result=None):
        if self.ended: return
        if result is None:
            p = self.player_castle.hp + sum(t.hp for t in self.player_towers)
            e = self.enemy_castle.hp + sum(t.hp for t in self.enemy_towers)
            if p > e: result = 'win'
            elif e > p: result = 'lose'
            else: result = 'draw'
        self.ended = True
        self.result = result
        self.end_timer = 0.0

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.help_timer > 0:
            self.help_timer -= dt
        if self.ended:
            self.end_timer += dt
            return

        # energy regen
        regen = 1.0 / 2.5
        if self.match_time <= 60:
            regen *= 2.0
        self.player_energy = min(self.max_energy, self.player_energy + dt * regen)
        self.enemy_energy = min(self.max_energy, self.enemy_energy + dt * regen)

        # timer
        self.match_time -= dt
        if self.match_time <= 0:
            self.match_time = 0
            self.end_battle()
            return

        # Update entities
        for u in self.player_units + self.enemy_units:
            if u.alive: u.update(dt, self)
        for t in self.player_towers + self.enemy_towers:
            if t.alive: t.update(dt, self)
        self.player_castle.update(dt, self)
        self.enemy_castle.update(dt, self)

        for p in self.projectiles:
            p.update(dt, self)
        self.projectiles = [p for p in self.projectiles if p.alive]

        self.player_units = [u for u in self.player_units if u.alive]
        self.enemy_units = [u for u in self.enemy_units if u.alive]
        self.player_towers = [t for t in self.player_towers if t.alive]
        self.enemy_towers = [t for t in self.enemy_towers if t.alive]

        for e in self.particles: e.update(dt)
        self.particles = [e for e in self.particles if e.alive]
        for d in self.damage_numbers: d.update(dt)
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]

        # question feedback timer
        if self.question and self.question['feedback']:
            self.question['feedback_time'] -= dt
            if self.question['feedback_time'] <= 0:
                self._resolve_question()

        # AI
        self.ai.update(dt, self)

        if not self.player_castle.alive:
            self.end_battle('lose')
        elif not self.enemy_castle.alive:
            self.end_battle('win')


# ---------------------------------------------------------------------------
# UI HELPERS
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, callback=None, color=ROYAL_BLUE, size=22, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.size = size
        self.enabled = enabled
        self.hover = False

    def update(self, mp):
        self.hover = self.enabled and self.rect.collidepoint(mp)

    def handle_event(self, event):
        if not self.enabled: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_sfx('click')
                if self.callback: self.callback()
                return True
        return False

    def draw(self, surf):
        base = self.color
        if not self.enabled:
            base = (60, 65, 80)
        elif self.hover:
            base = tuple(min(255, c + 30) for c in base)
        pygame.draw.rect(surf, base, self.rect, border_radius=8)
        pygame.draw.rect(surf, GOLD, self.rect, 2, border_radius=8)
        col = WHITE if self.enabled else (160, 160, 170)
        draw_text(surf, self.text, self.rect.center, self.size, col, bold=True, center=True)


def draw_bg(surf, color1=NAVY, color2=DARK):
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = (int(color1[0]*(1-t)+color2[0]*t),
             int(color1[1]*(1-t)+color2[1]*t),
             int(color1[2]*(1-t)+color2[2]*t))
        pygame.draw.line(surf, c, (0, y), (WIDTH, y))


def draw_panel(surf, rect, color=ROYAL_BLUE, border=GOLD, alpha=255):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surf.blit(s, rect.topleft)
    pygame.draw.rect(surf, border, rect, 2, border_radius=8)


def draw_card_face(surf, cid, x, y, w, h, selected=False, disabled=False, hover=False):
    c = CARD_DEFS[cid]
    rar_col = RARITY_COLORS[c['rarity']]
    base_rect = pygame.Rect(x, y, w, h)
    fill_col = c['color'] if not disabled else (60, 60, 70)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*fill_col, 200))
    surf.blit(s, (x, y))
    # Border
    bw = 4 if selected else (3 if hover else 2)
    pygame.draw.rect(surf, rar_col if not selected else GOLD, base_rect, bw, border_radius=6)
    # Header bar
    pygame.draw.rect(surf, (*rar_col, 255), pygame.Rect(x, y, w, 22), border_radius=6)
    # Cost circle
    pygame.draw.circle(surf, ROYAL_BLUE, (x + 14, y + 14), 12)
    pygame.draw.circle(surf, GOLD, (x + 14, y + 14), 12, 2)
    draw_text(surf, c['cost'], (x + 14, y + 14), 16, WHITE, bold=True, center=True)
    # Name
    draw_text(surf, c['name'][:13], (x + 28, y + 4), 12, WHITE, bold=True)
    # Body: stats
    yy = y + 28
    if 'hp' in c:
        draw_text(surf, f"HP {int(c['hp'])}", (x + 6, yy), 12, WHITE); yy += 16
    if 'dmg' in c and c['dmg'] > 0:
        draw_text(surf, f"DMG {int(c['dmg'])}", (x + 6, yy), 12, WHITE); yy += 16
    if 'heal' in c:
        draw_text(surf, f"HEAL {int(c['heal'])}", (x + 6, yy), 12, WHITE); yy += 16
    if c['type'] in ('spell', 'spell_heal'):
        draw_text(surf, f"{c['type']}", (x + 6, yy), 11, CREAM)
    else:
        draw_text(surf, c['type'], (x + 6, yy), 11, CREAM)
    # Rarity footer
    pygame.draw.rect(surf, (*rar_col, 255), pygame.Rect(x, y + h - 16, w, 16), border_radius=0)
    draw_text(surf, c['rarity'], (x + w//2, y + h - 8), 10, BLACK, bold=True, center=True)
    if disabled:
        s2 = pygame.Surface((w, h), pygame.SRCALPHA)
        s2.fill((0, 0, 0, 140))
        surf.blit(s2, (x, y))


# ---------------------------------------------------------------------------
# SCREENS
# ---------------------------------------------------------------------------
class Screen:
    def __init__(self, game):
        self.game = game
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surf): pass


class MainMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        cx = WIDTH // 2
        self.buttons = [
            Button(cx - 150, 260, 300, 55, "Play Campaign", lambda: game.change_screen(WorldMapScreen(game))),
            Button(cx - 150, 325, 300, 55, "Cards", lambda: game.change_screen(CollectionScreen(game))),
            Button(cx - 150, 390, 300, 55, "Deck Builder", lambda: game.change_screen(DeckBuilderScreen(game))),
            Button(cx - 150, 455, 300, 55, "Academy", lambda: game.change_screen(PracticeScreen(game))),
            Button(cx - 150, 520, 300, 55, "Statistics", lambda: game.change_screen(StatsScreen(game))),
            Button(cx - 150, 585, 300, 55, "Settings", lambda: game.change_screen(SettingsScreen(game))),
        ]
        self.timer = 0.0

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)

    def update(self, dt):
        self.timer += dt
        mp = pygame.mouse.get_pos()
        for b in self.buttons: b.update(mp)

    def draw(self, surf):
        draw_bg(surf, (20, 30, 70), (8, 12, 30))
        # Title
        draw_text(surf, "MULTIPLY ROYALE", (WIDTH//2, 100), 64, GOLD, bold=True, center=True)
        draw_text(surf, "Rise of the Number Kings", (WIDTH//2, 165), 26, CREAM, center=True)
        # decorative
        for i in range(6):
            y = 210 + i * 12
            pygame.draw.line(surf, (*PURPLE, 100), (WIDTH//2 - 200, y), (WIDTH//2 + 200, y), 1)
        for b in self.buttons: b.draw(surf)
        draw_text(surf, f"Level {self.game.db.get_player()['level']}  •  Gold {self.game.db.get_player()['gold']}",
                  (WIDTH//2, 680), 18, CREAM, center=True)


class WorldMapScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.back_btn = Button(20, 660, 120, 45, "Back", lambda: game.change_screen(MainMenuScreen(game)))
        self.region_buttons = []
        for i, reg in enumerate(REGIONS):
            unlocked = game.db.is_region_unlocked(reg['id'])
            btn = Button(160 + i*210, 260, 190, 220, "", 
                         (lambda r=reg: self.enter_region(r)) if unlocked else None,
                         color=reg['color'], enabled=unlocked)
            self.region_buttons.append((btn, reg, unlocked))

    def enter_region(self, region):
        self.game.change_screen(BattleSelectScreen(self.game, region['id']))

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        for b, _, _ in self.region_buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.game.change_screen(MainMenuScreen(self.game))

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.back_btn.update(mp)
        for b, _, _ in self.region_buttons: b.update(mp)

    def draw(self, surf):
        draw_bg(surf, (25, 20, 50), (10, 8, 25))
        draw_text(surf, "World Map", (WIDTH//2, 60), 48, GOLD, bold=True, center=True)
        for b, reg, unlocked in self.region_buttons:
            if not unlocked:
                pygame.draw.rect(surf, (40, 40, 50), b.rect, border_radius=8)
                pygame.draw.rect(surf, (90, 90, 100), b.rect, 2, border_radius=8)
                draw_text(surf, "Locked", b.rect.center, 22, (150, 150, 160), bold=True, center=True)
            else:
                pygame.draw.rect(surf, reg['color'], b.rect, border_radius=8)
                pygame.draw.rect(surf, GOLD, b.rect, 3, border_radius=8)
                draw_text(surf, reg['name'], (b.rect.centerx, b.rect.y + 30), 20, WHITE, bold=True, center=True)
                done, total = self.game.db.region_progress(reg['id'])
                draw_text(surf, f"{done}/{total} battles", (b.rect.centerx, b.rect.y + 80), 16, WHITE, center=True)
                # Progress bar
                p_r = pygame.Rect(b.rect.x + 20, b.rect.y + 130, b.rect.w - 40, 14)
                pygame.draw.rect(surf, DARK, p_r, border_radius=4)
                fill = pygame.Rect(p_r.x, p_r.y, int(p_r.w * done/total), p_r.h)
                pygame.draw.rect(surf, GOLD, fill, border_radius=4)
                pygame.draw.rect(surf, WHITE, p_r, 1, border_radius=4)
        self.back_btn.draw(surf)


class BattleSelectScreen(Screen):
    def __init__(self, game, region_id):
        super().__init__(game)
        self.region_id = region_id
        self.region = REGIONS[region_id - 1]
        self.back_btn = Button(20, 660, 120, 45, "Back", lambda: game.change_screen(WorldMapScreen(game)))
        self.battle_buttons = []
        for i, b in enumerate(self.region['battles']):
            won = game.db.is_won(region_id, i)
            unlocked = (i == 0) or game.db.is_won(region_id, i-1)
            def cb(idx=i):
                game.change_screen(BattleScreen(game, region_id, idx, self.region['battles'][idx]['diff']))
            btn = Button(160, 130 + i*130, WIDTH - 320, 100, b['name'],
                         cb if unlocked else None,
                         color=EMERALD if won else (ROYAL_BLUE if not b.get('boss') else PURPLE),
                         enabled=unlocked)
            self.battle_buttons.append((btn, b, won, unlocked))

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        for btn, _, _, _ in self.battle_buttons: btn.handle_event(e)

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.back_btn.update(mp)
        for btn, _, _, _ in self.battle_buttons: btn.update(mp)

    def draw(self, surf):
        draw_bg(surf, (25, 20, 50), (10, 8, 25))
        draw_text(surf, self.region['name'], (WIDTH//2, 60), 44, self.region['color'], bold=True, center=True)
        draw_text(surf, f"Families: {', '.join(str(f) for f in self.region['families'])}",
                  (WIDTH//2, 105), 20, CREAM, center=True)
        for btn, b, won, unlocked in self.battle_buttons:
            if unlocked:
                if won:
                    pygame.draw.rect(surf, EMERALD, btn.rect, border_radius=8)
                else:
                    pygame.draw.rect(surf, btn.color, btn.rect, border_radius=8)
                pygame.draw.rect(surf, GOLD, btn.rect, 2, border_radius=8)
                draw_text(surf, b['name'], (btn.rect.centerx, btn.rect.y + 35), 28, WHITE, bold=True, center=True)
                diff_names = {1:'Beginner',2:'Warrior',3:'Commander',4:'Shadow King'}
                draw_text(surf, f"Difficulty: {diff_names[b['diff']]}", 
                          (btn.rect.centerx, btn.rect.y + 70), 16, CREAM, center=True)
                if won:
                    draw_text(surf, "✓ DEFEATED", (btn.rect.right - 80, btn.rect.y + 40), 20, GOLD, bold=True)
            else:
                pygame.draw.rect(surf, (40, 40, 50), btn.rect, border_radius=8)
                draw_text(surf, "Locked", btn.rect.center, 24, GRAY, bold=True, center=True)
        self.back_btn.draw(surf)


class BattleScreen(Screen):
    def __init__(self, game, region_id, battle_idx, difficulty):
        super().__init__(game)
        self.battle = Battle(game, region_id, battle_idx, difficulty)
        self.card_rects = []
        hand_y = 560
        total_w = 4 * 130 + 3 * 10
        start_x = 365
        for i in range(4):
            self.card_rects.append(pygame.Rect(start_x + i*140, hand_y, 130, 150))
        self.pause_btn = Button(WIDTH - 130, 15, 110, 35, "Pause", self.pause)
        self.finalized = False
        self.show_exit = False

    def pause(self):
        self.game.change_screen(PauseScreen(self.game, self))

    def handle_event(self, e):
        if self.battle.ended:
            if e.type == pygame.MOUSEBUTTONDOWN and self.battle.end_timer > 1.5:
                self._finalize()
            return
        if self.battle.question:
            if e.type == pygame.KEYDOWN:
                if pygame.K_1 <= e.key <= pygame.K_4:
                    idx = e.key - pygame.K_1
                    self._choose_answer(idx)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # option rects computed in draw
                if hasattr(self, 'option_rects'):
                    for i, r in enumerate(self.option_rects):
                        if r.collidepoint(e.pos):
                            self._choose_answer(i)
                            break
            return
        self.pause_btn.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.pause()
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # card click
            for i, r in enumerate(self.card_rects):
                if r.collidepoint(e.pos):
                    self.select_card(i)
                    return
            # battlefield click
            if 60 <= e.pos[0] <= 1220 and 100 <= e.pos[1] <= 550:
                if self.battle.selected_card_idx >= 0:
                    idx = self.battle.selected_card_idx
                    cid = self.battle.player_hand[idx]
                    c = CARD_DEFS[cid]
                    if c['type'] in ('spell', 'spell_heal'):
                        self.battle.try_play_card(idx, e.pos[0], e.pos[1])
                    else:
                        if e.pos[0] > 640:
                            self.battle.show_message("Deploy on your side!")
                            return
                        self.battle.try_play_card(idx, e.pos[0], e.pos[1])
        if e.type == pygame.KEYDOWN:
            if pygame.K_1 <= e.key <= pygame.K_4:
                self.select_card(e.key - pygame.K_1)

    def select_card(self, i):
        if self.battle.question: return
        cid = self.battle.player_hand[i]
        if CARD_DEFS[cid]['cost'] > self.battle.player_energy:
            self.battle.show_message("Not enough energy!")
            play_sfx('wrong')
            self.battle.selected_card_idx = -1
            return
        if self.battle.card_lockout.get(cid, 0) > time.time():
            self.battle.show_message("Card is locked!")
            return
        if self.battle.selected_card_idx == i:
            self.battle.selected_card_idx = -1
        else:
            self.battle.selected_card_idx = i

    def _choose_answer(self, opt_idx):
        if not self.battle.question: return
        q = self.battle.question
        if q['feedback']: return
        choice = q['options'][opt_idx]
        self.battle.answer_question(choice)

    def _finalize(self):
        if self.finalized: return
        self.finalized = True
        b = self.battle
        if b.result == 'win':
            play_sfx('victory')
            b.rewards['gold'] = 50 + self.battle.difficulty * 25
            b.rewards['xp'] = 30 + self.battle.difficulty * 15
            if b.battle_def.get('boss'):
                b.rewards['gold'] += 100
                b.rewards['xp'] += 50
            p = self.game.db.get_player()
            gold = p['gold'] + b.rewards['gold']
            xp = p['xp'] + b.rewards['xp']
            level = p['level']
            while xp >= level * 100:
                xp -= level * 100
                level += 1
            battles_won = p['battles_won'] + 1
            self.game.db.update_player(gold=gold, xp=xp, level=level, battles_won=battles_won)
            self.game.db.set_won(b.region_id, b.battle_idx, 1)
            self.game.change_screen(VictoryScreen(self.game, self.battle, self))
        else:
            play_sfx('defeat')
            self.game.change_screen(DefeatScreen(self.game, self.battle, self))

    def update(self, dt):
        self.battle.update(dt)
        self.pause_btn.update(pygame.mouse.get_pos())
        if self.battle.ended and not self.finalized and self.battle.end_timer > 1.5:
            self._finalize()

    def draw(self, surf):
        b = self.battle
        # battlefield bg
        pygame.draw.rect(surf, (40, 70, 50), pygame.Rect(60, 100, 1160, 450))
        # river
        pygame.draw.rect(surf, (40, 80, 140), pygame.Rect(620, 100, 40, 450))
        # bridges
        pygame.draw.rect(surf, (150, 120, 80), pygame.Rect(620, 170, 40, 30))
        pygame.draw.rect(surf, (150, 120, 80), pygame.Rect(620, 420, 40, 30))
        # lanes
        pygame.draw.line(surf, (60, 100, 60), (60, 310), (1220, 310), 1)

        # top bar
        pygame.draw.rect(surf, DARK, pygame.Rect(0, 0, WIDTH, 70))
        pygame.draw.rect(surf, GOLD, pygame.Rect(0, 70, WIDTH, 2))
        # player HP
        p_hp = b.player_castle.hp
        e_hp = b.enemy_castle.hp
        draw_text(surf, f"Player Castle: {int(p_hp)}", (20, 10), 18, WHITE)
        bar = pygame.Rect(20, 35, 300, 16)
        pygame.draw.rect(surf, DARK, bar)
        pygame.draw.rect(surf, GREEN, (bar.x, bar.y, int(bar.w * max(0, p_hp / b.player_castle.max_hp)), bar.h))
        pygame.draw.rect(surf, WHITE, bar, 1)
        # enemy
        draw_text(surf, f"Enemy Castle: {int(e_hp)}", (WIDTH - 20, 10), 18, WHITE) if False else None
        draw_text(surf, f"Enemy Castle: {int(e_hp)}", (WIDTH - 320, 10), 18, WHITE)
        bar2 = pygame.Rect(WIDTH - 320, 35, 300, 16)
        pygame.draw.rect(surf, DARK, bar2)
        pygame.draw.rect(surf, RED, (bar2.x, bar2.y, int(bar2.w * max(0, e_hp / b.enemy_castle.max_hp)), bar2.h))
        pygame.draw.rect(surf, WHITE, bar2, 1)
        # timer
        mm = int(b.match_time) // 60
        ss = int(b.match_time) % 60
        draw_text(surf, f"{mm}:{ss:02d}", (WIDTH//2, 35), 32, GOLD, bold=True, center=True)

        # towers
        for t in b.player_towers + b.enemy_towers:
            col = LBLUE if t.team == 'player' else RED
            if t.hit_flash > 0: col = WHITE
            pygame.draw.rect(surf, (60, 60, 90), (int(t.x)-22, int(t.y)-40, 44, 80))
            pygame.draw.rect(surf, col, (int(t.x)-18, int(t.y)-36, 36, 70), 2)
            pygame.draw.circle(surf, col, (int(t.x), int(t.y)-10), 10)
            # hp bar
            bar = pygame.Rect(int(t.x)-25, int(t.y)+45, 50, 6)
            pygame.draw.rect(surf, DARK, bar)
            pygame.draw.rect(surf, GREEN, (bar.x, bar.y, int(bar.w * t.hp/t.max_hp), bar.h))
            draw_text(surf, str(int(t.hp)), (int(t.x), int(t.y)+58), 12, WHITE, center=True)

        # castles
        for c in [b.player_castle, b.enemy_castle]:
            col = GOLD if c.team == 'player' else RED
            if c.hit_flash > 0: col = WHITE
            x, y = int(c.x), int(c.y)
            pygame.draw.polygon(surf, (60, 60, 90), [(x-40, y+40), (x+40, y+40), (x+40, y-20), (x+20, y-40), (x-20, y-40), (x-40, y-20)])
            pygame.draw.polygon(surf, col, [(x-40, y+40), (x+40, y+40), (x+40, y-20), (x+20, y-40), (x-20, y-40), (x-40, y-20)], 2)
            bar = pygame.Rect(x-45, y+48, 90, 8)
            pygame.draw.rect(surf, DARK, bar)
            pygame.draw.rect(surf, GREEN if c.team=='player' else RED, (bar.x, bar.y, int(bar.w * c.hp/c.max_hp), bar.h))
            draw_text(surf, str(int(c.hp)), (x, y+64), 12, WHITE, center=True)

        # units
        for u in b.player_units + b.enemy_units:
            col = u.color
            if u.hit_flash > 0: col = WHITE
            x, y = int(u.x), int(u.y)
            if u.flying:
                pygame.draw.circle(surf, col, (x, y), u.radius)
                pygame.draw.circle(surf, WHITE, (x, y), u.radius, 2)
                # wings
                pygame.draw.line(surf, col, (x-u.radius-8, y-6), (x+u.radius+8, y-6), 3)
            else:
                pygame.draw.rect(surf, col, (x-u.radius, y-u.radius, u.radius*2, u.radius*2), border_radius=4)
                pygame.draw.rect(surf, WHITE if u.team=='player' else RED, (x-u.radius, y-u.radius, u.radius*2, u.radius*2), 1, border_radius=4)
            # hp bar
            hb = pygame.Rect(x-18, y-u.radius-10, 36, 4)
            pygame.draw.rect(surf, DARK, hb)
            pygame.draw.rect(surf, GREEN, (hb.x, hb.y, int(hb.w * u.hp/u.max_hp), hb.h))

        # projectiles
        for p in b.projectiles:
            pygame.draw.circle(surf, p.color, (int(p.x), int(p.y)), 5)
            pygame.draw.circle(surf, WHITE, (int(p.x), int(p.y)), 5, 1)

        # particles
        for pt in b.particles:
            alpha = int(255 * (pt.life / pt.max_life))
            s = pygame.Surface((pt.size*2, pt.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*pt.color, alpha), (pt.size, pt.size), pt.size)
            surf.blit(s, (pt.x - pt.size, pt.y - pt.size))

        # damage numbers
        for d in b.damage_numbers:
            alpha = int(255 * (d.life / 0.9))
            color = (*d.color, alpha)
            f = get_font(18, True)
            img = f.render(str(d.amount), True, d.color)
            img.set_alpha(alpha)
            surf.blit(img, (d.x, d.y))

        # selected card outline on battlefield
        if b.selected_card_idx >= 0 and not b.question:
            cid = b.player_hand[b.selected_card_idx]
            c = CARD_DEFS[cid]
            if c['type'] not in ('spell', 'spell_heal'):
                pygame.draw.rect(surf, (*GOLD, 60), pygame.Rect(60, 100, 580, 450), 3)

        # bottom bar
        pygame.draw.rect(surf, DARK, pygame.Rect(0, 550, WIDTH, 170))
        pygame.draw.rect(surf, GOLD, pygame.Rect(0, 550, WIDTH, 2))

        # energy panel
        draw_text(surf, "Energy", (185, 562), 18, GOLD, bold=True, center=True)
        draw_text(surf, f"{int(b.player_energy)}/{b.max_energy}", (185, 590), 28, WHITE, bold=True, center=True)
        for i in range(10):
            r = pygame.Rect(40 + i*30, 615, 24, 20)
            filled = (i+1) <= int(b.player_energy)
            pygame.draw.rect(surf, ROYAL_BLUE if filled else (40, 40, 60), r, border_radius=3)
            pygame.draw.rect(surf, GOLD if filled else GRAY, r, 1, border_radius=3)

        # cards
        for i, r in enumerate(self.card_rects):
            cid = b.player_hand[i]
            c = CARD_DEFS[cid]
            disabled = c['cost'] > b.player_energy or (b.card_lockout.get(cid, 0) > time.time())
            selected = (b.selected_card_idx == i)
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_card_face(surf, cid, r.x, r.y, r.w, r.h, selected, disabled, hover)
            draw_text(surf, str(i+1), (r.x + 8, r.y + r.h - 8), 14, GOLD, bold=True, center=True)

        # info panel
        info_r = pygame.Rect(940, 562, 320, 148)
        draw_panel(surf, info_r, (20, 30, 60), GOLD)
        if b.selected_card_idx >= 0:
            cid = b.player_hand[b.selected_card_idx]
            c = CARD_DEFS[cid]
            draw_text(surf, c['name'], (info_r.x + 10, info_r.y + 8), 18, GOLD, bold=True)
            lines = [f"Cost: {c['cost']}"]
            if 'hp' in c: lines.append(f"HP: {int(c['hp'])}")
            if 'dmg' in c and c['dmg'] > 0: lines.append(f"DMG: {int(c['dmg'])}")
            if 'range' in c: lines.append(f"Range: {int(c['range'])}")
            lines.append(f"Type: {c['type']}")
            lines.append(c.get('desc',''))
            yy = info_r.y + 32
            for ln in lines:
                draw_text(surf, ln, (info_r.x + 10, yy), 13, CREAM); yy += 18
        else:
            draw_text(surf, "Select a card, then click", (info_r.x + 10, info_r.y + 20), 14, CREAM)
            draw_text(surf, "the battlefield to deploy.", (info_r.x + 10, info_r.y + 40), 14, CREAM)
            draw_text(surf, "Spells can target anywhere.", (info_r.x + 10, info_r.y + 60), 13, CREAM)
            draw_text(surf, f"Question frequency: every {self.game.db.get_setting('question_freq', 1)} card(s)",
                      (info_r.x + 10, info_r.y + 90), 12, GOLD)

        # message
        if b.message_timer > 0:
            draw_text(surf, b.message, (WIDTH//2, 530), 22, GOLD, bold=True, center=True)

        # pause btn
        self.pause_btn.draw(surf)

        # Question popup
        if b.question:
            self._draw_question(surf)

        # help
        if b.help_timer > 0:
            help_txt = "Solve the multiplication to deploy! Press 1-4 or click."
            draw_text(surf, help_txt, (WIDTH//2, 90), 18, GOLD, bold=True, center=True)

        # End overlay
        if b.ended:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            surf.blit(s, (0, 0))
            if b.result == 'win':
                draw_text(surf, "VICTORY!", (WIDTH//2, 300), 72, GOLD, bold=True, center=True)
            elif b.result == 'lose':
                draw_text(surf, "DEFEAT", (WIDTH//2, 300), 72, RED, bold=True, center=True)
            else:
                draw_text(surf, "DRAW", (WIDTH//2, 300), 72, CREAM, bold=True, center=True)
            if b.end_timer > 1.5:
                draw_text(surf, "Click to continue", (WIDTH//2, 380), 22, CREAM, center=True)

    def _draw_question(self, surf):
        q = self.battle.question
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))
        panel = pygame.Rect(WIDTH//2 - 350, 180, 700, 380)
        draw_panel(surf, panel, (25, 35, 70), GOLD)
        draw_text(surf, "Multiplication Challenge!", (WIDTH//2, panel.y + 30), 28, GOLD, bold=True, center=True)
        draw_text(surf, f"{q['a']} × {q['b']} = ?", (WIDTH//2, panel.y + 100), 60, WHITE, bold=True, center=True)
        self.option_rects = []
        for i, opt in enumerate(q['options']):
            col = i % 2
            row = i // 2
            x = panel.x + 60 + col * 300
            y = panel.y + 170 + row * 75
            r = pygame.Rect(x, y, 260, 60)
            self.option_rects.append(r)
            hover = r.collidepoint(pygame.mouse.get_pos()) and not q['feedback']
            bg = ROYAL_BLUE if not hover else (60, 100, 200)
            if q['feedback'] == 'correct' and opt == q['answer']:
                bg = GREEN
            if q['feedback'] == 'wrong' and opt == q['answer']:
                bg = GREEN
            pygame.draw.rect(surf, bg, r, border_radius=8)
            pygame.draw.rect(surf, GOLD, r, 2, border_radius=8)
            draw_text(surf, f"{i+1}. {opt}", r.center, 28, WHITE, bold=True, center=True)
        if q['feedback'] == 'correct':
            draw_text(surf, "Correct! Deploying...", (WIDTH//2, panel.bottom - 30), 22, GREEN, bold=True, center=True)
        elif q['feedback'] == 'wrong':
            draw_text(surf, f"Wrong! The answer was {q['answer']}", (WIDTH//2, panel.bottom - 30), 22, RED, bold=True, center=True)


class VictoryScreen(Screen):
    def __init__(self, game, battle, parent_screen):
        super().__init__(game)
        self.battle = battle
        self.parent = parent_screen
        self.t = 0.0
        self.continue_btn = Button(WIDTH//2 - 120, 560, 240, 55, "Continue",
                                    lambda: game.change_screen(WorldMapScreen(game)))

    def handle_event(self, e):
        self.continue_btn.handle_event(e)

    def update(self, dt):
        self.t += dt
        self.continue_btn.update(pygame.mouse.get_pos())

    def draw(self, surf):
        draw_bg(surf, (30, 25, 10), (10, 8, 20))
        draw_text(surf, "VICTORY!", (WIDTH//2, 100), 82, GOLD, bold=True, center=True)
        for i in range(8):
            x = 100 + i*140
            y = 200 + int(math.sin(self.t*2 + i)*10)
            pygame.draw.circle(surf, GOLD, (x, y), 8)
        draw_text(surf, "Rewards", (WIDTH//2, 260), 36, CREAM, bold=True, center=True)
        draw_text(surf, f"+{self.battle.rewards['gold']} Gold", (WIDTH//2, 320), 28, GOLD, center=True)
        draw_text(surf, f"+{self.battle.rewards['xp']} XP", (WIDTH//2, 360), 28, LBLUE, center=True)
        if self.battle.battle_def.get('boss'):
            draw_text(surf, "Boss Defeated!", (WIDTH//2, 420), 32, PURPLE, bold=True, center=True)
            draw_text(surf, "Next region may be unlocked!", (WIDTH//2, 460), 22, GOLD, center=True)
        self.continue_btn.draw(surf)


class DefeatScreen(Screen):
    def __init__(self, game, battle, parent_screen):
        super().__init__(game)
        self.buttons = [
            Button(WIDTH//2 - 260, 500, 240, 55, "Retry",
                   lambda: game.change_screen(BattleScreen(game, battle.region_id, battle.battle_idx, battle.difficulty))),
            Button(WIDTH//2 + 20, 500, 240, 55, "Back to Map",
                   lambda: game.change_screen(WorldMapScreen(game))),
        ]

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)

    def update(self, dt):
        for b in self.buttons: b.update(pygame.mouse.get_pos())

    def draw(self, surf):
        draw_bg(surf, (30, 10, 10), (10, 5, 15))
        draw_text(surf, "DEFEAT", (WIDTH//2, 200), 90, RED, bold=True, center=True)
        draw_text(surf, "Your castle has fallen...", (WIDTH//2, 320), 26, CREAM, center=True)
        draw_text(surf, "Practice your multiplication to strengthen your forces!",
                  (WIDTH//2, 370), 20, GOLD, center=True)
        for b in self.buttons: b.draw(surf)


class PauseScreen(Screen):
    def __init__(self, game, battle_screen):
        super().__init__(game)
        self.parent = battle_screen
        self.buttons = [
            Button(WIDTH//2 - 150, 280, 300, 55, "Resume",
                   lambda: game.change_screen(battle_screen)),
            Button(WIDTH//2 - 150, 345, 300, 55, "Main Menu",
                   lambda: game.change_screen(MainMenuScreen(game))),
            Button(WIDTH//2 - 150, 410, 300, 55, "Settings",
                   lambda: game.change_screen(SettingsScreen(game, back=battle_screen))),
        ]

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.game.change_screen(self.parent)

    def update(self, dt):
        for b in self.buttons: b.update(pygame.mouse.get_pos())

    def draw(self, surf):
        self.parent.draw(surf)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surf.blit(s, (0, 0))
        draw_text(surf, "PAUSED", (WIDTH//2, 180), 64, GOLD, bold=True, center=True)
        for b in self.buttons: b.draw(surf)


class DeckBuilderScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.deck = game.db.get_deck()
        self.selected_slot = -1
        self.back_btn = Button(20, 660, 120, 45, "Back",
                                lambda: game.change_screen(MainMenuScreen(game)))
        self.save_btn = Button(WIDTH - 160, 660, 140, 45, "Save", self.save_deck)
        self.card_list = sorted(ALL_CARDS)

    def save_deck(self):
        if len(set(self.deck)) == 8 and len(self.deck) == 8:
            self.game.db.set_deck(self.deck)
            self.game.db.set_setting('deck_saved', True)

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        self.save_btn.handle_event(e)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            # Check deck slots
            for i in range(8):
                r = self._slot_rect(i)
                if r.collidepoint(e.pos):
                    self.selected_slot = i
                    return
            # Check collection
            for i, cid in enumerate(self.card_list):
                r = self._collection_rect(i)
                if r.collidepoint(e.pos):
                    self.add_card(cid)
                    return

    def add_card(self, cid):
        if self.selected_slot < 0:
            return
        # Count occurrences
        if cid in self.deck:
            if self.deck.count(cid) > 0 and self.selected_slot >= 0:
                self.deck[self.selected_slot] = cid
        else:
            self.deck[self.selected_slot] = cid

    def _slot_rect(self, i):
        return pygame.Rect(40 + (i % 4) * 145, 130 + (i // 4) * 165, 130, 150)

    def _collection_rect(self, i):
        cols = 8
        return pygame.Rect(40 + (i % cols) * 150, 470 + (i // cols) * 40, 140, 35)

    def update(self, dt):
        self.back_btn.update(pygame.mouse.get_pos())
        self.save_btn.update(pygame.mouse.get_pos())

    def draw(self, surf):
        draw_bg(surf)
        draw_text(surf, "Deck Builder", (WIDTH//2, 40), 42, GOLD, bold=True, center=True)
        draw_text(surf, "Click a slot, then click a card below to add it.", (WIDTH//2, 90), 16, CREAM, center=True)
        draw_text(surf, f"Deck size: {len(set(self.deck))}/8 unique", (WIDTH//2, 112), 14, GOLD, center=True)
        for i in range(8):
            r = self._slot_rect(i)
            if i < len(self.deck):
                draw_card_face(surf, self.deck[i], r.x, r.y, r.w, r.h, selected=(self.selected_slot==i))
            else:
                pygame.draw.rect(surf, (30,30,50), r, border_radius=6)
                pygame.draw.rect(surf, GRAY, r, 2, border_radius=6)
        # Collection
        draw_text(surf, "Collection", (WIDTH//2, 445), 22, GOLD, bold=True, center=True)
        for i, cid in enumerate(self.card_list):
            r = self._collection_rect(i)
            c = CARD_DEFS[cid]
            in_deck = cid in self.deck
            col = c['color'] if not in_deck else (80, 100, 60)
            pygame.draw.rect(surf, col, r, border_radius=4)
            pygame.draw.rect(surf, RARITY_COLORS[c['rarity']], r, 2, border_radius=4)
            draw_text(surf, c['name'][:12], (r.x + 5, r.y + 8), 12, WHITE)
        self.back_btn.draw(surf)
        self.save_btn.draw(surf)
        if self.selected_slot >= 0:
            draw_text(surf, f"Selected slot {self.selected_slot+1}",
                      (WIDTH//2, 645), 16, GOLD, center=True)


class CollectionScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.back_btn = Button(20, 660, 120, 45, "Back",
                                lambda: game.change_screen(MainMenuScreen(game)))
        self.selected = None
        self.cards_data = game.db.all_cards()
        self.card_list = sorted(ALL_CARDS)

    def _card_rect(self, i):
        cols = 5
        return pygame.Rect(50 + (i % cols) * 240, 120 + (i // cols) * 200, 220, 180)

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, cid in enumerate(self.card_list):
                if self._card_rect(i).collidepoint(e.pos):
                    self.selected = cid
                    return
            # Upgrade button
            if self.selected and hasattr(self, 'upgrade_rect'):
                if self.upgrade_rect.collidepoint(e.pos):
                    self.upgrade_selected()
            if hasattr(self, 'back_detail_rect') and self.selected:
                if self.back_detail_rect.collidepoint(e.pos):
                    self.selected = None

    def upgrade_selected(self):
        cid = self.selected
        cd = self.cards_data.get(cid, {})
        c = CARD_DEFS[cid]
        level = cd.get('level', 1)
        dupes = cd.get('dupes', 0)
        if level >= 5:
            return
        cost = 100 * level + 50
        dupes_needed = level
        p = self.game.db.get_player()
        if p['gold'] < cost:
            return
        if dupes < dupes_needed:
            # Deduct gold, but require dupes OR allow purchase
            self.game.db.update_player(gold=p['gold'] - cost)
            self.game.db.update_card(cid, level=level+1, dupes=max(0, dupes-dupes_needed))
        else:
            self.game.db.update_player(gold=p['gold'] - cost)
            self.game.db.update_card(cid, level=level+1, dupes=dupes-dupes_needed)
        self.cards_data = self.game.db.all_cards()

    def update(self, dt):
        self.back_btn.update(pygame.mouse.get_pos())

    def draw(self, surf):
        draw_bg(surf)
        draw_text(surf, "Card Collection", (WIDTH//2, 40), 42, GOLD, bold=True, center=True)
        p = self.game.db.get_player()
        draw_text(surf, f"Gold: {p['gold']}", (WIDTH - 200, 40), 22, GOLD, bold=True)
        for i, cid in enumerate(self.card_list):
            r = self._card_rect(i)
            cd = self.cards_data.get(cid, {})
            lvl = cd.get('level', 1)
            draw_card_face(surf, cid, r.x, r.y, r.w, r.h, hover=r.collidepoint(pygame.mouse.get_pos()))
            draw_text(surf, f"Lv {lvl}", (r.x + r.w - 10, r.y + 5), 14, WHITE, bold=True)
        if self.selected:
            self._draw_detail(surf)
        self.back_btn.draw(surf)

    def _draw_detail(self, surf):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surf.blit(s, (0, 0))
        panel = pygame.Rect(WIDTH//2 - 300, 150, 600, 450)
        draw_panel(surf, panel, (25, 35, 70), GOLD)
        cid = self.selected
        c = CARD_DEFS[cid]
        cd = self.cards_data.get(cid, {})
        lvl = cd.get('level', 1)
        dupes = cd.get('dupes', 0)
        draw_text(surf, c['name'], (panel.centerx, panel.y + 30), 32, GOLD, bold=True, center=True)
        draw_text(surf, f"Rarity: {c['rarity']}", (panel.centerx, panel.y + 70), 18, RARITY_COLORS[c['rarity']], center=True)
        draw_text(surf, f"Level: {lvl}/5", (panel.centerx, panel.y + 100), 20, WHITE, center=True)
        info = []
        if 'hp' in c: info.append(f"HP: {int(c['hp'] * (1 + (lvl-1)*0.1))}")
        if 'dmg' in c and c['dmg'] > 0: info.append(f"DMG: {int(c['dmg'] * (1 + (lvl-1)*0.1))}")
        if 'heal' in c: info.append(f"HEAL: {int(c['heal'] * (1 + (lvl-1)*0.1))}")
        info.append(f"Cost: {c['cost']}")
        info.append(f"Type: {c['type']}")
        if 'range' in c: info.append(f"Range: {int(c['range'])}")
        for i, line in enumerate(info):
            draw_text(surf, line, (panel.x + 40, panel.y + 140 + i*25), 18, CREAM)
        draw_text(surf, c.get('desc', ''), (panel.centerx, panel.y + 330), 16, CREAM, center=True)
        # Upgrade
        p = self.game.db.get_player()
        if lvl < 5:
            cost = 100 * lvl + 50
            up_rect = pygame.Rect(panel.centerx - 150, panel.y + 370, 300, 45)
            self.upgrade_rect = up_rect
            can_up = p['gold'] >= cost
            col = EMERALD if can_up else GRAY
            pygame.draw.rect(surf, col, up_rect, border_radius=8)
            pygame.draw.rect(surf, GOLD, up_rect, 2, border_radius=8)
            draw_text(surf, f"Upgrade - {cost} Gold", up_rect.center, 20, WHITE, bold=True, center=True)
            draw_text(surf, f"Duplicates: {dupes}", (panel.centerx, panel.y + 425), 14, GOLD, center=True)
        else:
            draw_text(surf, "MAX LEVEL", (panel.centerx, panel.y + 390), 24, GOLD, bold=True, center=True)
        # close
        close_rect = pygame.Rect(panel.right - 50, panel.y + 10, 40, 40)
        pygame.draw.rect(surf, RED, close_rect, border_radius=6)
        draw_text(surf, "X", close_rect.center, 24, WHITE, bold=True, center=True)
        self.back_detail_rect = close_rect


class PracticeScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.back_btn = Button(20, 660, 120, 45, "Back",
                                lambda: game.change_screen(MainMenuScreen(game)))
        self.question = None
        self.feedback = None
        self.feedback_t = 0.0
        self.start_t = 0.0
        self.option_rects = []
        self.families = [1,2,3,4,5,6,7,8,9,10]
        self.stats = game.mult.overall_stats()

    def _new_question(self):
        a, b = self.game.mult.select_question(self.families)
        self.question = {
            'a': a, 'b': b, 'answer': a*b,
            'options': self.game.mult.make_options(a, b, 4),
        }
        self.start_t = time.time()
        self.feedback = None

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        if not self.question:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._new_question()
            return
        if self.feedback: return
        if e.type == pygame.KEYDOWN and pygame.K_1 <= e.key <= pygame.K_4:
            self._answer(e.key - pygame.K_1)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.option_rects):
                if r.collidepoint(e.pos):
                    self._answer(i)
                    return

    def _answer(self, i):
        q = self.question
        if i >= len(q['options']): return
        choice = q['options'][i]
        rt = time.time() - self.start_t
        correct = (choice == q['answer'])
        self.game.mult.record(q['a'], q['b'], correct, rt)
        self.feedback = 'correct' if correct else 'wrong'
        self.feedback_t = 1.3
        self.stats = self.game.mult.overall_stats()
        if correct: play_sfx('correct')
        else: play_sfx('wrong')

    def update(self, dt):
        self.back_btn.update(pygame.mouse.get_pos())
        if self.feedback:
            self.feedback_t -= dt
            if self.feedback_t <= 0:
                self._new_question()

    def draw(self, surf):
        draw_bg(surf, (20, 30, 50), (10, 15, 30))
        draw_text(surf, "Multiplication Academy", (WIDTH//2, 50), 42, GOLD, bold=True, center=True)
        draw_text(surf, f"Total: {self.stats['total']}  •  Accuracy: {self.stats['accuracy']:.1f}%  •  Mastered: {self.stats['mastered']}/144",
                  (WIDTH//2, 100), 18, CREAM, center=True)
        if not self.question:
            draw_text(surf, "Click to begin practicing!", (WIDTH//2, 350), 30, WHITE, bold=True, center=True)
        else:
            q = self.question
            panel = pygame.Rect(WIDTH//2 - 350, 180, 700, 380)
            draw_panel(surf, panel, (25, 35, 70), GOLD)
            draw_text(surf, f"{q['a']} × {q['b']} = ?", (WIDTH//2, panel.y + 80), 60, WHITE, bold=True, center=True)
            self.option_rects = []
            for i, opt in enumerate(q['options']):
                col = i % 2
                row = i // 2
                r = pygame.Rect(panel.x + 60 + col*300, panel.y + 170 + row*75, 260, 60)
                self.option_rects.append(r)
                bg = ROYAL_BLUE
                if self.feedback == 'correct' and opt == q['answer']: bg = GREEN
                if self.feedback == 'wrong' and opt == q['answer']: bg = GREEN
                if self.feedback == 'wrong' and opt != q['answer']: bg = (100, 50, 50)
                pygame.draw.rect(surf, bg, r, border_radius=8)
                pygame.draw.rect(surf, GOLD, r, 2, border_radius=8)
                draw_text(surf, f"{i+1}. {opt}", r.center, 28, WHITE, bold=True, center=True)
            if self.feedback == 'correct':
                draw_text(surf, "Correct!", (WIDTH//2, panel.bottom - 30), 26, GREEN, bold=True, center=True)
            elif self.feedback == 'wrong':
                draw_text(surf, f"Answer: {q['answer']}", (WIDTH//2, panel.bottom - 30), 26, RED, bold=True, center=True)
        self.back_btn.draw(surf)


class StatsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.back_btn = Button(20, 660, 120, 45, "Back",
                                lambda: game.change_screen(MainMenuScreen(game)))
        self.facts = game.db.all_facts()
        self.stats = game.mult.overall_stats()

    def handle_event(self, e):
        self.back_btn.handle_event(e)

    def update(self, dt):
        self.back_btn.update(pygame.mouse.get_pos())

    def draw(self, surf):
        draw_bg(surf)
        draw_text(surf, "Learning Statistics", (WIDTH//2, 40), 42, GOLD, bold=True, center=True)
        # Summary
        draw_text(surf, f"Total Attempts: {self.stats['total']}", (WIDTH//2 - 300, 100), 20, CREAM)
        draw_text(surf, f"Correct: {self.stats['correct']}", (WIDTH//2 - 300, 130), 20, CREAM)
        draw_text(surf, f"Accuracy: {self.stats['accuracy']:.1f}%", (WIDTH//2 - 300, 160), 20, CREAM)
        draw_text(surf, f"Mastered Facts: {self.stats['mastered']}/144", (WIDTH//2 + 100, 100), 20, GOLD)
        # Grid 1..10
        fact_map = {(f['a'], f['b']): f for f in self.facts}
        cell_w = 44
        cell_h = 32
        start_x = WIDTH//2 - 250
        start_y = 210
        draw_text(surf, "Mastery Grid (row × col)", (WIDTH//2, 185), 18, GOLD, bold=True, center=True)
        for b in range(1, 11):
            draw_text(surf, str(b), (start_x + (b-1)*cell_w + cell_w//2, start_y - 15), 14, WHITE, center=True)
        for a in range(1, 11):
            draw_text(surf, str(a), (start_x - 20, start_y + (a-1)*cell_h + cell_h//2 - 6), 14, WHITE, center=True)
            for b in range(1, 11):
                f = fact_map.get((a, b)) or fact_map.get((b, a))
                mastery = f['mastery'] if f else 0
                if mastery >= 4: col = GREEN
                elif mastery >= 2: col = (200, 200, 60)
                elif mastery >= 1: col = (200, 140, 60)
                else: col = (80, 60, 60)
                r = pygame.Rect(start_x + (b-1)*cell_w, start_y + (a-1)*cell_h, cell_w-2, cell_h-2)
                pygame.draw.rect(surf, col, r, border_radius=3)
                if f and f['attempts'] > 0:
                    draw_text(surf, str(f['attempts']), r.center, 11, BLACK, center=True)
        # Weakest facts
        weak = sorted([f for f in self.facts if f['attempts'] > 0 and f['mastery'] < 3],
                      key=lambda x: (-x['incorrect'], -x['attempts']))[:8]
        draw_text(surf, "Needs Practice:", (WIDTH//2, 560), 20, GOLD, bold=True, center=True)
        for i, f in enumerate(weak):
            col = i % 4
            row = i // 4
            draw_text(surf, f"{f['a']}×{f['b']}: {f['incorrect']} wrong/{f['attempts']}",
                      (WIDTH//2 - 400 + col*220, 595 + row*28), 16, CREAM)
        self.back_btn.draw(surf)


class SettingsScreen(Screen):
    def __init__(self, game, back=None):
        super().__init__(game)
        self.back_screen = back or MainMenuScreen(game)
        self.back_btn = Button(20, 660, 120, 45, "Back", lambda: game.change_screen(self.back_screen))
        self.qfreq_btn = Button(WIDTH//2 - 150, 220, 300, 55, self._q_freq_label(),
                                 self.cycle_q_freq)
        self.mute_btn = Button(WIDTH//2 - 150, 300, 300, 55, self._mute_label(), self.toggle_mute)
        self.reset_btn = Button(WIDTH//2 - 150, 400, 300, 55, "Reset Progress (HOLD)",
                                 self.confirm_reset, color=(120, 40, 40))
        self.reset_confirm_until = 0.0

    def _q_freq_label(self):
        n = self.game.db.get_setting('question_freq', 1)
        if n == 0: return "Questions: OFF"
        return f"Question every {n} card(s)"

    def _mute_label(self):
        return "Sound: OFF" if self.game.db.get_setting('mute', 0) else "Sound: ON"

    def cycle_q_freq(self):
        n = self.game.db.get_setting('question_freq', 1)
        cycle = [1, 2, 3, 0]
        idx = (cycle.index(n) + 1) % len(cycle) if n in cycle else 0
        self.game.db.set_setting('question_freq', cycle[idx])
        self.qfreq_btn.text = self._q_freq_label()

    def toggle_mute(self):
        m = self.game.db.get_setting('mute', 0)
        self.game.db.set_setting('mute', 1 - m)
        if 1 - m: 
            try: pygame.mixer.pause()
            except: pass
        else:
            try: pygame.mixer.unpause()
            except: pass
        self.mute_btn.text = self._mute_label()

    def confirm_reset(self):
        if time.time() - self.reset_confirm_until < 2.0:
            self.game.db.reset()
            self.reset_confirm_until = 0.0
            self.reset_btn.text = "Reset Progress (HOLD)"
        else:
            self.reset_confirm_until = time.time()
            self.reset_btn.text = "Click again to confirm!"

    def handle_event(self, e):
        self.back_btn.handle_event(e)
        self.qfreq_btn.handle_event(e)
        self.mute_btn.handle_event(e)
        self.reset_btn.handle_event(e)

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.back_btn.update(mp)
        self.qfreq_btn.update(mp)
        self.mute_btn.update(mp)
        self.reset_btn.update(mp)
        if self.reset_confirm_until and time.time() - self.reset_confirm_until > 2.0:
            self.reset_confirm_until = 0.0
            self.reset_btn.text = "Reset Progress (HOLD)"

    def draw(self, surf):
        draw_bg(surf)
        draw_text(surf, "Settings", (WIDTH//2, 60), 48, GOLD, bold=True, center=True)
        p = self.game.db.get_player()
        draw_text(surf, f"Level {p['level']}  •  XP {p['xp']}  •  Gold {p['gold']}  •  Battles Won {p['battles_won']}",
                  (WIDTH//2, 140), 20, CREAM, center=True)
        self.qfreq_btn.draw(surf)
        self.mute_btn.draw(surf)
        self.reset_btn.draw(surf)
        self.back_btn.draw(surf)


# ---------------------------------------------------------------------------
# GAME
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiply Royale - Rise of the Number Kings")
        self.clock = pygame.time.Clock()
        self.running = True
        try:
            self.db = SaveDB(get_data_dir() / 'save.db')
        except Exception as e:
            print("DB error, using memory save:", e)
            self.db = SaveDB(':memory:')
        self.mult = MultEngine(self.db)
        init_sfx()
        self.current_screen = MainMenuScreen(self)

    def change_screen(self, screen):
        self.current_screen = screen

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    try:
                        self.current_screen.handle_event(event)
                    except Exception as e:
                        print("Event error:", e)
            try:
                self.current_screen.update(dt)
            except Exception as e:
                print("Update error:", e)
            try:
                self.current_screen.draw(self.screen)
            except Exception as e:
                print("Draw error:", e)
            pygame.display.flip()
        try:
            self.db.conn.close()
        except Exception:
            pass
        pygame.quit()


if __name__ == '__main__':
    try:
        Game().run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)