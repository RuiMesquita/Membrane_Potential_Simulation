import pygame  # pip install pygame
import random
import math
import matplotlib.pyplot as plt
import datetime
import sys
import Gui
import os
print(os.getcwd())

# ===================================================== Interface Grafica ================================================================
gui_variables = Gui.gui()

# ====================================================== Algoritmo Pygame ====================================================================
pygame.init()
screen_dimension = width, height = 1200, 800
clock = pygame.time.Clock()
FPS = 60

# Definir algumas cores
RED = (255, 0, 0)
RED_capt = (240, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLUE_capt = (0, 0, 240)

YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)

BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)

# Variaveis fisicas para o movimento das particulas
elasticity = 1
drag = 1

# ============================================ converter RGB para o formato correto de cor ================================================
# try/except causa com que o programa nao crash em caso de se fechar a janela da GUI sem inserir valores
try:
    Na_ions, K_ions = int(gui_variables[2]), int(gui_variables[3])

    gui_variables[0] = gui_variables[0].split(" ")
    gui_variables[1] = gui_variables[1].split(" ")

    R_k, G_k, B_k = gui_variables[0][0], gui_variables[0][1], gui_variables[0][2]
    color_k = (int(float(R_k)), int(float(G_k)), int(float(B_k)))

    R_Na, G_Na, B_Na = gui_variables[1][0], gui_variables[1][1], gui_variables[1][2]
    color_Na = (int(float(R_Na)), int(float(G_Na)), int(float(B_Na)))

except Exception:
    sys.exit()

# Variaveis para a modelacao
num_particles = Na_ions + K_ions
num_membranes = 7
selected_particle = None
run = True
count = 0
ddp = 0
step = 0

# Vetores para o algoritmo
pumps = []
my_particles = []
membranes = []
ddp_array = []
Ec_array = []

# Constantes
eletronC = float(1.602 * math.pow(10, -19))
capacitance = float(math.pow(10, -9))

screen = pygame.display.set_mode(screen_dimension)
pygame.display.set_caption("Simulador de particulas")

# ==================================================== Funções do algoritmo =======================================================


# Calculo da diferenca de cargas entre MIC e MEC
def calculateDC(particle_array):
    n_intra = 0
    n_extra = 0
    for i, particle in enumerate(particle_array):
        if particle.y < height / 2 + 10:
            n_extra += 1
        elif particle.y > height / 2:
            n_intra += 1

    ddp = n_intra - n_extra
    return n_intra, n_extra, ddp


# Funcao que devolve a particula que foi selecionada pelo rato
def findParticle(particles, x, y):
    for p in particles:
        if math.hypot(p.x - x, p.y - y) <= p.radius:
            return p
    return None


# Funcao que soma vetores
def addVectors(angle1, length1, angle2, length2):
    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2

    angle = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)
    return angle, length


# Verifica se houve colisao com a membrana
def membraneColision(p, membranes, n):
    for i in range(n):
        if (p.x - p.radius > membranes[i].x + membranes[i].width - 1 and p.x - p.radius <= membranes[i].x + membranes[i].width) or (p.x + p.radius < membranes[i].x + 1 and p.x + p.radius >= membranes[i].x):
            if p.y + p.radius > membranes[i].y and p.y - p.radius < membranes[i].y + membranes[i].height:
                p.speed = -p.speed * elasticity
                p.angle = math.pi - p.angle

        elif p.y + p.radius > membranes[i].y and p.y - p.radius < membranes[i].y + membranes[i].height:
            if p.x - p.radius < membranes[i].x + membranes[i].width and p.x + p.radius > membranes[i].x:
                p.speed = -p.speed * elasticity
                p.angle = -p.angle


# Faz modelacao do choque das particulas com as bombas de sodio e potassio quando estas se encontram fechadas
def colision_pumps(dx, dy, particle):
    tangent = math.atan2(dy, dx)
    angle = 0.5 * math.pi + tangent
    angle1 = 2 * tangent - particle.angle
    speed1 = particle.speed * elasticity

    particle.angle, particle.speed = angle1, speed1

    particle.x = particle.x + math.sin(angle)
    particle.y = particle.y - math.cos(angle)


# Verificar se houve alguma colisao entre particulas
def colision(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    dist = math.hypot(dx, dy)
    if dist < p1.radius + p2.radius:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass
        p1.angle, p1.speed = addVectors(p1.angle, p1.speed * (p1.mass - p2.mass) / total_mass, angle, 2 * p2.speed * p2.mass / total_mass)
        p2.angle, p2.speed = addVectors(p2.angle, p2.speed * (p2.mass - p1.mass) / total_mass, angle + math.pi, 2 * p1.speed * p1.mass / total_mass)
        p1.speed *= 0.99
        p2.speed *= 0.99

        overlap = 0.5 * (p1.radius + p2.radius - dist + 1)
        p1.x += math.sin(angle) * overlap
        p1.y -= math.cos(angle) * overlap
        p2.x -= math.sin(angle) * overlap
        p2.y += math.cos(angle) * overlap


# Faz o calculo da energia cinetica media das particulas
def kineticEnergy(particle_array):
    kinetic_energy = []
    kinetic_energy_sum = 0
    for particle in particle_array:
        kinetic_energy = 0.5 * particle.mass * pow(particle.speed, 2)
        kinetic_energy_sum += kinetic_energy
    return kinetic_energy_sum / num_particles


# Permite adicionar novas particulas ao ecra em função do iao selecionado
def addParticles(particle_array, option):
    color = color_k
    radius = 10
    density = random.randint(30, 40)
    if option == "Na":
        color = color_Na
        radius = 8
    x = random.randint(radius, width - radius)
    y = random.randint(radius, height - radius)
    while y + radius > membranes[5].y - 25 and y - radius < membranes[5].y + membranes[5].height + 25:
        y = random.randint(radius, width - radius)
    ion = Particles(x, y, radius, color, density * radius**2)
    ion.angle = random.uniform(0, math.pi * 2)
    ion.speed = random.uniform(0.5, 0.7)
    particle_array.append(ion)


# Permite remover particulas do ecra em função do iao selecionado
def deleteParticles(particle_array, option):
    positions = []
    if option == "K":
        for i, particle in enumerate(particle_array):
            if particle.color == color_k:
                positions.append(i)
        particle_array.pop(random.choice(positions))
    if option == "Na":
        for i, particle in enumerate(particle_array):
            if particle.color == color_Na:
                positions.append(i)
        particle_array.pop(random.choice(positions))


# imprime texto para uma superficie
def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()


# Quando se prime o botao de pausa faz "STOP" do programa e fica a espera que o botao ESC seja premido
def paused(pause=True):
    largeText = pygame.font.SysFont("Arial", 20)
    menu_width, menu_height = 400, 200
    shape = (width / 2 - (menu_width / 2), height / 2 - (menu_height / 2), menu_width, menu_height)
    pygame.draw.rect(screen, WHITE, shape, 0)
    pygame.draw.rect(screen, BLACK, shape, 2)

    TextSurf, TextRect = text_objects("Em pausa, pressione ESC para retomar", largeText)
    TextRect.center = ((width / 2), (height / 2))
    screen.blit(TextSurf, TextRect)

    pygame.display.update()

    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = False


# ========================================================= Classes do algoritmo =================================================
# Classe para a modelacao de todos os ioes (sodio e potassio)
class Particles:
    # Construtor
    def __init__(self, x, y, radius, color, mass=1):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.mass = mass
        self.thickness = 0
        self.speed = 0
        self.angle = 0

    # Metodo para desenhar uma particula
    def display(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius, self.thickness)

    # Metodo para mover particulas
    def move(self):
        self.angle, self.speed = addVectors(self.angle, self.speed, 10, 0)
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.speed *= drag

    # Metodo que verifca se houve colisoes com as paredes
    def bounce(self):
        if self.x + self.radius > width:
            self.x = 2 * (width - self.radius) - self.x
            self.angle = -self.angle
            self.speed = self.speed * elasticity
        elif self.x < self.radius:
            self.x = 2 * self.radius - self.x
            self.angle = -self.angle
            self.speed = self.speed * elasticity
        elif self.y + self.radius > height:
            self.y = 2 * (height - self.radius) - self.y
            self.angle = math.pi - self.angle
            self.speed = self.speed * elasticity
        elif self.y < self.radius:
            self.y = 2 * self.radius - self.y
            self.angle = math.pi - self.angle
            self.speed = self.speed * elasticity


# Classe que trata de todas as particulas e as suas acoes
class Na_K_pumps:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.thickness = 1
        self.status = 0  # para poder verificar se algum iao se encontra nesta bomba
        self.ion = None

    def displayLimits(self):
        if self.status == 0:
            pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), self.radius, self.thickness)
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius, self.thickness)

    def Na_Capture(self, particle):
        dx = particle.x - self.x
        dy = particle.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.radius + particle.radius:
            if particle.color == color_Na and particle.y > membranes[0].y + membranes[0].height and self.status == 0:
                self.ion = particle
                particle.speed = 0
                particle.angle = 0
                particle.color = RED_capt
                particle.x = self.x
                particle.y = self.y
                self.status = 1
            else:
                colision_pumps(dx, dy, particle)

    def K_capture(self, particle):
        dx = particle.x - self.x
        dy = particle.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.radius + particle.radius:
            if particle.color == color_k and particle.y < membranes[0].y and self.status == 0:
                self.ion = particle
                particle.speed = 0
                particle.angle = 0
                particle.color = BLUE_capt
                particle.x = self.x
                particle.y = self.y
                self.status = 1
            else:
                colision_pumps(dx, dy, particle)

    def lockPump(self, particle):
        if self.status == 1:
            dx = particle.x - self.x
            dy = particle.y - self.y
            dx2 = dx + 3
            dy2 = dy + 3
            safeDist = math.hypot(dx2, dy2)
            dist = math.hypot(dx, dy)

            # Condicao de seguranca para dar tempo ao algoritmo de reagir
            if safeDist < self.radius + particle.radius and safeDist > self.radius + particle.radius - 1:
                pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), 28, 2)
                colision_pumps(dx, dy, particle)

            # Impede que mais particulas entrem dentro das bombas quando estas ja tem uma carga
            if dist < self.radius + particle.radius and dist > self.radius + particle.radius - 1:
                colision_pumps(dx, dy, particle)

    def ionPassage(self):
        if self.status == 1:
            if self.ion.color == RED_capt:
                self.ion.color = color_Na
                self.ion.speed = random.uniform(0.5, 0.7)
                self.ion.angle = 0
            if self.ion.color == BLUE_capt:
                self.ion.color = color_k
                self.ion.speed = random.uniform(0.5, 0.7)
                self.ion.angle = math.pi


# Classe para fazer as membranas
class Platforms:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def drawPlatform(self):
        shape = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, GREEN, shape, 0)
        pygame.draw.rect(screen, BLACK, shape, 2)


# =========================================== Definir as posicoes para as membranas ==============================================
spacing = 50
permeable_pore = 50
x_dim = (width - (5 * spacing + permeable_pore)) / num_membranes

for i in range(num_membranes):
    membrane = Platforms(x_dim * i + spacing * i, height / 2, x_dim, 10)
    if i == 6:
        membrane = Platforms(x_dim * i + 47 * i, height / 2, 200, 10)
    membranes.append(membrane)


# ========================================= Criar multiplas particulas para o array ===============================================
for i in range(num_particles):
    color = color_Na
    radius = 8
    density = random.randint(30, 40)
    if i >= Na_ions:
        color = color_k
        radius = 10
    x = random.randint(radius, width - radius)
    y = random.randint(radius, height - radius)
    # +25/-25 para nao deixar as particulas dar spawn diretamente nos canais
    while y + radius > membranes[5].y - 25 and y - radius < membranes[5].y + membranes[5].height + 25:
        y = random.randint(radius, width - radius)

    particle = Particles(x, y, radius, color, density * radius**2)
    particle.angle = random.uniform(0, math.pi * 2)
    particle.speed = random.uniform(0.5, 0.7)
    my_particles.append(particle)


# ========================================== criar as bombas de sodio e potassio ===================================================
for i in range(num_membranes):
    if membranes[i].x + membranes[i].width + (spacing / 2) and i <= 4:
        pump = Na_K_pumps(int(membranes[i].x + membranes[i].width + (spacing / 2)), int(height / 2 + 2), 25)
        pumps.append(pump)

# ================================================== Legendas no ecra ==============================================================
font = pygame.font.Font("freesansbold.ttf", 15)
label1 = font.render("Meio extracelular", True, WHITE, GRAY)
label2 = font.render("Meio intracelular", True, WHITE, GRAY)

label2Rect = label2.get_rect()
label2Rect.center = (100, 780)
label1Rect = label1.get_rect()
label1Rect.center = (100, 20)


# ===================================================== MAIN LOOP ==================================================================
# controla tudo o que acontece enquanto a simulacao estiver ativa
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = findParticle(my_particles, mouseX, mouseY)
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None
        # ======================================== Funcoes do teclado ============================================================
        # i - informação relativa a ddp
        # e - valor media de energia cinetica nesse instante
        # n - adiciona ioes de sodio
        # k - adiciona ioes de potassio
        # a - remove ioes de sodio
        # s - remove ioes de potassio
        # ESC - pausa a aplicacao
        # ESC - continua a aplicacao
        # seta esq/dir - muda a cor do fundo
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused()

            if event.key == pygame.K_i:
                hour = datetime.datetime.now().hour
                minute = datetime.datetime.now().minute
                second = datetime.datetime.now().second
                print("Diferenca de potencial as %s:%s.%s - %lg V" % (hour, minute, second, ddp))

            if event.key == pygame.K_n:
                addParticles(my_particles, "Na")
                num_particles += 1
            if event.key == pygame.K_k:
                addParticles(my_particles, "K")
                num_particles += 1

            if event.key == pygame.K_a:
                deleteParticles(my_particles, "Na")
                num_particles -= 1
            if event.key == pygame.K_s:
                deleteParticles(my_particles, "K")
                num_particles -= 1

            if event.key == pygame.K_RIGHT:
                step += 1
            if event.key == pygame.K_LEFT:
                if step != 0:
                    step -= 1

            if event.key == pygame.K_e:
                Ec = kineticEnergy(my_particles)
                print("Energia cinetica atual:", round(Ec, 2), "UA")

    if selected_particle:
        mouseX, mouseY = pygame.mouse.get_pos()
        dx = mouseX - selected_particle.x
        dy = mouseY - selected_particle.y
        selected_particle.angle = 0.5 * math.pi + math.atan2(dy, dx)
        selected_particle.speed = math.hypot(dx, dy) * 0.1

    # Preenche o background do ecra
    if step == 0:
        screen.fill(GRAY)
    if step == 1:
        screen.fill(WHITE)
    if step == 2:
        screen.fill(BLACK)
    if step == 3:
        step = 0

    for i, particle1 in enumerate(my_particles):
        particle1.move()
        particle1.bounce()
        membraneColision(particle1, membranes, num_membranes)
        particle1.display()
        if i == 0:
            Ec_array.append(kineticEnergy(my_particles))

        # calculos para o ddp
        deltaQ = float(calculateDC(my_particles)[2])
        ddp = float(deltaQ * eletronC) / capacitance
        ddp_array.append(ddp)

        # label para mostrar as cargas ao longo do programa
        label3 = font.render("Diferença de cargas: %i - %i = %i" % calculateDC(my_particles), True, WHITE, GRAY)

        for particle2 in my_particles[i + 1:num_particles]:
            colision(particle1, particle2)

        # Condicoes para a passagem de e captura de ioes
        for i, pump in enumerate(pumps):
            pump.displayLimits()
            if 0 <= i <= 2:
                if pump.status == 0:
                    pump.Na_Capture(particle1)
                    if pump.status == 1:
                        count += 1
            if i > 2:
                if pump.status == 0:
                    pump.K_capture(particle1)
                    if pump.status == 1:
                        count += 1
            pump.lockPump(particle1)

    # verifica se todas as bombas tem um iao capturado
    if count == 5:
        for b in pumps:
            b.ionPassage()
            b.status = 0
            b.ion = None
            count = 0

    # Desenha as membranas no ecra
    for membrane in membranes:
        membrane.drawPlatform()

    # Meter as legendas a aparecer no ecra
    label3Rect = label3.get_rect()
    label3Rect.center = (152, 40)
    screen.blit(label1, label1Rect)
    screen.blit(label2, label2Rect)
    screen.blit(label3, label3Rect)

    pygame.display.update()
pygame.quit()

# plot dos graficos de energia cinetica e de variacao de ddp
fig = plt.figure("Resumo de simulação")
p1 = fig.add_subplot(211)
plt.title("Representação gráfica da energia cinetica média dos iões")
plt.ylabel("Energia cinética média (UA)")
p1.plot(Ec_array)

p2 = fig.add_subplot(212)
p2.plot(ddp_array)
plt.title("Variação da diferença de potencial")
plt.xlabel("Numero de amostras")
plt.ylabel("Diferença de potencial (V)")
plt.show()
