from PIL import Image, ImageDraw, ImageFont
import os

def create_rr_icon():
    """Создаем иконку RR на синем фоне."""
    # Создаем изображение 256x256
    size = 256
    img = Image.new('RGBA', (size, size), (0, 100, 200, 255))  # Синий фон
    draw = ImageDraw.Draw(img)
    
    # Рисуем буквы RR
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # Если Arial недоступен, используем стандартный
        font = ImageFont.load_default()
    
    # Позиции для букв RR
    text = "RR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Центрируем текст
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Рисуем белые буквы с тенью
    # Тень
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 50, 100, 200))
    # Основной текст
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # Добавляем градиентный эффект
    for i in range(5):
        alpha = 50 - i * 10
        draw.text((x - i, y - i), text, font=font, fill=(200, 220, 255, alpha))
    
    # Сохраняем в разных размерах
    sizes = [16, 32, 48, 64, 128, 256]
    
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f'assets/icon_{s}x{s}.png')
    
    # Создаем .ico файл для Windows
    img.save('assets/review_generator.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    print("Иконки созданы в папке assets/")

if __name__ == "__main__":
    create_rr_icon()
