"""Desenhos simples do vídeo 2: céu da boca (tela cheia), chupeta plantada e chupeta nos balões."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

F = "../../fonts3/"
ROXO = (127, 34, 191)
LILAS = (236, 226, 246)
ESCURO = (60, 30, 80)
S = 2   # desenha em 2x e reduz (bordas suaves)

def fonte(nome, tam):
    return ImageFont.truetype(F + nome, tam * S)

def chupeta(d, cx, cy, esc=1.0, ang=0, cor=(214, 160, 235)):
    """Chupeta de frente: escudo arredondado, bico e argola."""
    def R(x, y):
        a = math.radians(ang)
        return (cx * S + (x * math.cos(a) - y * math.sin(a)) * esc * S, cy * S + (x * math.sin(a) + y * math.cos(a)) * esc * S)
    # bico (atrás)
    pts = [R(-28 + 56 * t, -40 - 70 * math.sin(math.pi * t)) for t in [i / 30 for i in range(31)]]
    d.polygon(pts, fill=(250, 226, 190), outline=(190, 150, 110), width=2 * S)
    # escudo
    esc_pts = [R(95 * math.cos(t), -10 + 48 * math.sin(t) * (1.15 if math.sin(t) > 0 else 0.9)) for t in [i * math.pi / 40 for i in range(81)]]
    d.polygon(esc_pts, fill=cor, outline=ROXO, width=3 * S)
    # botão + argola
    bx, by = R(0, 10)
    d.ellipse([bx - 22 * esc * S, by - 22 * esc * S, bx + 22 * esc * S, by + 22 * esc * S], fill=ROXO)
    ax, ay = R(0, 62)
    d.ellipse([ax - 42 * esc * S, ay - 42 * esc * S, ax + 42 * esc * S, ay + 42 * esc * S], outline=ROXO, width=9 * S)

def cartao(w, h, cor):
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], 40 * S, fill=cor)
    return im, d

# ------------------------------------------------ chupeta plantada
def plantada(dst):
    w, h = 620, 520
    im, d = cartao(w, h, (247, 241, 252, 255))
    # vaso
    d.polygon([(170 * S, 330 * S), (450 * S, 330 * S), (415 * S, 480 * S), (205 * S, 480 * S)], fill=(205, 110, 70))
    d.rounded_rectangle([150 * S, 300 * S, 470 * S, 345 * S], 12 * S, fill=(185, 95, 60))
    d.ellipse([175 * S, 300 * S, 445 * S, 330 * S], fill=(110, 70, 45))
    # broto
    d.line([(310 * S, 305 * S), (310 * S, 170 * S)], fill=(80, 160, 80), width=8 * S)
    d.ellipse([230 * S, 150 * S, 312 * S, 200 * S], fill=(110, 190, 100))
    d.ellipse([308 * S, 120 * S, 395 * S, 172 * S], fill=(110, 190, 100))
    # chupeta "plantada" (meio enterrada, inclinada)
    chupeta(d, 235, 300, 0.62, -25)
    # presente que vai nascer
    gx, gy = 445, 120
    d.rounded_rectangle([gx * S, gy * S, (gx + 110) * S, (gy + 95) * S], 10 * S, fill=ROXO)
    d.rectangle([(gx + 47) * S, gy * S, (gx + 63) * S, (gy + 95) * S], fill=(255, 220, 120))
    d.rectangle([gx * S, (gy + 30) * S, (gx + 110) * S, (gy + 44) * S], fill=(255, 220, 120))
    d.ellipse([(gx + 25) * S, (gy - 28) * S, (gx + 55) * S, (gy + 4) * S], outline=(255, 220, 120), width=7 * S)
    d.ellipse([(gx + 55) * S, (gy - 28) * S, (gx + 85) * S, (gy + 4) * S], outline=(255, 220, 120), width=7 * S)
    for sx, sy in [(420, 95), (585, 160), (440, 255)]:
        r1, r2 = 15, 5
        estrela = [((sx + (r1 if i % 2 == 0 else r2) * math.cos(math.pi / 4 * i - math.pi / 2)) * S,
                    (sy + (r1 if i % 2 == 0 else r2) * math.sin(math.pi / 4 * i - math.pi / 2)) * S) for i in range(8)]
        d.polygon(estrela, fill=(255, 200, 80))
    d.text((310 * S, 40 * S), "Plantar a chupeta", font=fonte("KBPoppinsBold.ttf", 40), fill=ROXO, anchor="mm")
    im.resize((w, h), Image.LANCZOS).save(dst)

# ------------------------------------------------ chupeta nos balões
def baloes(dst):
    w, h = 620, 560
    im, d = cartao(w, h, (226, 240, 252, 255))
    for cx, cy, r in [(110, 120, 30), (520, 90, 26), (480, 420, 22)]:
        d.ellipse([(cx - 2 * r) * S, (cy - r) * S, (cx + 2 * r) * S, (cy + r) * S], fill=(255, 255, 255))
        d.ellipse([(cx - r) * S, (cy - 1.6 * r) * S, (cx + r * 1.2) * S, (cy + 0.6 * r) * S], fill=(255, 255, 255))
    cores = [(127, 34, 191), (190, 120, 230), (240, 120, 170), (120, 170, 240), (255, 190, 90)]
    centros = [(200, 150), (290, 110), (380, 150), (245, 215), (340, 215)]
    nx, ny = 310, 395
    for (bx, by), c in zip(centros, cores):
        d.line([(bx * S, (by + 58) * S), (nx * S, (ny - 40) * S)], fill=(120, 110, 130), width=3 * S)
    for (bx, by), c in zip(centros, cores):
        d.ellipse([(bx - 45) * S, (by - 58) * S, (bx + 45) * S, (by + 58) * S], fill=c)
        d.ellipse([(bx - 25) * S, (by - 40) * S, (bx - 10) * S, (by - 18) * S], fill=(255, 255, 255, 255))
        d.polygon([((bx - 8) * S, (by + 56) * S), ((bx + 8) * S, (by + 56) * S), (bx * S, (by + 66) * S)], fill=c)
    chupeta(d, nx, ny + 15, 0.62, 0)
    d.text((310 * S, 525 * S), "Rumo ao céu!", font=fonte("KBPoppinsBold.ttf", 38), fill=ROXO, anchor="mm")
    im.resize((w, h), Image.LANCZOS).save(dst)

# ------------------------------------------------ céu da boca (tela cheia)
def arco(d, cx, topo, larg, prof, cor_osso, dentes=True):
    """Corte frontal da arcada superior: osso + céu da boca + dentes."""
    pts_int = []
    for i in range(41):
        t = i / 40
        x = cx - larg / 2 + larg * t
        y = topo + prof * (1 - (2 * t - 1) ** 2) ** (0.5 if prof < 120 else 0.9) * -1
        pts_int.append((x, y + prof))
    base = topo + prof
    contorno = [(cx - larg / 2 - 70, base + 40), (cx - larg / 2 - 70, topo - 90), (cx + larg / 2 + 70, topo - 90),
                (cx + larg / 2 + 70, base + 40)]
    poly = [(cx + larg / 2 + 70, base + 40)] + [(x, y) for x, y in reversed(pts_int)][::-1][::-1] + [(cx - larg / 2 - 70, base + 40)]
    d.polygon([(x * S, y * S) for x, y in contorno], fill=cor_osso)
    d.polygon([(x * S, y * S) for x, y in [(cx - larg / 2 - 70, base + 40)] + pts_int + [(cx + larg / 2 + 70, base + 40)]],
              fill=(255, 255, 255))
    d.line([(x * S, y * S) for x, y in pts_int], fill=(200, 80, 110), width=7 * S)
    if dentes:
        for sx in (-1, 1):
            x0 = cx + sx * (larg / 2 + 10)
            d.rounded_rectangle([(x0 - 34) * S, (base + 5) * S, (x0 + 34) * S, (base + 95) * S], 14 * S,
                                fill=(255, 255, 255), outline=(180, 180, 190), width=3 * S)

def ceu_da_boca(dst):
    W, H = 1080, 1920
    im = Image.new("RGB", (W * S, H * S), LILAS)
    d = ImageDraw.Draw(im)
    t1 = fonte("KBPoppinsBold.ttf", 70)
    t2 = fonte("KBMontserratRegular.ttf", 42)
    d.text((540 * S, 340 * S), "O céu da boca", font=t1, fill=ROXO, anchor="mm")
    d.text((540 * S, 415 * S), "visto de frente", font=t2, fill=ESCURO, anchor="mm")
    cor_osso = (247, 200, 205)
    # sem chupeta
    d.rounded_rectangle([140 * S, 480 * S, 940 * S, 930 * S], 40 * S, fill=(255, 255, 255))
    d.text((540 * S, 530 * S), "Formato esperado", font=fonte("KBPoppinsSemiBold.ttf", 44), fill=ESCURO, anchor="mm")
    arco(d, 540, 690, 520, 70, cor_osso)
    d.text((540 * S, 880 * S), "céu da boca mais raso e largo", font=t2, fill=ESCURO, anchor="mm")
    # com chupeta prolongada
    d.rounded_rectangle([140 * S, 980 * S, 940 * S, 1450 * S], 40 * S, fill=(255, 255, 255))
    d.text((540 * S, 1030 * S), "Uso prolongado da chupeta", font=fonte("KBPoppinsSemiBold.ttf", 44), fill=ROXO, anchor="mm")
    arco(d, 540, 1150, 330, 140, cor_osso)
    # seta mostrando o aprofundamento
    d.line([(540 * S, 1282 * S), (540 * S, 1180 * S)], fill=ROXO, width=7 * S)
    d.polygon([(520 * S, 1195 * S), (560 * S, 1195 * S), (540 * S, 1160 * S)], fill=ROXO)
    d.text((540 * S, 1410 * S), "céu da boca fundo e estreito", font=t2, fill=ROXO, anchor="mm")
    im.resize((W, H), Image.LANCZOS).save(dst)

plantada("chupeta_plantada.png")
baloes("chupeta_baloes.png")
ceu_da_boca("ceu_da_boca.png")
print("ok")
