#from os import environ
from random import randint, weibullvariate, random#, seed
from math import sin, cos, atan2, degrees, pi, log, floor
from warnings import catch_warnings#, copysign
from numpy import zeros
#from turtle import Screen, bgcolor
import pygame

pygame.init()
#seed(13)#3,13
#environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (5,35)

bg_color=(32, 33, 36)
bd_color=(123, 171, 160)
pth_color=(230, 197, 227)
hm_color=(190, 90, 255) #hm_color=(10, 60, 110)
nk_color=(207, 50, 141)
tg_color=(172, 224, 38)
DIS_WIDTH  = 950
DIS_HEIGHT = 1000
SPACE = (15,15,737,981)
background_pic = pygame.image.load("bg.png")
noise_pic = pygame.image.load("noise.png")
body_pic = []
i = 1
while i<=21:
	body_pic.append (pygame.image.load("bods/body"+str(i)+".png"))
	i+=1
digit_b_pic = []
i = 0
while i<=9:
	digit_b_pic.append (pygame.transform.scale(pygame.image.load("digits/digit_b_"+str(i)+".png"),(24,40)))
	i+=1
digit_w_pic = []
i = 0
while i<=9:
	digit_w_pic.append (pygame.transform.scale(pygame.image.load("digits/digit_w_"+str(i)+".png"),(24,40)))
	i+=1
#DIS_FIELD = 50
body_count = 11
body_count_min = 7
body_count_max = 10
body_radius = 50
body_dens_a = 7
body_dens_b = 1.5
body_dens_max = 50
damage_radius = 20
target_radius = 4
speed_number = 3 #10
grav_number = 4668.82828*speed_number**-1.98848 #50
grid_number = 20

#transp_surface = pygame.Surface((DIS_WIDTH,DIS_HEIGHT), pygame.SRCALPHA)
font = pygame.font.SysFont('Courier New', 20)
font_2 = pygame.font.Font('freesansbold.ttf', 40)

def make_screen():
	gamescreen=pygame.display.set_mode((DIS_WIDTH,DIS_HEIGHT))
	gamescreen.fill(bg_color)
	pygame.display.set_caption("G-Game")
	return gamescreen

def make_bods(cnt,rad,home):
	bods = []
	i=0
	while i < cnt:
		empty = False
		while not empty:
			r = randint(10,max(10,rad))
			x = round(randint(r+SPACE[0],SPACE[2]-r)/grid_number)*grid_number
			y = round(randint(SPACE[1]+r,SPACE[3]-r)/grid_number)*grid_number
			empty = collision_bod(bods,home,x,y,r)
		d = min(body_dens_max,body_dens_a/2 + weibullvariate(body_dens_a, body_dens_b))
		if randint(0,500) == 21: #1000
			r = 2.5
			d = body_dens_max*1000
		m = d * 4/3 * pi * r**3 * .000001
		body_pic_scaled = pygame.transform.scale(body_pic[randint(0,20)], (r*2+2, r*2+2))
		bods.append ((x,y,r,m,d,body_pic_scaled))
		i += 1
	return bods

def make_target(bods):
	n = 0
	m = 0
	i = 0
	while i <= body_count:
		b = bods[i]
		if b[2] > damage_radius:
			n = i
			break
		elif b[2] > m:
			m=b[2]
			n=i
		i+=1
	b = bods[n]
	a = random()*2*pi
	s = 10#randint(1,10)
	x = b[0]+b[2]*cos(a)
	y = b[1]+b[2]*sin(a)
	return [x,y,n,a,s]

def move_target(t,bods):
	a = t[3] + t[4]/100
	b = bods[t[2]]
	x = b[0]+b[2]*cos(a)
	y = b[1]+b[2]*sin(a)
	return [x,y,t[2],a,t[4]]

def color_grad(den):
	k=den/body_dens_max
	r = round(max(0,255 * (k-0.5)))
	g = round(max(0,255 * (1-2*k)))
	b = 255
	#t = 188
	return (min(127,r),g,b)

def color_grad_bis(val,top):
	val = max(0,min(val,top))
	r = round(val/top*255)
	g = round((1-val/top)*255)
	b = 0
	return(r,g,b)

def color_butt(on):
	if on:
		color = (124, 90, 219)
	else:
		color = (65, 47, 115)
	return color

def next_point(bods,point,vel):
	x = point[0]
	y = point[1]
	vx = vel[0]
	vy = vel[1]
	ax = 0
	ay = 0
	for b in bods:
		dx = b[0]-x
		dy = b[1]-y
		k = grav_number/(dx**2+dy**2)**1.5
		ax += dx*k*b[3]
		ay += dy*k*b[3]
	vx += ax
	vy += ay
	x += vx
	y += vy
	return [x,y,vx,vy]

def calc_path(bods,cnt,pos,vel,ang):
	path=[]
	path.append((pos[0],pos[1]))
	i=0
	x=pos[0]
	y=pos[1]
	vx=vel*cos(ang)
	vy=-vel*sin(ang)
	while i < cnt:
		x,y,vx,vy = next_point(bods,(x,y),(vx,vy))
		#x,y = i,i
		if collision_nuc(bods,pos,(x,y)):
			i = cnt+1
		else:
			path.append((x,y))
		i+=1
	return path

def calc_dist(bods,cnt,pos,vel,ang,tar):
	i=0
	j=0
	path=0
	x=pos[0]
	y=pos[1]
	dist = ((x-tar[0])**2+(y-tar[1])**2)**.5
	vx=vel*cos(ang)
	vy=vel*sin(ang)
	while i < cnt:
		x,y,vx,vy = next_point(bods,(x,y),(vx,vy))
		if collision_nuc(bods,pos,(x,y)):
			i = cnt+1
		else:
			if check_on_screen((x,y)):
				j+=1
			dist_next = ((x-tar[0])**2+(y-tar[1])**2)**.5
			if dist_next <= dist:				
				dist = dist_next
				path = j
		i+=1
	return (dist,path)

def collision_nuc(bods,home,pos):
	crash = False
	#if (home[0]-pos[0])**2+(home[1]-pos[1])**2 < home[2]**2:
	#	crash = True
	if not crash:
		for b in bods:
			if (b[0]-pos[0])**2+(b[1]-pos[1])**2 <= b[2]**2:
				crash = True
				break	
	return crash

def collision_bod(bods,home,x,y,r):
	empty = True
	if ((home[0]-x)**2+(home[1]-y)**2)**0.5 < home[2]+r+min(home[2],r):
		empty = False
	if empty:
		for b in bods:
			if ((b[0]-x)**2+(b[1]-y)**2)**0.5 < b[2]+r+min(b[2],r):
				empty = False
				break	
	return empty

def success(nuke,target):
  return ((nuke[0]-target[0])**2+(nuke[1]-target[1])**2)<=(damage_radius)**2

def make_field(bods):
	flows = []
	x=0
	grait = 0
	while x<=DIS_WIDTH:
		y=0
		while y<=DIS_HEIGHT:
			if not collision_nuc(bods,(-grid_number,-grid_number),(x,y)):
				ax = 0
				ay = 0
				for b in bods:
					dx = b[0]-x
					dy = b[1]-y
					k = grav_number/(dx**2+dy**2)**1.5
					ax += dx*k*b[3]
					ay += dy*k*b[3]
				#check_length (max or proportion)
				r = (ax**2+ay**2)**0.5
				flows.append ([x,y,ax,ay,r])
				if r > grait:
					grait = r
				#dot(x,y) #or arrow
			y+=grid_number
		x+=grid_number
	k_1 = grid_number/grait
	for f in flows:
		f[2]*=k_1
		f[3]*=k_1
		f[4]*=k_1
		#if f[4] < 3:
		#	k_2 = (log(3,m)*m/3)
		#	f[2]*=k_2
		#	f[3]*=k_2
		#	f[4]*=k_2
		#else:
		#	k_2 = log(f[4],m)*m / f[4]
		#	f[2]*=k_2
		#	f[3]*=k_2
		#	f[4]*=k_2
		k_2 = log(f[4]+1,grid_number) * (grid_number*1.01-0.77) / f[4]
		f[2]*=k_2
		f[3]*=k_2
		f[4]*=k_2		
	
	return flows

def make_field_bis(bods):
	flows_size_x = DIS_WIDTH // grid_number + 1
	flows_size_y = DIS_HEIGHT // grid_number + 1
	flows = zeros((flows_size_x, flows_size_y, 3))
	grait = 0
	for x in range(flows_size_x):
		for y in range(flows_size_y):
			if not collision_nuc(bods,(-grid_number,-grid_number),(x*grid_number,y*grid_number)):
				ax = 0
				ay = 0
				for b in bods:
					dx = b[0]-x*grid_number
					dy = b[1]-y*grid_number
					k = grav_number/(dx**2+dy**2)**1.5
					ax += dx*k*b[3]
					ay += dy*k*b[3]
				#check_length (max or proportion)
				r = (ax**2+ay**2)**0.5
				flows[x,y] = [ax,ay,r]
				if r > grait:
					grait = r
				#dot(x,y) #or arrow
			else:
				flows[x,y] = [0,0,0]
			y+=grid_number
		x+=grid_number
	k_1 = grid_number/grait*10
	grait = 0
	for line in flows:
		for f in line:
			if f[2] > 0:
				f[0]*=k_1
				f[1]*=k_1
				f[2]*=k_1
				k_2 = log(f[2]+1,grid_number) * (grid_number*1.01-0.77) / f[2]
				f[0]*=k_2
				f[1]*=k_2
				f[2]*=k_2		
	
	return flows

def angle_by_coord(pos_1,pos_2,angle_corr):
		angle = atan2((pos_1[1] - pos_2[1]), -(pos_1[0] - pos_2[0])) + angle_corr
		angle %= 2*pi
		return angle

def check_on_screen(coord):
	return coord[0]>=SPACE[0] and coord[0]<=SPACE[2] and coord[1]>=SPACE[1] and coord[1]<=SPACE[3]

def get_click(pos):
	b=-1
	if pygame.Rect(850,260,90,30).collidepoint(pos[0],pos[1]):
		b=0
	elif pygame.Rect(850,300,90,30).collidepoint(pos[0],pos[1]):
		b=1
	elif pygame.Rect(850,340,90,30).collidepoint(pos[0],pos[1]):
		b=3
	elif pygame.Rect(850,380,90,30).collidepoint(pos[0],pos[1]):
		b=4
	elif pygame.Rect(850,420,90,30).collidepoint(pos[0],pos[1]):
		b=5
	elif pygame.Rect(850,460,90,30).collidepoint(pos[0],pos[1]):
		b=6
	return b

def draw_digits(screen,angle):
	totalSeconds = angle * 360 * 60 * 60 / (2 * pi)
	seconds = round(totalSeconds % 60,0)
	minutes = floor((totalSeconds / 60) % 60)
	degrees = floor(totalSeconds / (60 * 60))

	w = 24
	h = 40

	g = 6

	x = 753
	y = 194+7

	screen.blit(digit_b_pic[floor(degrees/100)],(x, y))
	screen.blit(digit_b_pic[floor(degrees/10)%10],(x+w, y))
	screen.blit(digit_b_pic[floor(degrees%10)],(x+w*2, y))

	screen.blit(digit_w_pic[floor(minutes/10)],(x+w*3+g, y))
	screen.blit(digit_w_pic[floor(minutes%10)],(x+w*4+g, y))

	screen.blit(digit_w_pic[floor(seconds/10)],(x+w*5+g*2, y))
	screen.blit(digit_w_pic[floor(seconds%10)],(x+w*6+g*2, y))
	
def draw_frame(screen,bods,home,speed,ang_corr,path,flows,nuke,damage,target,buttons,coord):
	screen.fill(bg_color)	
	if buttons[0]:
		for x in range(DIS_WIDTH // grid_number + 1):
			for y in range(DIS_HEIGHT // grid_number + 1):		
				f = flows[x,y]
				if x > 0 and y > 0:
					f_left = flows[x-1,y]
					f_uupp = flows[x,y-1]
					pygame.draw.line(screen,bd_color,(x*grid_number+f[0],y*grid_number+f[1]),((x-1)*grid_number+f_left[0],(y)*grid_number+f_left[1]))
					pygame.draw.line(screen,bd_color,(x*grid_number+f[0],y*grid_number+f[1]),((x)*grid_number+f_uupp[0],(y-1)*grid_number+f_uupp[1]))
					#pygame.draw.line(screen,pth_color,(x*grid_number+f[0],y*grid_number+f[1]),(x*grid_number,y*grid_number))
	pygame.draw.circle(screen,tg_color,(target[0],target[1]),target_radius,0)
	#transp_surface.fill((0,0,0,0))
	for body in bods:
		pygame.draw.circle(screen,color_grad(body[4]),(body[0],body[1]),body[2])
		screen.blit(body[5], (body[0]-body[2], body[1]-body[2]))
		#pygame.draw.circle(transp_surface,color_grad(body[4]),(body[0],body[1]),body[2])
		#pygame.draw.circle(transp_surface,(30,224,33,100),(250,100),10)
	#screen.blit(transp_surface, (0,0))
	pygame.draw.circle(screen,hm_color,(home[0],home[1]),home[2],1)
	#if buttons[0]:
		#for f in flows: #эта была нормальной до сетки
			#pygame.draw.circle(screen,tg_color,(f[0],f[1]),1,0)
			#pygame.draw.line(screen,bd_color,(f[0],f[1]),(f[0]+f[2],f[1]+f[3])) #эта была нормальной до сетки
			
	if path:
		if buttons[2]:
			angle = angle_by_coord(home,pygame.mouse.get_pos(),ang_corr)
		else:
			angle = angle_by_coord(home,(nuke[2],nuke[3]),ang_corr)
		#coord = calc_path(bods,300,home,speed,angle)
		x = 752
		y = 566
		w = 188
		h = 88
		dirs = []
		dir_m = 0
		xa = []
		xam = 0
		ya = []
		yam = 0
		i=1
		while i < len(coord):
			if i % 2 == 0 and (coord[i][0]-target[0])**2 + (coord[i][1]-target[1])**2 > 200**2:
				color = pth_color
			else:
				color = bg_color
			if buttons[3] and check_on_screen(coord[i]) and check_on_screen(coord[i-1]):
				pygame.draw.line(screen,color,coord[i-1],coord[i])
			if buttons[1]:
				dirs.append(angle_by_coord(coord[i-1],coord[i],0))
				xa.append(coord[i][0]%DIS_WIDTH)
				ya.append(coord[i][1]%DIS_HEIGHT)
				if dirs[len(dirs)-1]>dir_m:
					dir_m = dirs[len(dirs)-1]
				#if xa[len(xa)-1]>xam:
				#	xam = xa[len(xa)-1]
				#if ya[len(ya)-1]>yam:
				#	yam = ya[len(ya)-1]
			i+=1
		screen.blit(background_pic,(0,0))
		pygame.draw.line(screen,(255,0,0),(758,546-speed*10*speed_number),(832,546-speed*10*speed_number),3)
		#text = font.render(str(speed), True, hm_color)
		#textRect = text.get_rect()
		#textRect.topright = (DIS_WIDTH, 0)
		#screen.blit(text, textRect)	
		pygame.draw.line(screen,(255,0,0),(845,96),(845+70*cos(angle),96-70*sin(angle)),3)
		draw_digits(screen,angle)
		if buttons[1]:
			#pygame.draw.rect(screen,hm_color,(x,y,w,h),2)
			i=1
			while i < w:
				screen.set_at((x+i, round(y+h-dirs[floor(i*len(dirs)/w)]*h/2/pi)), (255,0,0))
				screen.set_at((x+i, round(y+h-xa[floor(i*len(xa)/w)]*h/DIS_WIDTH)), (0,255,0))
				screen.set_at((x+i, round(y+h-ya[floor(i*len(ya)/w)]*h/DIS_HEIGHT)), (0,0,255))
				i+=1
	elif buttons[5]:
		draw_frame_def(screen,bods,home,target)		
	else:
		pygame.draw.circle(screen,nk_color,(nuke[0],nuke[1]),3,1)
		screen.blit(background_pic,(0,0))
	if damage:
		pygame.draw.circle(screen,bg_color,(nuke[0],nuke[1]),damage_radius,0)
		#pygame.draw.circle(screen,nk_color,(nuke[0],nuke[1]),damage_radius,1)
		pygame.draw.circle(screen,nk_color,(nuke[0],nuke[1]),2,0)
	pygame.draw.rect(screen,color_butt(buttons[0]),(850,260,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[1]),(850,300,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[3]),(850,340,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[4]),(850,380,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[5]),(850,420,90,30),0)
	make_text_butt(screen,"FIELDS",850+45, 260+15)
	make_text_butt(screen,"OSCILL",850+45, 300+15)
	make_text_butt(screen,"COURSE",850+45, 340+15)
	make_text_butt(screen,"MOTION",850+45, 380+15)
	make_text_butt(screen,"SURVEY",850+45, 420+15)
	pygame.draw.rect(screen,color_butt(False),(850,460,90,30),0)
	make_text_butt(screen,"RE-GEN",850+45, 460+15)

def make_text_butt(screen,string,x,y):
	text = font.render(string, True , tg_color)
	text_rect = text.get_rect()
	text_rect.center = (x, y)
	screen.blit(text,text_rect)

def draw_path(screen,coord,buttons,angle):
	xa = []
	ya = []
	dirs = []
	dir_m = 0
	x = 752
	y = 566
	w = 188
	h = 88

	i=1
	while i < len(coord):
		if i % 2 == 0:
			color = pth_color
		else:
			color = bg_color
		if check_on_screen(coord[i]) and check_on_screen(coord[i-1]):
			pygame.draw.line(screen,color,coord[i-1],coord[i])
		if buttons[1]:
			dirs.append(angle_by_coord(coord[i-1],coord[i],0))
			xa.append(coord[i][0]%DIS_WIDTH)
			ya.append(coord[i][1]%DIS_HEIGHT)
			if dirs[len(dirs)-1]>dir_m:
				dir_m = dirs[len(dirs)-1]
		i+=1
	draw_digits(screen,angle)
	if buttons[1]:
		i=1
		while i < w:
			screen.set_at((x+i, round(y+h-dirs[floor(i*len(dirs)/w)]*h/2/pi)), (255,0,0))
			screen.set_at((x+i, round(y+h-xa[floor(i*len(xa)/w)]*h/DIS_WIDTH)), (0,255,0))
			screen.set_at((x+i, round(y+h-ya[floor(i*len(ya)/w)]*h/DIS_HEIGHT)), (0,0,255))
			i+=1

def draw_frame_def(screen,bods,home,target,buttons,flows):
	xc = 846
	yc = 97
	rc = 80
	N = 15
	P = 300

	screen.fill(bg_color)
	screen.blit(background_pic,(0,0))

	pygame.draw.rect(screen,color_butt(buttons[0]),(850,260,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[1]),(850,300,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[3]),(850,340,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[4]),(850,380,90,30),0)
	pygame.draw.rect(screen,color_butt(buttons[5]),(850,420,90,30),0)
	make_text_butt(screen,"FIELDS",850+45, 260+15)
	make_text_butt(screen,"OSCILL",850+45, 300+15)
	make_text_butt(screen,"COURSE",850+45, 340+15)
	make_text_butt(screen,"MOTION",850+45, 380+15)
	make_text_butt(screen,"SURVEY",850+45, 420+15)
	pygame.draw.rect(screen,color_butt(False),(850,460,90,30),0)
	make_text_butt(screen,"RE-GEN",850+45, 460+15)

	#pygame.draw.circle(screen,nk_color,(x,y),r,1)
	pygame.draw.circle(screen,tg_color,(target[0],target[1]),target_radius,0)
	for body in bods:
		pygame.draw.circle(screen,color_grad(body[4]),(body[0],body[1]),body[2])
		screen.blit(body[5], (body[0]-body[2], body[1]-body[2]))
	pygame.draw.circle(screen,hm_color,(home[0],home[1]),home[2],1)

	D = rc/N
	R = [d*D for d in range(round(rc/D)+1)]
	T = [round(2*d*pi/1)*1 for d in range(round(rc/D)+1)]
	T[0] = 1

	p_max = -1
	d_win = 9999
	for i in range(len(R)):
		a_here = 0
		s_here = 0
		p_here = -1
		d_here = 9999
		for j in range(T[i]):
			r = R[i]
			angle = j*(2 * pi / T[i])
			speed = r/rc*7
			d_min,path = calc_dist(bods,P,home,speed,-angle,target)
			if p_max == -1 and d_min<d_win:
				d_win = d_min
				a_win = angle
				s_win = speed
			if d_min<30:
				if path > p_max:
					p_max = path
					a_win = angle
					s_win = speed
			if p_here == -1 and d_min<d_here:
				d_here = d_min
				a_here = angle
				s_here = speed
			if d_min<30:
				if path > p_max:
					p_here = path
					a_here = angle
					s_here = speed
			color = color_grad_bis(d_min,500)
			#screen.set_at((x,y), color)
			pygame.draw.circle(screen, color, (round(r*cos(angle) + xc),round(-r*sin(angle) + yc)), round(rc/N/2), 0)
		coord = calc_path(bods,P,home,s_here,a_here)
		draw_path(screen,coord,buttons,a_here)
		pygame.display.update()
	if p_max != -1:
		#screen.fill(bg_color)
		pygame.draw.rect(screen,bg_color,(SPACE[0],SPACE[1],SPACE[2]-SPACE[0],SPACE[3]-SPACE[1]))
		pygame.draw.rect(screen,(128,128,128),(752,566,188,89))
		screen.blit(noise_pic,(SPACE[0],SPACE[1]))
		pygame.draw.circle(screen,tg_color,(target[0],target[1]),target_radius,0)
		pygame.draw.circle(screen,hm_color,(home[0],home[1]),home[2],1)
		for body in bods:
			pygame.draw.circle(screen,color_grad(body[4]),(body[0],body[1]),body[2])
			screen.blit(body[5], (body[0]-body[2], body[1]-body[2]))
		coord = calc_path(bods,P,home,s_win,a_win)
		draw_path(screen,coord,buttons,a_win)

def is_dot_in_circle(dot,circle):
	return (dot[0]-circle[0])**2+(dot[1]-circle[1])**2 < circle[2]**2

def calc_mass_center(planet,holes): #planet[x,y,r], holes[[x,y,r],[x,y,r],...]
	sum_x = 0 #сумма дифференциалов по x
	sum_y = 0 #сумма дифференциалов по y
	count_x = 0 #количество дифференциалов по x
	count_y = 0 #количество дифференциалов по y
	step = 2 #шаг или размер дифференциала
	dy = planet[1] - planet[2] #от нижнего края планеты
	while dy <= planet[1] + planet[2]: #до верхнего края планеты
		dx = planet[0] - planet[2] #от левого края планеты
		while dx <= planet[0] + planet[2]: #до правого края планеты
			dot = (dx,dy) #дифференциированная точка 
			if is_dot_in_circle(dot,planet): #внутри планеты?
				it_is = True #да, внутри планеты
				for hole in holes: #для каждой воронки
					if is_dot_in_circle(dot,hole): #внутри воронки?
						it_is = False #нет, не внутри планеты
						break #дальше не ищем
				if it_is: #если внутри планеты - учитываем точку в расчете центра масс
					sum_x += dx
					sum_y += dy
					count_x += 1
					count_y += 1
			dx += step
		dy += step
	if count_x == 0 or count_y == 0: #оберег от деления на ноль
		return [planet[0], planet[1]]
	return [sum_x/count_x,sum_y/count_y] #расчет средних координат всех прошедших точек

def main_loop():
	clock=pygame.time.Clock()
	gamescreen = make_screen()
	
	state_gen = True
	state_aim = False
	state_fly = False
	state_res = False
	state_ext = False
   
	bods = []
	home = (100,100,5)
	#fields = False
	buttons = [False,True,False,False,False,False] #field,graph,angle_lock,path,rotation,defence

	while not state_ext:

		if state_gen:
			body_count = randint(body_count_min,body_count_max)
			bods = make_bods(body_count,body_radius,home)
			target = make_target(bods)
			momentum = 10
			angle_precision = 0 #2.2444
			buttons[2] = True
			if buttons[0]:
				flows = make_field_bis(bods)
				flows_exist = True
			else:
				flows = []
				flows_exist = False				
			nuke = [home[0],home[1],0,0]
			state_gen = False
			state_aim = True
			def_first = True
			momentum_prev = -1
			angle_prev = -1
			
		if state_aim:
			if buttons[5]:
				if def_first:
					draw_frame_def(gamescreen,bods,home,target,buttons,flows)
					def_first = False
			else:
				if buttons[4]:
					target = move_target(target,bods)
				if buttons[2]:
					angle = angle_by_coord(home,pygame.mouse.get_pos(),angle_precision)
				else:
					angle = angle_by_coord(home,(nuke[2],nuke[3]),angle_precision)
				if momentum_prev != momentum or angle_prev != angle:
					coord = calc_path(bods,500,home,momentum/speed_number,angle)
				draw_frame(gamescreen,bods,home,momentum/speed_number,angle_precision,True,flows,nuke,False,target,buttons,coord)#with path
				momentum_prev = momentum
				angle_prev = angle

		if state_fly:
			if buttons[4]:
				target = move_target(target,bods)
			nuke = next_point(bods,(nuke[0],nuke[1]),(nuke[2],nuke[3]))
			if collision_nuc(bods,home,nuke):
				state_fly = False
				state_res = True
			else:
				draw_frame(gamescreen,bods,home,0,0,False,flows,nuke,False,target,buttons,[])#with no path, no damage

		if state_res:
			draw_frame(gamescreen,bods,home,0,0,False,flows,nuke,True,target,buttons,[])#with damage
			if success(nuke,target):
				text = font.render("You win!", True, tg_color)
			else:
				text = font.render("You lose!", True, tg_color)
			textRect = text.get_rect()
			textRect.center = (DIS_WIDTH/2, DIS_HEIGHT/2)
			gamescreen.blit(text, textRect)
		
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				state_ext = True
			
			if event.type == pygame.MOUSEWHEEL:
				k=1
				if pygame.key.get_mods() & pygame.KMOD_SHIFT:
					k=10

				if not buttons[2] and pygame.Rect(753,194,78,54).collidepoint(pygame.mouse.get_pos()):
					angle_precision+=0.017453*event.y*k
				elif not buttons[2] and pygame.Rect(753+78,194,54,54).collidepoint(pygame.mouse.get_pos()):
					angle_precision+=0.000291*event.y*k
				elif not buttons[2] and pygame.Rect(753+78+54,194,54,54).collidepoint(pygame.mouse.get_pos()):
					angle_precision+=0.000005*event.y*k
				else:
					momentum+=event.y*k/10
					momentum = min(28,max(0,momentum))
			
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					butt_click = get_click(pygame.mouse.get_pos())
					if butt_click == -1:
						if state_aim:
							if buttons[2]:
								vx=momentum/speed_number*cos(angle_by_coord(home,pygame.mouse.get_pos(),angle_precision)) #/10
								vy=-momentum/speed_number*sin(angle_by_coord(home,pygame.mouse.get_pos(),angle_precision))
							else:
								vx=momentum/speed_number*cos(angle_by_coord(home,(nuke[2],nuke[3]),angle_precision))
								vy=-momentum/speed_number*sin(angle_by_coord(home,(nuke[2],nuke[3]),angle_precision))
							nuke = [home[0],home[1],vx,vy]
							state_fly = True
							state_aim = False
						elif state_fly:
							state_res = True
							state_fly = False
					elif butt_click == 6:
						state_gen = True
						state_aim = False
						state_fly = False
						state_res = False
						state_ext = False
					else:
						buttons[butt_click] = not buttons[butt_click]
						if buttons[0] and not flows_exist:
							flows = make_field_bis(bods)
						if butt_click == 5 and buttons[5]:
							def_first = True
				elif event.button == 3:
					buttons[2] = not buttons[2]
					(nuke[2],nuke[3]) = pygame.mouse.get_pos()
					angle_precision = 0
					#nuke[3] = pygame.mouse.get_pos()[1]

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					if state_res or state_aim:
						state_gen = True
						state_res = False
					else:
						state_res = True
						state_aim = False
						state_fly = False
				#elif event.key == pygame.K_f:
				#	fields = not fields
				#	if fields:
				#		flows = make_field(bods)
				#	else:
				#		flows = []
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_ESCAPE:
					state_ext = True

		pygame.display.update()
		clock.tick(30)

main_loop()
pygame.quit()
quit()
