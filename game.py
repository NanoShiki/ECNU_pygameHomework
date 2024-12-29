import time
import pygame
import random
import librosa
import numpy as np
import os

class Note:
    def __init__(self, resourcesPath, odd):
        self.color = (255, 255, 255)
        self.radius = 5.0           
        self.minRadius = 5.0        
        self.maxRadius = 30.0         
        self.timer = 0              #音符出现时间
        self.living = False        
        self.position = (0, 0)
        self.lifeCycle = 1.5        #音符生命周期
        self.restLife = 1.5         #音符剩余生命

        if odd:
            self.texture = pygame.image.load(resourcesPath + "红.png").convert_alpha()
        else:
            self.texture = pygame.image.load(resourcesPath + "蓝.png").convert_alpha()


    def spwan(self, position, color):
        self.position = position
        self.color = color
        self.radius = self.minRadius
        self.timer = time.time()
        self.living = True

    def update(self):
        duration = time.time() - self.timer
        self.radius = pygame.math.lerp(self.minRadius, self.maxRadius, min(duration * 4, 1))
        self.restLife = self.lifeCycle - duration
        if self.restLife <= 0: self.living = False    

class Particle:
    def __init__(self, position, color):
        self.x = position[0]
        self.y = position[1]
        self.color = color
        self.velocity = (random.uniform(-2, 2), random.uniform(-2, 2))
        self.size = random.randint(2, 4)
        self.lifeCycle = 0.5
        self.timer = time.time()
        self.restLife = 0.5
        self.living = True
    
    def update(self):
        duration = time.time() - self.timer
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.restLife = self.lifeCycle - duration
        if self.restLife <= 0: self.living = False


class Game:
    def __init__(self, resourcesPath):
        pygame.init()
        self.width, self.height = 800, 450
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.alpha = 90
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("艾尔登法球")
        pygame.display.flip()
        
        self.notes = []
        self.particles = []
        self.tryGenerateNote = False

        self.score = 0
        self.noteNum = 0
        self.lastNoteTimer = 0
        self.start_time = 0  # 记录游戏开始的时间
        self.odd = True
        self.path = resourcesPath
        self.audio_path = resourcesPath + "/一等情事.mp3"    #MP3路径
        
        self.font = pygame.font.Font(None, 36)
        self.noteInterval = 0.5        #音符生成间隔
 
    def generateParticles(self, notePos, color):
        for _ in range(8):
            particle = Particle(notePos, color)
            self.particles.append(particle)

    def updateAllParticles(self):
        newParticlesList = []
        for p in self.particles:
            if p.living:
                p.update()
                newParticlesList.append(p)
                pygame.draw.circle(self.screen, p.color, (p.x, p.y), p.size)
        self.particles = newParticlesList
    
    def generateNote(self):
        note = Note(self.path, self.odd)
        notePos = (random.randint(self.width //4, self.width // 4 * 3),
                            random.randint(self.height // 4, self.height // 4 * 3))
        if self.odd: noteCol = (150, 0, 0)
        else: noteCol = (0, 0, 150)
        self.odd = not self.odd
        note.spwan(notePos, noteCol)
        self.lastNoteTimer = note.timer
        self.notes.append(note)
        self.noteNum += 1
        self.tryGenerateNote = False

    def updateAllNotes(self):
        #更新所有note的状态
        newNotesList = []
        for n in self.notes:
            if n.living:
                n.update()
                newNotesList.append(n)

                newWidth = int(n.radius * 2)
                newHeight = int(n.radius * 2)
                scaledTexture = pygame.transform.scale(n.texture, (newWidth, newHeight))
                textureRec = scaledTexture.get_rect(center=n.position)
                self.screen.blit(scaledTexture, textureRec)
        self.notes = newNotesList

    def draw(self, frame):
        # 将帧绘制到 Pygame 窗口
        self.screen.blit(frame, (0, 0))
        transparent_rect_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_rect_surface, (0, 0, 0, self.alpha), (0, 0, self.width, self.height))
        self.screen.blit(transparent_rect_surface, (0, 0))

        self.updateAllNotes()
        self.updateAllParticles()

        #显示分数
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()
 
    def preLoadFrames(self, folder):
        # 提前加载所有动画
        frames = []
        loading_font = pygame.font.Font(None, 36)   #Loading字体
        filenames = sorted(os.listdir(folder))
        totalFrames = len(filenames)
        for frameIndex, filename in enumerate(filenames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
            if filename.endswith('.jpg'):
                imgPath = os.path.join(folder, filename)
                frame = pygame.image.load(imgPath)
                frames.append(frame)
            # 计算加载进度
            progress = (frameIndex + 1) / totalFrames
            progress_percent = int(progress * 100)
            progress_text = f"Loading: {progress_percent}%"
            #显示加载进度
            self.screen.fill((0, 0, 0))
            loading_text = loading_font.render(progress_text, True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
            menu = pygame.image.load(self.path + "/mainMenu.jpg")
            self.screen.blit(menu, (0, 0))
            self.screen.blit(loading_text, loading_rect)
            pygame.display.flip()
        return frames

    def get_beats(self):
        y_audio, sr = librosa.load(self.audio_path)
        _, beats = librosa.beat.beat_track(y=y_audio, sr=sr)
        x = librosa.frames_to_time(beats, sr=sr)
        y_audio, sr = librosa.load(self.audio_path)

        # 提取相应节拍的振幅作为Y坐标
        amplitude = []
        for i in range(len(beats) - 1):
            start_sample = librosa.frames_to_samples(beats[i])
            end_sample = librosa.frames_to_samples(beats[i + 1])
            segment = y_audio[start_sample:end_sample]
            amplitude.append(np.max(np.abs(segment)))  # 计算振幅

        y = amplitude  # 将振幅作为Y坐标

        # 只保留与x相匹配的y
        if len(y) < len(x): x = x[:len(y)]

        return x, y

    def run(self):
        clock = pygame.time.Clock()
        x, y = self.get_beats()
        i, j = 0, 0

        pygame.mixer.music.load(self.path + "Elden Ring Main Theme.mp3")
        pygame.mixer.music.play()
        # 提前加载所有动画
        frames = self.preLoadFrames(self.path + "frames")
        
        pygame.mixer.music.stop()
        pygame.mixer.music.unload() 

        pygame.mixer.music.load(self.audio_path)
        pygame.mixer.music.play()
        self.start_time = time.time()
        start_video = False

        while pygame.mixer.music.get_busy():
            #检测输入
            for event in pygame.event.get():
                #检测是否关闭程序
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    self.show_final_score()

                #检测是否按下ESC
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload() 
                        self.show_final_score()

                #检测鼠标点击
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    for n in self.notes:
                        noteRect = pygame.Rect(n.position[0] - n.maxRadius,
                                            n.position[1] - n.maxRadius,
                                            n.maxRadius * 2, n.maxRadius * 2)
                        if noteRect.collidepoint(mousePos):
                            self.score += 1
                            n.living = False
                            self.generateParticles(n.position, n.color) 

            #根据音频信息生成note
            if i < len(x) and time.time() - self.start_time - x[i] >= 0:
                if time.time() - self.start_time - x[i] >= 0.5: 
                    i += 1
                if time.time() - self.lastNoteTimer > self.noteInterval: 
                    if i < len(y) and y[i] > 0.25:
                        self.generateNote()

            #保证音画同步
            if time.time() - self.start_time > x[0] - int(x[0]) + 0.7:
                start_video = True
            if start_video:
                self.draw(frames[j])
                j += 1

            #限制帧数, 防止音画不同步
            clock.tick(30)

        self.show_final_score()
    
    def show_final_score(self):
        self.screen.fill((0, 0, 0))
        resultFont = pygame.font.Font(None, 36)
        resultText = f"Game Over! SCORE: {self.score}, TP: {self.score * 100 // self.noteNum}% press ESC to exit"
        resultText = resultFont.render(resultText, True, (255, 255, 255))
        resultRect = resultText.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(resultText, resultRect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():    
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

if __name__ == "__main__":
    print("\n游戏准备就绪,启动中...")

    #获取当前py文件所在的绝对路径(需要os库)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    dir = []
    for i in current_directory:
        if i == "\\":
            dir.append("/")
        else:
            dir.append(i)
    resourcesPath = ""
    for j in dir:
        resourcesPath += j
    resourcesPath += "/resources/"
    
    #启动游戏
    game = Game(resourcesPath)
    game.run()