"""
贪吃蛇游戏 - 带配置界面
使用方向键控制蛇的移动
"""

import pygame
import random
import sys
import os

# 初始化pygame
pygame.init()

# 游戏配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# 预设颜色
COLORS = {
    '红色': (255, 0, 0),
    '绿色': (0, 255, 0),
    '蓝色': (0, 0, 255),
    '黄色': (255, 255, 0),
    '紫色': (128, 0, 128),
    '青色': (0, 255, 255),
    '橙色': (255, 165, 0),
    '粉色': (255, 192, 203)
}

# 速度配置 - 快为基准，中为快的75%，慢为快的50%
BASE_SPEED = 10
SPEEDS = {
    '快': BASE_SPEED,
    '中': int(BASE_SPEED * 0.75),
    '慢': int(BASE_SPEED * 0.5)
}

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# 获取中文字体
def get_chinese_font(size):
    """尝试获取支持中文的字体"""
    # Windows 中文字体列表
    chinese_fonts = [
        'microsoftyahei',
        'simhei',
        'simsun',
        'nsimsun',
        'Microsoft YaHei',
        'SimHei',
        'SimSun',
        'NSimSun',
        'PMingLiU',
        'MingLiU'
    ]

    # 尝试使用系统中文字体
    for font_name in chinese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试字体是否能正确渲染中文
            test_surf = font.render('测试', True, WHITE)
            return font
        except:
            continue

    # 如果都失败，使用默认字体
    return pygame.font.Font(None, size)


class Toggle:
    """开关组件"""
    def __init__(self, x, y, width, height, default_state=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = default_state  # False=关, True=开
        self.hover = False

    def is_on(self):
        return self.state

    def toggle(self):
        self.state = not self.state
        return self.state

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and event.button == 1:
                self.toggle()
                return True
        return False

    def draw(self, surface, font):
        # 绘制开关背景
        bg_color = GRAY if not self.state else GREEN
        if self.hover:
            bg_color = LIGHT_GRAY

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        # 绘制开关状态
        circle_width = min(self.rect.width - 10, self.rect.height - 10)
        circle_x = self.rect.x + self.rect.width // 2

        if self.state:
            # 开状态 - 绿色圆圈
            pygame.draw.circle(surface, WHITE, (circle_x - circle_width // 4, self.rect.centery), circle_width // 4)
        else:
            # 关状态 - 灰色圆圈
            pygame.draw.circle(surface, DARK_GRAY, (circle_x + circle_width // 4, self.rect.centery), circle_width // 4)


class Dropdown:
    """下拉菜单组件"""
    def __init__(self, x, y, width, height, options, default_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        self.hover = False
        self.button_rect = pygame.Rect(x + width - height, y, height, height)
        self.max_visible = 3
        self.item_height = height
        self.dropdown_rect = pygame.Rect(x, y, width, height * min(len(options), self.max_visible))

    def get_selected(self):
        return self.options[self.selected_index]

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.is_open:
                    # 检查点击了哪个选项
                    for i, option in enumerate(self.options):
                        option_rect = pygame.Rect(
                            self.rect.x,
                            self.rect.y + (i + 1) * self.item_height,
                            self.rect.width,
                            self.item_height
                        )
                        if option_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.is_open = False
                            return True
                    # 点击外部关闭下拉菜单
                    if not self.dropdown_rect.collidepoint(event.pos):
                        self.is_open = False
                else:
                    # 检查是否点击了下拉按钮
                    if self.rect.collidepoint(event.pos):
                        self.is_open = not self.is_open
                        return True
        return False

    def draw(self, surface, font):
        # 绘制主按钮
        pygame.draw.rect(surface, WHITE if not self.hover else LIGHT_GRAY, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLUE, self.rect, 2, border_radius=5)

        # 绘制选中的文本
        text = font.render(self.options[self.selected_index], True, BLACK)
        text_rect = text.get_rect(center=(self.rect.centerx - self.item_height // 2, self.rect.centery))
        surface.blit(text, text_rect)

        # 绘制下拉箭头
        arrow_points = [
            (self.button_rect.centerx, self.button_rect.centery - 5),
            (self.button_rect.centerx - 5, self.button_rect.centery),
            (self.button_rect.centerx + 5, self.button_rect.centery)
        ]
        if self.is_open:
            arrow_points = [
                (self.button_rect.centerx, self.button_rect.centery + 3),
                (self.button_rect.centerx - 5, self.button_rect.centery - 4),
                (self.button_rect.centerx + 5, self.button_rect.centery - 4)
            ]
        pygame.draw.polygon(surface, BLACK, arrow_points)

        # 绘制下拉选项
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i + 1) * self.item_height,
                    self.rect.width,
                    self.item_height
                )

                # 高亮鼠标悬停的选项
                mouse_pos = pygame.mouse.get_pos()
                bg_color = LIGHT_GRAY if option_rect.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(surface, bg_color, option_rect)
                pygame.draw.rect(surface, BLUE, option_rect, 1)

                # 绘制选项文本
                option_text = font.render(option, True, BLACK)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                surface.blit(option_text, option_text_rect)


class ColorPicker:
    """颜色选择器 - 一行显示所有颜色"""
    def __init__(self, x, y, button_size, spacing, colors, default_name):
        self.x = x
        self.y = y
        self.button_size = button_size
        self.spacing = spacing
        self.colors = colors
        self.color_names = list(colors.keys())
        self.selected_name = default_name
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        for i, (name, color) in enumerate(self.colors.items()):
            x = self.x + i * (self.button_size + self.spacing)
            rect = pygame.Rect(x, self.y, self.button_size, self.button_size)
            self.buttons.append({'rect': rect, 'name': name, 'color': color})

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for btn in self.buttons:
                    if btn['rect'].collidepoint(event.pos):
                        self.selected_name = btn['name']
                        return True
        return False

    def get_selected(self):
        return self.colors[self.selected_name]

    def get_selected_name(self):
        return self.selected_name

    def draw(self, surface, font):
        for btn in self.buttons:
            # 绘制颜色按钮
            pygame.draw.rect(surface, btn['color'], btn['rect'], border_radius=5)

            # 如果选中，加粗白色边框
            if btn['name'] == self.selected_name:
                # 白色边框
                pygame.draw.rect(surface, WHITE, btn['rect'], 4, border_radius=5)
            else:
                # 灰色细边框
                pygame.draw.rect(surface, GRAY, btn['rect'], 1, border_radius=5)


class Button:
    """简单的按钮类"""
    def __init__(self, x, y, width, height, text, color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.action = action
        self.hover = False

    def draw(self, surface, font):
        color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255)) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, WHITE if sum(self.color) < 500 else BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and self.action:
                self.action()


class ConfigMenu:
    """配置菜单界面"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('贪吃蛇 - 配置')
        self.clock = pygame.time.Clock()

        # 使用中文字体
        self.font_title = get_chinese_font(60)
        self.font = get_chinese_font(32)
        self.font_small = get_chinese_font(28)

        # 创建UI组件
        self.create_ui()

    def create_ui(self):
        # 第一行：标题区域 (0-100px)
        # 第二行：游戏速度 (Y=120px)
        label_x = 250  # 文案后面的距离 + 向右偏移150px
        self.speed_dropdown = Dropdown(label_x, 115, 150, 40, list(SPEEDS.keys()), 0)

        # 第三行：蛇颜色 (Y=180px)
        self.snake_color_picker = ColorPicker(label_x, 170, 50, 10, COLORS, '绿色')

        # 第四行：食物颜色 (Y=240px)
        self.food_color_picker = ColorPicker(label_x, 230, 50, 10, COLORS, '黄色')

        # 第五行：自动开关 (Y=300px)
        # 在"自动："后面100px的位置添加开关
        toggle_x = 250
        self.auto_toggle = Toggle(toggle_x, 290, 80, 40, False)

        # 第六行：开始游戏按钮 (Y=380px) - 向右偏移
        self.start_btn = Button(450, 370, 200, 60, '开始游戏', GREEN, self.start_game)

    def start_game(self):
        # 保存配置并开始游戏
        config = {
            'speed': SPEEDS[self.speed_dropdown.get_selected()],
            'snake_color': self.snake_color_picker.get_selected(),
            'food_color': self.food_color_picker.get_selected(),
            'auto_mode': self.auto_toggle.is_on()
        }
        game = Game(config)
        game.run()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # 处理UI事件
                self.speed_dropdown.handle_event(event)
                self.snake_color_picker.handle_event(event)
                self.food_color_picker.handle_event(event)
                self.auto_toggle.handle_event(event)
                self.start_btn.handle_event(event)

            # 绘制
            self.draw()

            self.clock.tick(60)

    def draw(self):
        self.screen.fill(BLACK)

        # 第一行：标题 (0-100px) - 完全居中
        title = self.font_title.render('游戏配置', True, WHITE)
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = (100 - title.get_height()) // 2
        self.screen.blit(title, (title_x, title_y))

        # 第二行：游戏速度 (Y=120px)
        speed_label = self.font.render('游戏速度：', True, WHITE)
        self.screen.blit(speed_label, (50, 120))
        self.speed_dropdown.draw(self.screen, self.font)

        # 第三行：蛇颜色 (Y=180px)
        snake_label = self.font.render('蛇颜色：', True, WHITE)
        self.screen.blit(snake_label, (50, 175))
        self.snake_color_picker.draw(self.screen, self.font_small)

        # 第四行：食物颜色 (Y=240px)
        food_label = self.font.render('食物颜色：', True, WHITE)
        self.screen.blit(food_label, (50, 235))
        self.food_color_picker.draw(self.screen, self.font_small)

        # 第五行：自动开关 (Y=300px)
        auto_label = self.font.render('自动：', True, WHITE)
        self.screen.blit(auto_label, (50, 295))
        self.auto_toggle.draw(self.screen, self.font_small)

        # 显示自动状态
        auto_status = "开启" if self.auto_toggle.is_on() else "关闭"
        status_text = self.font_small.render(f'({auto_status})', True, GRAY)
        self.screen.blit(status_text, (340, 295))

        # 第六行：开始游戏按钮 (Y=380px)
        self.start_btn.draw(self.screen, self.font)

        pygame.display.flip()


class Snake:
    def __init__(self, color):
        self.length = 1
        # 初始化位置使用网格对齐的坐标
        center_x = (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        self.positions = [(center_x, center_y)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = color
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new_x = (cur[0] + x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (cur[1] + y * GRID_SIZE) % SCREEN_HEIGHT
        new = (new_x, new_y)

        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 1
        center_x = (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        self.positions = [(center_x, center_y)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def get_next_direction(self, food_position):
        """自动寻路：计算朝向食物的最佳方向"""
        head_x, head_y = self.get_head_position()
        food_x, food_y = food_position

        # 计算到食物的距离
        dx = food_x - head_x
        dy = food_y - head_y

        # 确定主要方向（距离远的轴优先）
        if abs(dx) > abs(dy):
            # 水平距离更大，优先水平移动
            preferred_dir = RIGHT if dx > 0 else LEFT
            secondary_dir = UP if dy > 0 else DOWN
        else:
            # 垂直距离更大，优先垂直移动
            preferred_dir = DOWN if dy > 0 else UP
            secondary_dir = RIGHT if dx > 0 else LEFT

        # 检查首选方向是否可用
        next_x = head_x + preferred_dir[0] * GRID_SIZE
        next_y = head_y + preferred_dir[1] * GRID_SIZE
        next_pos = ((next_x % SCREEN_WIDTH), (next_y % SCREEN_HEIGHT))

        if next_pos not in self.positions:
            return preferred_dir

        # 首选方向不可用，尝试次要方向
        next_x = head_x + secondary_dir[0] * GRID_SIZE
        next_y = head_y + secondary_dir[1] * GRID_SIZE
        next_pos = ((next_x % SCREEN_WIDTH), (next_y % SCREEN_HEIGHT))

        if next_pos not in self.positions:
            return secondary_dir

        # 如果两个方向都不可用，尝试其他方向
        for direction in [UP, DOWN, LEFT, RIGHT]:
            if direction == preferred_dir or direction == secondary_dir:
                continue
            next_x = head_x + direction[0] * GRID_SIZE
            next_y = head_y + direction[1] * GRID_SIZE
            next_pos = ((next_x % SCREEN_WIDTH), (next_y % SCREEN_HEIGHT))
            if next_pos not in self.positions:
                return direction

        # 如果所有方向都不可用，继续当前方向（可能会撞到自己，但这是最后的选择）
        return self.direction

    def render(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], GRID_SIZE - 2, GRID_SIZE - 2))

    def handle_keys(self):
        # 处理所有事件，返回是否继续游戏
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True


class Food:
    def __init__(self, color):
        self.position = (0, 0)
        self.color = color
        self.randomize_position()

    def randomize_position(self):
        # 确保食物在网格内对齐
        grid_x = random.randint(0, GRID_WIDTH - 1)
        grid_y = random.randint(0, GRID_HEIGHT - 1)
        self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def render(self, surface):
        x, y = self.position
        # 绘制食物，稍微小一点以便看到网格
        pygame.draw.rect(surface, self.color, (x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2))


class Game:
    def __init__(self, config):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('贪吃蛇游戏 - 方向键控制 (ESC返回配置)')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(32)
        self.font_small = get_chinese_font(28)
        self.speed = config['speed']
        self.auto_mode = config['auto_mode']
        self.snake = Snake(config['snake_color'])
        self.food = Food(config['food_color'])
        # 确保食物初始位置不在蛇身上
        while self.food.position == self.snake.get_head_position():
            self.food.randomize_position()

    def run(self):
        while True:
            # 处理所有事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # 返回配置菜单
                    # 手动控制方向
                    elif event.key == pygame.K_UP and self.snake.direction != DOWN:
                        self.snake.direction = UP
                    elif event.key == pygame.K_DOWN and self.snake.direction != UP:
                        self.snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.snake.direction != LEFT:
                        self.snake.direction = RIGHT

            # 自动模式：计算最佳方向
            if self.auto_mode:
                self.snake.direction = self.snake.get_next_direction(self.food.position)

            # 更新蛇的位置
            self.snake.update()

            # 检查是否吃到食物
            if self.snake.get_head_position() == self.food.position:
                self.snake.length += 1
                self.snake.score += 10

                # 先随机生成新位置
                new_pos = self.food.position
                while new_pos in self.snake.positions:
                    self.food.randomize_position()
                    new_pos = self.food.position

            # 绘制背景
            self.screen.fill(BLACK)

            # 先绘制蛇（在下面）
            self.snake.render(self.screen)

            # 后绘制食物（在上面）
            self.food.render(self.screen)

            # 显示分数
            score_text = self.font.render(f'得分: {self.snake.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))

            # 显示速度
            speed_text = self.font.render(f'速度: {self.speed} FPS', True, LIGHT_GRAY)
            self.screen.blit(speed_text, (SCREEN_WIDTH - 150, 10))

            # 显示模式
            mode_text = self.font_small.render('自动模式' if self.auto_mode else '手动模式', True,
                                            CYAN if self.auto_mode else WHITE)
            self.screen.blit(mode_text, (SCREEN_WIDTH - 150, 50))

            pygame.display.update()
            self.clock.tick(self.speed)


def main():
    """启动配置菜单"""
    config_menu = ConfigMenu()
    config_menu.run()


if __name__ == '__main__':
    main()
