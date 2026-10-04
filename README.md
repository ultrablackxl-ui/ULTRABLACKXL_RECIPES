# UltrablackXL Recipes

Автоматичний каталог повноформатних відеорецептів каналу **UltrablackXL**.

## Як працює
- джерело: `https://www.youtube.com/@ultrablackxl6205/videos`;
- Shorts не імпортуються;
- відео не перезаливаються, а відтворюються з оригінального YouTube;
- `scripts/sync_youtube.py` синхронізує каталог;
- `scripts/build.py` створює статичну головну та окрему SEO-сторінку кожного рецепта;
- GitHub Actions щодня перевіряє нові повноформатні відео;
- GitHub Pages публікує тестову версію сайту.

## Локальна збірка
```bash
python scripts/build.py
python -m http.server 8000
```

V0.1: технічний фундамент. Далі: повна редакційна категоризація, інгредієнти, час приготування, порції, SEO-тексти та аналітика переходів.

Pages: enabled via GitHub Actions.

YouTube avatar auto-sync enabled.

SEO recipe pages V1 enabled.
