import pgzrun
import pygame
import random
import math
import os

# 定义游戏相关属性
TITLE = '喵了个喵'
WIDTH = 542
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 50
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []
game_state = 'menu'  # 初始状态为主菜单
start_time = 0
time_limit = 0  # 游戏时间限制
difficulty = ''  # 当前选择的难度

# 加载字体  
font = pygame.font.Font(None, 36)  # 使用默认字体，大小36
large_font = pygame.font.Font(None, 72)

# 创建主菜单按钮
easy_button = Actor('easy_button', pos=(WIDTH // 2 + 25, 400))
medium_button = Actor('medium_button', pos=(WIDTH // 2 + 25, 500))
hard_button = Actor('hard_button', pos=(WIDTH // 2 + 25, 600))

# 创建结束界面的按钮
menu_button = Actor('menu_button', pos=(WIDTH // 2, 450))
retry_button = Actor('retry_button', pos=(WIDTH // 2, 450))

def initialize_tiles():
    global tiles, docks
    tiles = []
    docks = []
    ts = list(range(1, 9)) * 12  # 8种牌，每种12张，总计96张
    random.shuffle(ts)
    n = 0
    for k in range(6):  # 6层
        for i in range(6 - k):  # 每层减少行数
            for j in range(6 - k):  # 每层减少列数
                if n >= len(ts):
                    break
                t = ts[n]
                n += 1
                tile = Actor(f'tile{t}')
                tile.pos = 150 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9
                tile.tag = t
                tile.layer = k
                tile.status = 1 if k == 5 else 0  # 顶层可点击
                tiles.append(tile)

    # 放置下方额外的5张牌
    for i in range(5):  # 剩余5张牌放在下面
        if n >= len(ts):  # 防止超出牌的数量
            break
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        tile.pos = 160 + i * tile.width, 516  # 设置下方4张牌的位置
        tile.tag = t
        tile.layer = 0  # 设置为最低层
        tile.status = 1  # 可点
        tiles.append(tile)

# 游戏帧绘制函数
def draw():
    screen.clear()

    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()
    elif game_state == 'win':
        draw_win()
    elif game_state == 'lose':
        draw_lose()

# 绘制主菜单
def draw_menu():
    screen.blit('back8', (0, 0))
    easy_button.draw()
    medium_button.draw()
    hard_button.draw()

# 游戏帧绘制函数
def draw_game():
    screen.blit('back5', (0, 0))
    for tile in tiles:
        tile.draw()
        if tile.status == 0:
            screen.blit('mask', tile.topleft)
    for i, tile in enumerate(docks):
        tile.left = (DOCK.x + i * T_WIDTH)
        tile.top = DOCK.y
        tile.draw()

    # 显示倒计时  
    elapsed_time = pygame.time.get_ticks() - start_time  
    remaining_time = (time_limit - elapsed_time) // 1000  
    if remaining_time < 0:  
        remaining_time = 0  
    text = font.render(f"Time Left: {remaining_time}s", True, (255, 255, 255))  # 渲染文本  
    screen.blit(text, (50, 10))  # 绘制文本到屏幕上 
      
# 绘制胜利界面
def draw_win():
    screen.blit('back6', (0, 0))
    win_text = large_font.render("You Win!", True, (255, 255, 255))
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2 - 150))
    menu_button.draw()

# 绘制失败界面
def draw_lose():
    screen.blit('back4', (0, 0))
    lose_text = large_font.render("Game Over", True, (255, 255, 255))
    screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - lose_text.get_height() // 2 + 120))
    retry_button.draw()

# 游戏循环更新函数
def update():
    global game_state

    if game_state == 'playing':
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > time_limit:
            game_state = 'lose'

        if len(tiles) == 0:
            game_state = 'win'
        # 超过7张，失败
        if len(docks) >= 7:
            game_state = 'lose'

# 游戏开始
def start_game(selected_difficulty):
    global start_time, time_limit, game_state, difficulty

    difficulty = selected_difficulty
    initialize_tiles()

    if difficulty == 'easy':
        time_limit = 180000  # 3分钟
    elif difficulty == 'medium':
        time_limit = 150000  # 1分30秒
    elif difficulty == 'hard':
        time_limit = 60000  # 1分钟

    start_time = pygame.time.get_ticks()
    game_state = 'playing'

# 鼠标点击响应
def on_mouse_down(pos):
    global game_state

    if game_state == 'menu':
        if easy_button.collidepoint(pos):
            start_game('easy')
        elif medium_button.collidepoint(pos):
            start_game('medium')
        elif hard_button.collidepoint(pos):
            start_game('hard')

    elif game_state == 'win':
        if menu_button.collidepoint(pos):
            game_state = 'menu'

    elif game_state == 'lose':
        if retry_button.collidepoint(pos):
            start_game(difficulty)

    elif game_state == 'playing':
        handle_tile_click(pos)

# 处理牌点击逻辑
def handle_tile_click(pos):
    global docks

    if len(docks) >= 7 or len(tiles) == 0:
        return
    for tile in reversed(tiles):
        if tile.status == 1 and tile.collidepoint(pos):
            tile.status = 2
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]
            if len(docks) - len(diff) < 2:
                docks.append(tile)
            else:
                docks = diff
            update_tile_status(tile)
            return

# 更新牌的状态
def update_tile_status(tile):
    for down in tiles:
        if down.layer == tile.layer - 1 and down.colliderect(tile):
            for up in tiles:
                if up.layer == down.layer + 1 and up.colliderect(down):
                    break
            else:
                down.status = 1

pgzrun.go()
