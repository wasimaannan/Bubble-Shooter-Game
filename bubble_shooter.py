import sys
import random
import time
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

W_Width = 600
W_Height = 800


def MidpointLine(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    zone = findZone(dx, dy)
    a0, b0 = convertToZone0(x0, y0, zone)
    a1, b1 = convertToZone0(x1, y1, zone)
    dx = a1 - a0
    dy = b1 - b0
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)
    x, y = convertBackToZone(a0, b0, zone)
    draw_pixel(x, y)
    while a0 < a1:
        if d <= 0:
            d += dE
            a0 += 1
        else:
            d += dNE
            a0 += 1
            b0 += 1

        x, y = convertBackToZone(a0, b0, zone)
        draw_pixel(x, y)


def findZone(dx, dy):
    if abs(dx) >= abs(dy) and dx >= 0 and dy >= 0:
        return 0
    elif abs(dx) < abs(dy) and dx >= 0 and dy >= 0:
        return 1
    elif abs(dx) < abs(dy) and dx < 0 and dy >= 0:
        return 2
    elif abs(dx) >= abs(dy) and dx < 0 and dy >= 0:
        return 3
    elif abs(dx) >= abs(dy) and dx < 0 and dy < 0:
        return 4
    elif abs(dx) < abs(dy) and dx < 0 and dy < 0:
        return 5
    elif abs(dx) < abs(dy) and dx >= 0 and dy < 0:
        return 6
    elif abs(dx) >= abs(dy) and dx >= 0 and dy < 0:
        return 7


def convertToZone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y


def convertBackToZone(a, b, zone):
    if zone == 0:
        return a, b
    elif zone == 1:
        return b, a
    elif zone == 2:
        return -b, a
    elif zone == 3:
        return -a, b
    elif zone == 4:
        return -a, -b
    elif zone == 5:
        return -b, -a
    elif zone == 6:
        return b, -a
    elif zone == 7:
        return a, -b


def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_left_arrow():
    glColor3f(0.0, 1.0, 1.0)
    MidpointLine(15, 765, 60, 765)
    MidpointLine(15, 765, 35, 745)
    MidpointLine(15, 765, 35, 785)


def draw_pause():
    glColor3f(1.0, 1.0, 0.0)  # Yellow

    if pause:
        # play
        MidpointLine(287, 750, 320, 770)
        MidpointLine(320, 770, 287, 790)
        MidpointLine(287, 750, 287, 790)
    else:
        # pause
        MidpointLine(290, 745, 290, 790)
        MidpointLine(310, 745, 310, 790)


def draw_cross():
    glColor3f(1.0, 0.0, 0.0)
    MidpointLine(540, 750, 580, 790)
    MidpointLine(540, 790, 580, 750)


def MidpointCircle(xc, yc, r):
    d = 1 - r
    x = 0
    y = r
    CirclePoints(xc, yc, x, y)
    while x < y:
        if d < 0:
            d = d + 2 * x + 3
            x += 1
        else:
            d = d + 2 * x - 2 * y + 5
            x += 1
            y -= 1
        CirclePoints(xc, yc, x, y)


def CirclePoints(xc, yc, x, y):
    draw_pixel(xc + x, yc + y)
    draw_pixel(xc + y, yc + x)
    draw_pixel(xc + y, yc - x)
    draw_pixel(xc + x, yc - y)
    draw_pixel(xc - x, yc - y)
    draw_pixel(xc - y, yc - x)
    draw_pixel(xc - y, yc + x)
    draw_pixel(xc - x, yc + y)


shooter_x = W_Width // 2
shooter_radius = 20


def draw_shooter_bubble():
    global shooter_x
    shooter_y = 50
    glColor3f(1.0, 0.65, 0.40)
    MidpointCircle(shooter_x, shooter_y, shooter_radius)


class Bubble:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed

    def update(self):
        self.y -= self.speed

    def draw(self):
        glColor3f(1.0, 0.20, 0.50)
        MidpointCircle(self.x, self.y, self.radius)

    def is_off_screen(self):
        return self.y + self.radius < 0


bubbles = []
max_bubbles = 5


def bubbles_collide(bubble1, bubble2):
    dist = math.sqrt((bubble1.x - bubble2.x) ** 2 + (bubble1.y - bubble2.y) ** 2)
    return dist <= (bubble1.radius + bubble2.radius)


def draw_bubbles():
    for bubble in bubbles:
        bubble.draw()


def pause_game():
    global pause
    pause = True


class Bullet:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.color = (random.random(), random.random(), random.random())

    def update(self):
        self.y += self.speed

    def draw(self):
        glColor3f(*self.color)
        MidpointCircle(self.x, self.y, self.radius)

    def is_off_screen(self):
        return self.y - self.radius > W_Height


bullets = []


def draw_bullets():
    for bullet in bullets:
        bullet.draw()


def detect_collision(bullet, bubble):
    dist = math.sqrt((bullet.x - bubble.x) ** 2 + (bullet.y - bubble.y) ** 2)
    return dist <= (bullet.radius + bubble.radius)


def check_collisions():
    global score, lives
    for bullet in bullets:
        for bubble in bubbles:
            if detect_collision(bullet, bubble):
                bubbles.remove(bubble)
                bullets.remove(bullet)
                score += 1
                print(f"Hit! Score: {score}")
                break


def check_game_over():
    global game_over
    if lives <= 0 or missed_bullets >= 3:
        game_over = True
        print(f"Game Over! Final Score: {score}")
        bubbles.clear()
        bullets.clear()


def reset_game():
    global score, lives, game_over, bullets, bubbles, missed_bullets
    score = 0
    lives = 3
    missed_bullets = 0
    game_over = False
    bullets.clear()
    bubbles.clear()
    print(f"Game reset. Lives: {lives}, Score: {score}")


score = 0
lives = 3
game_over = False
pause = False
missed_bullets = 0


def animate():
    global lives, missed_bullets
    if not pause and not game_over:
        for bubble in bubbles:
            bubble.update()
            if bubble.is_off_screen():
                bubbles.remove(bubble)
                lives -= 1
                print(f"Missed! Lives remaining: {lives}")

        for bullet in bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullets.remove(bullet)
                missed_bullets += 1
        check_collisions()
        check_game_over()

    if not game_over:
        if len(bubbles) < max_bubbles:
            max_attempts = 100
            for _ in range(max_attempts):
                radius = random.randint(10, 30)
                x = random.randint(radius, W_Width - radius)
                y = W_Height
                speed = random.uniform(0.2, 0.5)

                new_bubble = Bubble(x, y, radius, speed)

                if all(not bubbles_collide(new_bubble, bubble) for bubble in bubbles):
                    bubbles.append(new_bubble)
                    return


def keyboardListener(key, x, y):
    global shooter_x, shooter_radius, game_over
    step = 10
    if not game_over:
        if key == b'a':
            shooter_x -= step
            if shooter_x - shooter_radius < 0:
                shooter_x = shooter_radius + 5
        elif key == b'd':
            shooter_x += step
            if shooter_x + shooter_radius > W_Width:
                shooter_x = W_Width - shooter_radius - 5
        elif key == b' ':
            bullets.append(Bullet(shooter_x, 50 + shooter_radius, 4, 15))

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global pause, game_over
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = W_Height - y
        # pause button
        if 290 <= x <= 310 and 745 <= y <= 790:
            pause = not pause
        # left arrow (restart)
        elif 15 <= x <= 35 and 745 <= y <= 785:
            reset_game()
        # cross (exit)
        elif 540 <= x <= 580 and 750 <= y <= 790:
            print(f"Your final score is {score}. Goodbye!")
            glutLeaveMainLoop()

    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_left_arrow()
    draw_pause()
    draw_cross()
    draw_shooter_bubble()
    if not game_over:
        animate()
        draw_bubbles()
        draw_bullets()

    glutSwapBuffers()


def timer(value):
    animate()
    glutPostRedisplay()
    glutTimerFunc(30, timer, 30)


def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, W_Width, 0, W_Height)


# OpenGL setup
glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)  # Depth, Double buffer, RGB color

wind = glutCreateWindow(b"Bubble Shooter")
init()
glutTimerFunc(0, timer, 0)
glutDisplayFunc(display)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseListener)
glutMainLoop()
