from PIL import Image, ImageDraw, ImageFont
import os

def create_rm_icon():
    """Создаем минималистичную иконку Review Maker в стиле Apple."""
    # Создаем изображение 256x256
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Прозрачный фон
    draw = ImageDraw.Draw(img)
    
    # Цвета из приложения (синий фон, оранжевые буквы)
    bg_color = (30, 41, 59, 255)  # #1e293b - синий из темы
    text_color = (251, 146, 60, 255)  # #fb923c - оранжевый из темы
    
    # Рисуем квадрат с округленными углами
    square_size = int(size * 0.8)
    square_left = (size - square_size) // 2
    square_top = (size - square_size) // 2
    corner_radius = 20
    
    # Рисуем скругленный прямоугольник
    draw.rounded_rectangle([square_left, square_top, 
                           square_left + square_size, square_top + square_size], 
                          radius=corner_radius, fill=bg_color)
    
    # Добавляем рыжую обводку скругленных углов (второй прямоугольник)
    border_color = (251, 146, 60, 255)  # Оранжевый цвет букв
    border_margin = 2
    border_size = square_size - border_margin * 2
    border_left = square_left + border_margin
    border_top = square_top + border_margin
    
    # Рисуем обводку как скругленный прямоугольник
    draw.rounded_rectangle([border_left, border_top, 
                           border_left + border_size, border_top + border_size], 
                          radius=corner_radius - border_margin, outline=border_color, width=1)
    
    # Рисуем буквы RM в стиле Apple
    try:
        # Используем Helvetica или похожий шрифт
        font = ImageFont.truetype("arialbd.ttf", 100)  # Arial Bold для жирности
    except:
        font = ImageFont.load_default()
    
    text = "RM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Строго по центру квадрата
    square_center_x = square_left + square_size // 2
    square_center_y = square_top + square_size // 2
    
    # Центрируем текст относительно его центра
    x = square_center_x - text_width // 2
    y = square_center_y - text_height // 2 - 55 + (text_height // 2)  # Опускаем на половину высоты букв
    
    # Рисуем буквы
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Для проверки - рисуем центральные линии
    draw.line([square_center_x, square_top, square_center_x, square_top + square_size], fill=(255,0,0,128), width=1)
    draw.line([square_left, square_center_y, square_left + square_size, square_center_y], fill=(255,0,0,128), width=1)
    
    # Сохраняем в разных размерах
    sizes = [16, 32, 48, 64, 128, 256]
    
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f'assets/icon_{s}x{s}.png')
    
    # Создаем .ico файл для Windows
    img.save('assets/review_generator.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    print("Минималистичная иконка Review Maker создана в папке assets/")

if __name__ == "__main__":
    create_rm_icon()
