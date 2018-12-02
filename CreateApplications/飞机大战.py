# -*- coding:utf-8 -*-

import pygame
from pygame.locals import *
import time
import random
import sys

'''
游戏帮助：
1. w,a,s,d和上下左右键---控制战机移动
2. 空格键---开火
3. f键---进入全屏
4. Esc键---退出全屏

'''
# 字体
gameover_font = u"./feiji/font/15.ttf"
mainfrm_font = u"./feiji/font/20.ttf"

# 背景图
# background_Image = "./feiji/background/background.png"
background_Image = "./feiji/background/灌木丛.jpg"
SCREEN_SIZE = [500, 750]  # 背景图大小
gameover_image = "./feiji/background/gameover.png"

# 挂件图
cloud_image = "./feiji/云.png"
birds_image = "./feiji/飞鸟2.png"
flower_image = "./feiji/落花.png"

# 获取玩家战机模型图和尺寸和战机爆炸视图列表
heroplane_Image = "./feiji/hero1.png"
heroplane_bombImagelist = ["./feiji/hero_blowup_n" + str(i) + ".png" for i in range(4)]
herobullet_image = "./feiji/bullet/bullet10.png"

# 获取玩家战机模型图和敌机爆炸视图列表
# 敌机1
enemyplane_Image = "./feiji/enemy0.png"
enemyplane_bombImagelist = ["./feiji/enemy0_down" + str(i) + ".png" for i in range(4)]
enemybullet_image = "./feiji/bullet/bullet7.png"
# 敌机2
enemyplane_Image2 = "./feiji/enemy1.png"
enemyplane_bombImagelist2 = ["./feiji/enemy1_down" + str(i) + ".png" for i in range(4)]
enemybullet_image2 = "./feiji/bullet/bullet0.png"

###########################################功能类#######################################################


class Game(object):
    """
    游戏类：用于游戏界面布局和渲染，以及一些辅助性功能
    """

###########################################静态方法#######################################################
    # 打印游戏退出信息
    @staticmethod
    def print_info():
        print "玩家生命已耗尽！！！"
        print "游戏退出！"

###########################################类属性#######################################################
    # 定义游戏数据变量
    ka = kd = kw = ks = fr = fu = False  # 按键状态标识类属性
    hero_death_num = 0  # 玩家死亡次数
    hero_life_total_num = 10  # 玩家生命总数
    enemy_death_num = 0  # 击毁敌机数量
    sounds = []  # 声音文件列表
    bk_position = ()  # 两背景图位置元组
    backgrounds = []  # 背景图片列表

###########################################类方法#######################################################

    #  加载音乐
    @classmethod
    def load_bomb_music(cls):
        cls.sounds.append(pygame.mixer.Sound("./feiji/bomb1.ogg"))
        cls.sounds.append(pygame.mixer.Sound("./feiji/bomb2.ogg"))

    # 创建小挂件
    @classmethod
    def create_widgets(cls):
        screen = cls.screen
        # 创建云朵，飞鸟，落花
        cls.cloud = MySpriter(screen, cls.backgrounds[0], cloud_image, speed=1.5, direction='left', original_position=(0, 0))
        cls.birds = MySpriter(screen, cls.backgrounds[0], birds_image, speed=2, direction='right', original_position=(screen.get_width(), 0))
        cls.flowers = MySpriter(screen, cls.backgrounds[0], flower_image, speed=1.6, direction='top',
                            original_position=(screen.get_width() / 2, 0), scale=1/3.0)

    @classmethod
    def show_widgets(cls):
        # 贴上云朵，飞鸟，落花
        cls.cloud.show()
        cls.birds.show()
        cls.flowers.show()

    # 初始化游戏背景
    @classmethod
    def initBackgound(cls, screen_temp):
        cls.screen = screen_temp

        # 1. 创建三个背景图片（2个游戏界面和1个游戏结束界面）
        gameover_temp = pygame.image.load(gameover_image)
        gameover_temp = pygame.transform.scale(gameover_temp, SCREEN_SIZE)  # 重置尺寸

        background1 = pygame.image.load(background_Image)
        background1 = pygame.transform.scale(background1, SCREEN_SIZE)  # 重置尺寸
        back1_left = 0
        back1_top = 0

        background2 = pygame.image.load(background_Image)
        background2 = pygame.transform.scale(background2, SCREEN_SIZE)  # 重置尺寸
        back2_left = 0
        back2_top = -background2.get_height()

        cls.bk_position = [back1_left, back1_top, back2_left, back2_top]
        cls.backgrounds = [background1, background2, gameover_temp]

    # 更新游戏背景
    @classmethod
    def updateBackgound(cls):
        screen = cls.screen
        margin_height = screen.get_height()
        background1, background2 = cls.backgrounds[:-1]
        back1_left, back1_top, back2_left, back2_top = cls.bk_position
        # 同时贴上两张相同背景图片,实现背景循环滑动
        background_speed = 1  # 背景图移动速度
        screen.blit(background1, [back1_left, back1_top])
        screen.blit(background2, [back2_left, back2_top])
        back1_top += background_speed
        back2_top += background_speed
        if back1_top >= margin_height:
            back1_top = -margin_height
        if back2_top >= margin_height:
            back2_top = -margin_height

        cls.bk_position = [back1_left, back1_top, back2_left, back2_top]

    # 显示游戏数据
    @classmethod
    def summary_data(cls, font, fontsize, position):
        """
        # 游戏数据汇总并显示函数
        :param screen_temp:             # 主窗体
        :param hero_life_total_num:     # 英雄生命总数
        :param hero_death_num:          # 英雄死亡次数
        :param enemy_death_num:         # 击毁敌机架数
        :param font:                    # 字体
        :param fontsize:                # 字体大小
        :param position:                # 绘制位置
        :return:
        """
        # 获取窗体尺寸
        screen_temp = cls.screen
        screen_width = screen_temp.get_width()
        screen_height = screen_temp.get_height()

        # 加载以及渲染字体
        my_font = pygame.font.Font(font, fontsize)
        text_surface1 = my_font.render((u"玩家战机生命总条数：%d" % cls.hero_life_total_num), True, (0, 0, 255))
        text_surface2 = my_font.render((u"玩家战机剩余生命条数：%d" % (cls.hero_life_total_num - cls.hero_death_num)), True, (0, 255, 0))
        text_surface3 = my_font.render((u"击毁敌机数量：%d" % cls.enemy_death_num), True, (255, 0, 0))

        if position == 'center':
            screen_temp.blit(text_surface1, ((screen_width - text_surface1.get_width()) / 2, (
                    screen_height - text_surface1.get_height()) / 2.0 - 3 * text_surface1.get_height()))
            screen_temp.blit(text_surface2, ((screen_width - text_surface2.get_width()) / 2, (
                    screen_height - text_surface2.get_height()) / 2.0 - text_surface2.get_height()))
            screen_temp.blit(text_surface3, ((screen_width - text_surface3.get_width()) / 2, (
                    screen_height - text_surface3.get_height()) / 2.0 + text_surface3.get_height()))
        elif position == 'top_right_corner':
            screen_temp.blit(text_surface1,
                             (screen_temp.get_width() - text_surface1.get_width(), text_surface1.get_height()))
            screen_temp.blit(text_surface2, (screen_temp.get_width() - text_surface2.get_width(),
                                             text_surface1.get_height() + 1.5 * text_surface2.get_height()))
            screen_temp.blit(text_surface3, (screen_temp.get_width() - text_surface3.get_width(),
                                             text_surface1.get_height() + 3 * text_surface3.get_height()))

    # 碰撞检测（击中检测）
    @classmethod
    def detect_collision(cls, heroPlane_temp, enemyPlane_temp):
        # 获取gameover背景图
        gameover_temp = cls.backgrounds[-1]
        # 获取音效
        sound1 = cls.sounds[0]
        sound2 = cls.sounds[1]
        # 检测碰撞
        isHeroPlaneAttacked = False
        isEnemyPlaneAttacked = False
        heroPlane_centerx = heroPlane_temp.rect.centerx
        heroPlane_centery = heroPlane_temp.rect.centery
        enemyPlane_centerx = enemyPlane_temp.rect.centerx
        enemyPlane_centery = enemyPlane_temp.rect.centery

        # 检测玩家战机是否被击中
        for bullet in enemyPlane_temp.bullet_list:
            bullet_centerx = bullet.rect.centerx
            bullet_centery = bullet.rect.centery

            distance_x = abs(heroPlane_temp.x + heroPlane_centerx - (bullet.x + bullet_centerx))
            distance_y = abs(heroPlane_temp.y + heroPlane_centery - (bullet.y + bullet_centery))
            if distance_x < (heroPlane_centerx + bullet_centerx - 10) and distance_y < (
                    heroPlane_centery + bullet_centery - 20):
                enemyPlane_temp.bullet_list.remove(bullet)
                heroPlane_temp.bomb()
                isHeroPlaneAttacked = True

        # 检测敌机是否被击中
        for bullet in heroPlane_temp.bullet_list:
            bullet_centerx = bullet.rect.centerx
            bullet_centery = bullet.rect.centery

            distance_x = abs(enemyPlane_temp.x + enemyPlane_centerx - (bullet.x + bullet_centerx))
            distance_y = abs(enemyPlane_temp.y + enemyPlane_centery - (bullet.y + bullet_centery))
            if distance_x < (enemyPlane_centerx + bullet_centerx - 10) and distance_y < (
                    enemyPlane_centery + bullet_centery - 20):
                heroPlane_temp.bullet_list.remove(bullet)
                enemyPlane_temp.bomb()
                isEnemyPlaneAttacked = True

        # 判断碰撞情况
        if isHeroPlaneAttacked:  # 玩家战机被击中
            sound1.play()  # 播放爆炸声
            for i in range(560):
                heroPlane_temp.display()
                pygame.display.update()

            cls.reset(heroPlane_temp)  # 重置敌机
            isHeroPlaneAttacked = False
            cls.hero_death_num += 1
            if cls.hero_death_num == cls.hero_life_total_num:
                # 游戏数据汇总：设置退出
                cls.screen.blit(gameover_temp, (0, 0))
                cls.summary_data(font=gameover_font, fontsize=32, position='center')
                pygame.display.update()
                time.sleep(3)
                cls.print_info()
                sys.exit()  # 退出游戏

        elif isEnemyPlaneAttacked:  # 敌机被击中
            sound2.play()  # 播放爆炸声
            for i in range(560):
                enemyPlane_temp.display()
                pygame.display.update()

            cls.reset(enemyPlane_temp)  # 重置玩家战机
            isEnemyPlaneAttacked = False
            cls.enemy_death_num += 1

    # 战机重置
    @classmethod
    def reset(cls, plane):
        plane.image_index = 0
        plane.image_num = 0
        plane.hit = False

    # 按键控制
    @classmethod
    def key_control(cls, hero_temp):
        # 获取事件，比如按键等
        for event in pygame.event.get():

            # 判断是否是点击了退出按钮
            if event.type == QUIT:
                print("exit")
                sys.exit()

            # 判断是否改变窗口大小
            # if event.type == VIDEORESIZE:
            #     sc_size = event.size
            #     cls.screen = pygame.display.set_mode(sc_size, RESIZABLE, 32)
            #     pygame.display.set_caption("Window resized to " + str(event.size))
            #
            #     # 更新背景
            #     bk1 = cls.backgrounds[0]
            #     bk2 = cls.backgrounds[1]
            #     screen_width, screen_height = sc_size
            #     m_back1_left = (screen_width-bk1.get_width())/2.0
            #     m_back1_top = 0
            #     m_back2_left = (screen_width - bk2.get_width()) / 2.0
            #     m_back2_top = -bk1.get_height()
            #     cls.screen.blit(bk1, (m_back1_left, m_back1_top))
            #     cls.screen.blit(bk2,(m_back2_left, m_back2_top))
            #     cls.bk_position = [m_back1_left, m_back1_top, m_back2_left, m_back2_top]
            #
            #     # 更新挂件精灵
            #     cls.cloud.set_margin(bk1)
            #     cls.birds.set_margin(bk1)
            #     cls.flowers.set_margin(bk1)
            #
            #     # 更新窗口
            #     pygame.display.update()
            #     # 这里需要重新填满窗口
            #     # for y in range(0, screen_height, cls.backgrounds[0].get_height()):
            #     #     for x in range(0, screen_width, cls.backgrounds[0].get_width()):
            #     #         cls.screen.blit(cls.backgrounds[0], (x, y))



            # 判断是否是松开了按键
            if event.type == KEYUP:
                # 检测按键是否是a或者left
                if event.key == K_a or event.key == K_LEFT:
                    cls.ka = False
                    cls.fr = True
                # 检测按键是否是d或者right
                elif event.key == K_d or event.key == K_RIGHT:
                    cls.kd = False
                    cls.fr = False
                # 检测按键是否是w或者up
                elif event.key == K_w or event.key == K_UP:
                    cls.kw = False
                    cls.fu = False
                # 检测按键是否是s或者right
                elif event.key == K_s or event.key == K_DOWN:
                    cls.ks = False
                    cls.fu = True

            # 判断是否是按下了按键
            if event.type == KEYDOWN:
                # 检测按键是否是a或者left
                if event.key == K_a or event.key == K_LEFT:
                    cls.ka = True
                    cls.fr = False
                # 检测按键是否是d或者right
                elif event.key == K_d or event.key == K_RIGHT:
                    cls.kd = True
                    cls.fr = True
                # 检测按键是否是w或者up
                elif event.key == K_w or event.key == K_UP:
                    cls.kw = True
                    cls.fu = True
                # 检测按键是否是s或者right
                elif event.key == K_s or event.key == K_DOWN:
                    cls.ks = True
                    cls.fu = False
                # 退出全屏检测
                elif event.key == K_ESCAPE:
                    cls.screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
                # 进入全屏控制
                elif event.key == K_f:
                    cls.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
                # 检测按键是否是空格键
                elif event.key == K_SPACE:
                    print('------玩家发射炮弹------')
                    hero_temp.fire()

        if cls.ka is True and cls.fr is False:
            hero_temp.move_left()
        elif cls.kd is True and cls.fr is True:
            hero_temp.move_right()
        elif cls.kw is True and cls.fu is True:
            hero_temp.move_up()
        elif cls.ks is True and cls.fu is False:
            hero_temp.move_down()


class Base(object):
    def __init__(self, screen_temp, x, y, image_name):
        self.x = x
        self.y = y
        self.screen = screen_temp
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()


class BasePlane(Base):
    def __init__(self, screen_temp, x, y, image_name, bombImage_name_temp):
        Base.__init__(self, screen_temp, x, y, image_name)
        self.bullet_list = []  # 存储发射出去的子弹对象引用

        # 爆炸效果用的如下属性
        self.hit = False  # 表示是否要爆炸
        self.bomb_list = []  # 用来存储爆炸时需要的图片
        self.__crate_images(bombImage_name_temp)  # 调用这个方法向bomb_list中添加图片
        self.image_num = 0  # 用来记录while True的次数,当次数达到一定值时才显示一张爆炸的图,然后清空,,当这个次数再次达到时,再显示下一个爆炸效果的图片
        self.image_index = 0  # 用来记录当前要显示的爆炸效果的图片的序号

    def __crate_images(self, bombImage_name_temp):
        self.bomb_list.append(pygame.image.load(bombImage_name_temp[0]))
        self.bomb_list.append(pygame.image.load(bombImage_name_temp[1]))
        self.bomb_list.append(pygame.image.load(bombImage_name_temp[2]))
        self.bomb_list.append(pygame.image.load(bombImage_name_temp[3]))

    def bomb(self):
        self.hit = True

    def display(self):
        # 如果被击中,就显示爆炸效果,否则显示普通的飞机效果
        if self.hit == True:
            if self.image_index > 3:
                # 等待死亡
                return

            self.screen.blit(self.bomb_list[self.image_index], (self.x, self.y))
            self.image_num += 1
            if self.image_num == 140:
                self.image_num = 0
                self.image_index += 1
        else:
            self.screen.blit(self.image, (self.x, self.y))
            # 不管战机是否被击中,都要显示发射出去的子弹
            mark = []
            for bullet in self.bullet_list:
                bullet.display()
                bullet.move()
                # 判断子弹是否越界,并标记越界子弹
                if bullet.judge():
                    mark.append(bullet)

            # 删除越界子弹
            for waste in mark:
                self.bullet_list.remove(waste)


class HeroPlane(BasePlane):
    def __init__(self, screen_temp, heroplane_Image_temp, heroplane_bombImagelist_temp, herobullet_image_temp):
        BasePlane.__init__(self, screen_temp, screen_temp.get_rect().centerx, screen_temp.get_rect().centery,
                           heroplane_Image_temp, heroplane_bombImagelist_temp)
        self.herobullet_image = herobullet_image_temp

    def move_left(self):
        if self.x < -self.width:
            self.x = self.screen.get_width()
        else:
            self.x -= 10

    def move_right(self):
        if self.x > self.screen.get_width():
            self.x = -self.width
        else:
            self.x += 10

    def move_up(self):
        if self.y < -self.height:
            self.y = self.screen.get_height()
        else:
            self.y -= 10

    def move_down(self):
        if self.y > self.screen.get_height():
            self.y = -self.height
        else:
            self.y += 10

    def fire(self):
        self.bullet_list.append(HeroBullet(self.screen, self.x, self.y, self.herobullet_image))


class EnemyPlane(BasePlane):
    """敌机的类"""

    def __init__(self, screen_temp, enemyplane_Image_temp, enemyplane_bombImagelist_temp, enemybullet_image_temp):
        # bombImage_name = ["./feiji/enemy0_down" + str(i) + ".png" for i in range(4)]
        BasePlane.__init__(self, screen_temp, 0, 0, enemyplane_Image_temp, enemyplane_bombImagelist_temp)
        self.direction = "right"  # 用来存储飞机默认的显示方向
        self.enemybullet_image = enemybullet_image_temp
    def move(self):

        if self.direction == "right":
            self.x += random.randint(2, 10)
        elif self.direction == "left":
            self.x -= random.randint(2, 10)

        if self.x > 480 - 50:
            self.direction = "left"
        elif self.x < 0:
            self.direction = "right"

    def fire(self):
        random_num = random.randint(1, 100)
        if random_num == 8 or random_num == 20:
            self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, self.enemybullet_image))


class BaseBullet(Base):
    def display(self):
        self.screen.blit(self.image, (self.x, self.y))


class HeroBullet(BaseBullet):
    def __init__(self, screen_temp, x, y, herobullet_image_temp):
        BaseBullet.__init__(self, screen_temp, x + 40, y - 20, herobullet_image_temp)

    def move(self):
        # 玩家子弹速度
        self.y -= 15

    def judge(self):
        if self.y < 0:
            return True
        else:
            return False


class EnemyBullet(BaseBullet):
    def __init__(self, screen_temp, x, y, enemybullet_image_temp):
        BaseBullet.__init__(self, screen_temp, x + 25, y + 40, enemybullet_image_temp)

    def move(self):
        # 敌机子弹速度
        self.y += 5

    def judge(self):
        if self.y > 852:
            return True
        else:
            return False


class MySpriter(object):
    def __init__(self, screen_temp, margin, image_name, speed, direction, original_position, scale=1.0):
        """
        MySpriter类初始化函数
        :param screen_temp:         主窗体
        :param image_name:          精灵图像
        :param speed:               精灵速度
        :param direction:           精灵出发方位
        :param original_position:   精灵的初始位置
        """
        self.x = original_position[0]
        self.y = original_position[1]
        self.screen = screen_temp
        self.margin = margin
        self.image = pygame.image.load(image_name)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.scale = scale
        self.__change_scale()
        self.speed = speed
        self.direction = direction
        self.screen_is_changed = False
        self.flag = True

    # 改变精灵比例
    def __change_scale(self):
        self.image = pygame.transform.scale(self.image,
                [int(self.width * self.scale), int(self.height * self.scale)])  # 重置尺寸

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    # 显示精灵
    def show(self):
        # 在主窗体贴上云朵，飞鸟，落花
        self.update_position()
        self.screen.blit(self.image, (self.x, self.y))

    # 随机生成精灵移动方向
    def random_direction(self):
        # 随机改变方向
        self.direction = random.choice(['left', 'right'])

    # 设置边缘
    def set_margin(self, margin):
        self.margin = margin
        self.screen_is_changed = True

    # 更新精灵位置
    def update_position(self):
        """
        更新挂件位置函数
        """
        margin_height = self.margin.get_height()
        margin_width = self.margin.get_width()
        screen_height = self.screen.get_height()
        screen_width = self.screen.get_width()

        if self.flag:
            if self.direction == 'left':
                self.x += self.speed
                if self.x > screen_width + self.width:
                    # 更新物体位置
                    self.y = random.randint(0, int(screen_height - self.height) + 1)
                    self.x = - self.width
                    self.random_direction()
            elif self.direction == 'right':
                self.x -= self.speed
                if self.x < - self.width:
                    # 更新物体位置
                    self.y = random.randint(0, int(screen_height - self.height) + 1)
                    self.x = screen_width + self.width
                    self.random_direction()
            elif self.direction == 'top':
                self.y += self.speed
                if self.y > screen_height + self.height:
                    # 更新物体位置
                    self.x = random.randint(0, int(screen_width - self.width) + 1)
                    self.y = - self.height
            elif self.direction == 'bottom':
                self.y -= self.speed
                if self.y < - self.height:
                    # 更新物体位置
                    self.x = random.randint(0, int(screen_width - self.width) + 1)
                    self.y = screen_height + self.height

            return


        if self.screen_is_changed is False:
            if self.direction == 'left':
                self.x += self.speed
                if self.x > (screen_width + margin_width)/2.0 + self.width:
                    # 更新物体位置
                    self.y = random.randint(0, int(margin_height - self.height) + 1)
                    self.x = (screen_width - margin_width)/2.0 - self.width
                    self.random_direction()
            elif self.direction == 'right':
                self.x -= self.speed
                if self.x < (screen_width - margin_width)/2.0 - self.width:
                    # 更新物体位置
                    self.y = random.randint(0, int(margin_height - self.height) + 1)
                    self.x = (screen_width + margin_width)/2.0 + self.width
                    self.random_direction()
            elif self.direction == 'top':
                self.y += self.speed
                if self.y > (screen_height + margin_height)/2.0 + self.height:
                    # 更新物体位置
                    self.x = random.randint(0, int(margin_width - self.width) + 1)
                    self.y = (screen_height - margin_height)/2.0 - self.height
            elif self.direction == 'bottom':
                self.y -= self.speed
                if self.y < (screen_height - margin_height)/2.0 - self.height:
                    # 更新物体位置
                    self.x = random.randint(0, int(margin_width - self.width) + 1)
                    self.y = (screen_height + margin_height)/2.0 + self.height
        else:
            if self.direction == 'left':
                self.x += self.speed
                if self.x > (screen_width + margin_width)/2.0:
                    # 更新物体位置
                    self.y = random.randint(0, int(margin_height - self.height) + 1)
                    self.x = (screen_width - margin_width)/2.0
                    self.random_direction()
            elif self.direction == 'right':
                self.x -= self.speed
                if self.x < (screen_width - margin_width)/2.0:
                    # 更新物体位置
                    self.y = random.randint(0, int(margin_height - self.height) + 1)
                    self.x = (screen_width + margin_width)/2.0
                    self.random_direction()
            elif self.direction == 'top':
                self.y += self.speed
                if self.y > (screen_height + margin_height)/2.0:
                    # 更新物体位置
                    self.x = random.randint(0, int(margin_width - self.width) + 1)
                    self.y = (screen_height - margin_height)/2.0
            elif self.direction == 'bottom':
                self.y -= self.speed
                if self.y < (screen_height - margin_height)/2.0:
                    # 更新物体位置
                    self.x = random.randint(0, int(margin_width - self.width) + 1)
                    self.y = (screen_height + margin_height)/2.0


###########################################主程序#######################################################


def main():
    # 0. 初始化
    pygame.init()

    # 1. 读取爆炸音乐
    Game.load_bomb_music()

    # 2. 创建窗口并设置标题
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("飞机大战！")

    # 初始化背景, 并返回初始化后的背景图和初始位置
    Game.initBackgound(screen)

    # 3. 创建一个飞机对象
    hero = HeroPlane(screen, heroplane_Image, heroplane_bombImagelist, herobullet_image)
    # 4. 创建两个敌机
    enemy = EnemyPlane(screen, enemyplane_Image, enemyplane_bombImagelist, enemybullet_image)
    enemy2 = EnemyPlane(screen, enemyplane_Image2, enemyplane_bombImagelist2, enemybullet_image2)

    # 5. 创建小挂机
    Game.create_widgets()

    # 设定时钟
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)  # 设定游戏帧数（60）

        # 更新背景图，同时贴上两张相同背景图片,实现背景循环滑动
        Game.updateBackgound()

        # 游戏角色开启
        hero.display()  # 显示玩家战机
        enemy.display()  # 显示敌机
        enemy.move()  # 调用敌机的移动方法
        enemy.fire()  # 敌机开火

        enemy2.display()  # 显示敌机
        enemy2.move()  # 调用敌机的移动方法
        enemy2.fire()  # 敌机开火

        # 显示小挂件
        Game.show_widgets()

        # 按键检测
        Game.key_control(hero)

        # 在主窗体右上角显示游戏数据
        Game.summary_data(font=mainfrm_font, fontsize=16, position='top_right_corner')

        # 检测子弹和战机有没有发生碰撞
        Game.detect_collision(hero, enemy)
        Game.detect_collision(hero, enemy2)

        # 更新画面
        pygame.display.update()


if __name__ == "__main__":
    main()
