import pgzrun
import random
from ctypes import windll
from pgzhelper import *

WIDTH=800
HEIGHT=600

hwnd = pygame.display.get_wm_info()['window']
windll.user32.MoveWindow(hwnd, 0, 0, WIDTH, HEIGHT, False)

tank = Actor('tank_blue')
tank.y = 575
tank.x = 475
tank.original_x, tank.original_y = tank.x, tank.y
tank.angle = 90
tank.move_count = 0
enemies = []
explosions = []

for i in range(5):
    enemy = Actor('tank_red')
    enemy.y = 25
    enemy.x = i * 100 + 75
    enemy.angle = 270
    enemy.move_count = 0
    enemy.original_x, enemy.original_y = enemy.x, enemy.y
    enemies.append(enemy)

# create different types of walls. Some walls could be passed through, Some
# walls could block the bullets, and some walls could be broken.
walls = []
for x in range(16):
    for y in range(10):
        if random.randint(0, 100) < 50:
            rand = random.randint(0,9)
            if rand < 6:
                obs = Actor('wall')
            elif rand == 6:
                obs = Actor("cratemetal")
                obs.scale = 1.5
            elif rand == 7:
                obs = Actor("cratewood")
                obs.scale = 1.5
            elif rand == 8:
                obs = Actor("fencered")
            elif rand == 9:
                obs = Actor("treegreen_small")

            obs.x = x * 50 + 25
            obs.y = y * 50 + 25 + 50
            walls.append(obs)

bullets = []
bullet_holdoff = 0
enemy_bullets = []

game_over = False
win = False

bird = Actor("bird")
bird.x, bird.y = 400, 585
bird.scale = 0.5

# create birds wall, they are also of the wall type.
for i in range(4):
    bird_wall = Actor("wall")
    bird_wall.x, bird_wall.y = 380, 560 + i*12
    bird_wall.scale = 0.25
    walls.append(bird_wall)

for i in range(4):
    bird_wall = Actor("wall")
    bird_wall.x, bird_wall.y = 420, 560 + i*12
    bird_wall.scale = 0.25
    walls.append(bird_wall)

for i in range(1, 4):
    bird_wall = Actor("wall")
    bird_wall.x, bird_wall.y = 380 + i*12, 560
    bird_wall.scale = 0.25
    walls.append(bird_wall)

sounds.level1.play(-1)

def create_explosion(x_pos, y_pos):
    explosion = Actor("explosion3")
    explosion.x, explosion.y = x_pos, y_pos
    explosion.frame = 6
    explosions.append(explosion)

def tank_moving():
    # this part is about tank moving
    if tank.move_count > 0:
        if tank.angle == 180:
            tank.x = tank.x - 5
        elif tank.angle == 0:
            tank.x = tank.x + 5
        elif tank.angle == 90:
            tank.y = tank.y - 5
        elif tank.angle == 270:
            tank.y = tank.y + 5

        tank.move_count -= 1
        wall_index = tank.collidelist(walls)
        if wall_index != -1:
            if walls[wall_index].image != "treegreen_small":
                tank.x = tank.original_x
                tank.y = tank.original_y
                tank.move_count = 0

        if tank.x < 25 or tank.x > 775 or tank.y < 25 or tank.y > 575:
            tank.x = tank.original_x
            tank.y = tank.original_y
            tank.move_count = 0
    else:
        tank.original_x, tank.original_y = tank.x, tank.y
        if keyboard.left or keyboard.right or keyboard.up or keyboard.down:
            tank.move_count = 10

        if keyboard.left:
            if tank.angle != 180:
                tank.angle = 180
        elif keyboard.right:
            if tank.angle != 0:
                tank.angle = 0

        elif keyboard.up:
            if tank.angle != 90:
                tank.angle = 90
        elif keyboard.down:
            if tank.angle != 270:
                tank.angle = 270

def update():
    global bullet_holdoff
    global game_over, win

    if game_over != True and win != True:
        tank_moving()

        # This part is for the bullet, when hitting wall or the enemy tanks, have
        # explosion effect.
        if bullet_holdoff == 0:
            if keyboard.space:
                bullet = Actor('bulletblue2')
                bullet.angle = tank.angle
                bullet.x = tank.x
                bullet.y = tank.y
                bullets.append(bullet)
                bullet_holdoff = 25
        else:
            bullet_holdoff = bullet_holdoff - 1

        for bullet in bullets:
            if bullet.angle == 0:
                bullet.x = bullet.x + 15
            elif bullet.angle == 90:
                bullet.y = bullet.y - 15
            elif bullet.angle == 180:
                bullet.x = bullet.x - 15
            elif bullet.angle == 270:
                bullet.y = bullet.y + 15

        for bullet in bullets:
            # if bullet hits wall, remove the wall.
            wall_index = bullet.collidelist(walls)
            if wall_index != -1:
                if walls[wall_index].image == "wall" or walls[wall_index].image == "cratewood":
                    create_explosion(walls[wall_index].x, walls[wall_index].y)
                    sounds.sfx_damage_hit10.play()
                    del walls[wall_index]
                    bullets.remove(bullet)
                elif walls[wall_index].image == "fencered":
                    sounds.sfx_damage_hit10.play()
                    bullets.remove(bullet)

            if bullet.x < 0 or bullet.x > 800 or bullet.y < 0 or bullet.y > 600:
                bullets.remove(bullet)

            # if bullet hits enemy, remove the enemy
            enemy_index = bullet.collidelist(enemies)
            if enemy_index != -1:
                create_explosion(enemies[enemy_index].x, enemies[enemy_index].y)
                sounds.sfx_damage_hit10.play()
                del enemies[enemy_index]
                bullets.remove(bullet)
            else:
                # if bullets hit in the air, remove both bullets.
                enemy_index = bullet.collidelist(enemy_bullets)
                if enemy_index != -1:
                    del enemy_bullets[enemy_index]
                    bullets.remove(bullet)


        # This part is for the enemy
        for enemy in enemies:
            choice = random.randint(0, 1)
            if enemy.move_count > 0:
                if enemy.angle == 0:
                    enemy.x = enemy.x + 2
                elif enemy.angle == 90:
                    enemy.y = enemy.y - 2
                elif enemy.angle == 180:
                    enemy.x = enemy.x - 2
                elif enemy.angle == 270:
                    enemy.y = enemy.y + 2
                enemy.move_count -= 1

                if enemy.collidelist(walls) != -1:
                    enemy.x = enemy.original_x
                    enemy.y = enemy.original_y
                    enemy.move_timer = 0

                if enemy.x < -25 or enemy.x > 825 or enemy.y < -25 or enemy.y > 625:
                    enemy.x = enemy.original_x
                    enemy.y = enemy.original_y
                    enemy.move_count = 0

            else:
                enemy.move_count = 25
                enemy.original_x = enemy.x
                enemy.original_y = enemy.y

                # depending on the random value, check if the enemy tank should turn.
                if random.randint(0,4) < 3:

                    if enemy.x < 0:
                        enemy.angle = 0
                    elif enemy.x > 800:
                        enemy.angle = 180
                    elif enemy.y < 0:
                        enemy.angle = 270
                    elif enemy.y > 600:
                        enemy.angle = 90
                    else:
                        if random.randint(0, 2) < 2:
                            enemy.angle = 270
                        else:
                            enemy.angle = random.randint(0, 3) * 90
                else:
                    bullet = Actor('bulletred2')
                    bullet.angle = enemy.angle
                    bullet.x = enemy.x
                    bullet.y = enemy.y
                    enemy_bullets.append(bullet)

            if enemy.colliderect(bird):
                game_over = True
                sounds.sfx_damage_hit10.play()

        # This part is for the enemy bullets
        for bullet in enemy_bullets:
            if bullet.angle == 0:
                bullet.x = bullet.x + 5
            elif bullet.angle == 90:
                bullet.y = bullet.y - 5
            elif bullet.angle == 180:
                bullet.x = bullet.x - 5
            elif bullet.angle == 270:
                bullet.y = bullet.y + 5

        for bullet in enemy_bullets:
            # enemy bullets hit the wall. depending on the wall type, has
            # different effect.
            wall_index = bullet.collidelist(walls)
            if wall_index != -1:
                if walls[wall_index].image == "wall" or walls[wall_index].image == "cratewood":
                    create_explosion(walls[wall_index].x, walls[wall_index].y)
                    sounds.sfx_damage_hit10.play()
                    del walls[wall_index]
                    enemy_bullets.remove(bullet)
                elif walls[wall_index].image == "fencered":
                    sounds.sfx_damage_hit10.play()
                    enemy_bullets.remove(bullet)

            # enemy bullets hits the edge.
            if bullet.x < 0 or bullet.x > 800 or bullet.y < 0 or bullet.y > 600:
                enemy_bullets.remove(bullet)

            # enemy bullets hit the tank.
            if bullet.colliderect(tank) or bullet.colliderect(bird):
                game_over = True
                sounds.sfx_damage_hit10.play()

        # this part is about the collision between tank and enemy.
        enemy_index = tank.collidelist(enemies)
        if enemy_index != -1:
            create_explosion(tank.x, tank.y)
            create_explosion(enemies[enemy_index].x, enemies[enemy_index].y)
            game_over = True
            sounds.sfx_damage_hit10.play()

        for explosion in explosions:
            explosion.frame -= 1
            if explosion.frame == 3:
                explosion.image = "explosion4"
            elif explosion.frame == 0:
                explosions.remove(explosion)

        # if all the enemy tanks are destroyed, declare win to True.
        if len(enemies) == 0:
            win = True
            sounds.sfx_sounds_powerup3.play()

def draw():
    if win:
        sounds.level1.stop()
        screen.fill((0,0,0))
        screen.draw.text('You Win!', (260,250), color=(255,255,255), fontsize=100)
    elif game_over:
        screen.fill((0,0,0))
        screen.draw.text('You Lose!', (260,250), color=(255,255,255), fontsize=100)
        sounds.level1.stop()
    else:
        screen.fill((0,0,0))
        tank.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for bullet in enemy_bullets:
            bullet.draw()
        for wall in walls:
            wall.draw()

        bird.draw()

        for explosion in explosions:
            explosion.draw()

pgzrun.go() # Must be last line
