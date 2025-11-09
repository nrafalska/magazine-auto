"""
1_prepare_variants.py
Створює 3-5 варіантів плану журналу з одного брифа
"""
import json
import csv
import random
import shutil
from pathlib import Path
from typing import List, Dict

class MagazineVariantGenerator:
    def __init__(self, config_path: str = 'config/templates_config.json'):
        """Ініціалізація генератора"""
        self.config = self._load_config(config_path)
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """Завантажує конфігурацію шаблонів"""
        try:
            with open(config_path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Конфіг не знайдено: {config_path}")
            print("   Використовую базову конфігурацію")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Базова конфігурація якщо файл не знайдено"""
        return {
            "covers": {
                "fashion": [
                    {"file": "vogue_designes_scripts_label.idml", "page": 1}
                ],
                "minimal": [
                    {"file": "vogue_designes_scripts_label.idml", "page": 1}
                ]
            },
            "spreads": {
                "fashion": [
                    {"file": "julia_stula.idml", "pages": [2, 3]},
                    {"file": "julia_stula.idml", "pages": [4, 5]},
                    {"file": "julia_stula.idml", "pages": [6, 7]}
                ],
                "minimal": [
                    {"file": "julia_stula.idml", "pages": [2, 3]}
                ]
            }
        }
    
    def load_brief(self, csv_path: str) -> List[Dict]:
        """Читає бриф з CSV файлу"""
        try:
            with open(csv_path, encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            print(f"❌ CSV файл не знайдено: {csv_path}")
            return []
    
    def _get_random_template(self, template_type: str, style: str) -> Dict:
        """Вибирає випадковий шаблон"""
        templates = self.config.get(template_type, {}).get(style, [])
        if not templates:
            print(f"⚠️  Шаблони не знайдені для {template_type}/{style}")
            return None
        return random.choice(templates)
    
    def create_cover_page(self, cover_data: Dict, style: str) -> Dict:
        """Створює дані для обкладинки"""
        template = self._get_random_template('covers', style)
        if not template:
            return None
        
        return {
            "template": f"cover_{style}",
            "template_file": template['file'],
            "page": template['page'],
            "data": {
                "image1": cover_data.get('photo_path', ''),
                "title": cover_data.get('title', ''),
                "subtitle": cover_data.get('subtitle', '')
            }
        }
    
    def create_spread_page(self, spread_data: Dict, style: str) -> Dict:
        """Створює дані для розвороту"""
        template = self._get_random_template('spreads', style)
        if not template:
            return None
        
        # Розділяємо шляхи до фото (якщо їх 2)
        photos = spread_data.get('photo_path', '').split('|')
        left_photo = photos[0] if len(photos) > 0 else ''
        right_photo = photos[1] if len(photos) > 1 else photos[0]
        
        return {
            "template": f"spread_{style}",
            "template_file": template['file'],
            "pages": template['pages'],
            "data": {
                "left": {
                    "image1": left_photo,
                    "title": spread_data.get('title', ''),
                    "quote": spread_data.get('quote', '')
                },
                "right": {
                    "image1": right_photo,
                    "name": spread_data.get('name', ''),
                    "bio": spread_data.get('body_text', ''),
                    "facts": spread_data.get('facts', '').split('|') if spread_data.get('facts') else []
                }
            }
        }
    
    def create_variant(self, brief_data: List[Dict], variant_num: int, style: str = 'fashion') -> Dict:
        """
        Створює один варіант журналу
        
        Args:
            brief_data: Дані з CSV
            variant_num: Номер варіанту (1-5)
            style: Стиль журналу (fashion/minimal/family)
        """
        plan = {
            "project_name": f"magazine_variant_{variant_num}",
            "style": style,
            "variant": variant_num,
            "pages": []
        }
        
        # 1. Обкладинка (завжди перша)
        cover_rows = [row for row in brief_data if row.get('type') == 'cover']
        if cover_rows:
            cover_page = self.create_cover_page(cover_rows[0], style)
            if cover_page:
                plan['pages'].append(cover_page)
        
        # 2. Розвороти
        spread_rows = [row for row in brief_data if row.get('type') == 'spread']
        
        # ВАРІАТИВНІСТЬ: для варіантів 2+ міняємо порядок
        if variant_num > 1:
            random.seed(variant_num)  # Щоб варіанти були відтворювані
            spread_rows = spread_rows.copy()
            random.shuffle(spread_rows)
        
        for spread_row in spread_rows:
            spread_page = self.create_spread_page(spread_row, style)
            if spread_page:
                plan['pages'].append(spread_page)
        
        return plan
    
    def save_variant(self, plan: Dict, variant_num: int):
        """Зберігає план варіанту в JSON"""
        variant_dir = self.output_dir / f'variant_{variant_num}'
        variant_dir.mkdir(exist_ok=True)
        
        plan_path = variant_dir / 'plan.json'
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        return plan_path
    
    def generate_all_variants(self, brief_csv: str, num_variants: int = 5, style: str = 'fashion'):
        """
        Головна функція - генерує всі варіанти
        
        Args:
            brief_csv: Шлях до CSV файлу з брифом
            num_variants: Кількість варіантів (3-5)
            style: Стиль журналу
        """
        print("=" * 60)
        print("📰 ГЕНЕРАТОР ВАРІАНТІВ ЖУРНАЛУ")
        print("=" * 60)
        
        # Завантажуємо дані
        print(f"\n📄 Читаю бриф: {brief_csv}")
        brief_data = self.load_brief(brief_csv)
        
        if not brief_data:
            print("❌ Не вдалося завантажити бриф. Перевірте файл.")
            return
        
        print(f"   ✅ Завантажено {len(brief_data)} сторінок")
        
        # Створюємо варіанти
        print(f"\n🎨 Створюю {num_variants} варіантів (стиль: {style})...")
        print()
        
        created_variants = []
        
        for i in range(1, num_variants + 1):
            print(f"   Варіант {i}/{num_variants}...", end=' ')
            
            plan = self.create_variant(brief_data, i, style)
            plan_path = self.save_variant(plan, i)
            
            created_variants.append({
                'num': i,
                'path': plan_path,
                'pages': len(plan['pages'])
            })
            
            print(f"✅ ({plan['pages'].__len__()} сторінок)")
        
        # Підсумок
        print("\n" + "=" * 60)
        print("🎉 ГОТОВО!")
        print("=" * 60)
        print(f"\nСтворено {len(created_variants)} варіантів:")
        
        for variant in created_variants:
            print(f"   📁 Варіант {variant['num']}: {variant['path']}")
        
        print(f"\n💡 Наступний крок:")
        print(f"   python scripts/2_run_indesign.py")
        print()


def main():
    """Головна функція"""
    import sys
    
    # Параметри за замовчуванням
    brief_csv = 'input/client_brief.csv'
    num_variants = 5
    style = 'fashion'
    
    # Можна передати параметри через командний рядок
    if len(sys.argv) > 1:
        brief_csv = sys.argv[1]
    if len(sys.argv) > 2:
        num_variants = int(sys.argv[2])
    if len(sys.argv) > 3:
        style = sys.argv[3]
    
    # Створюємо генератор і запускаємо
    generator = MagazineVariantGenerator()
    generator.generate_all_variants(brief_csv, num_variants, style)


if __name__ == '__main__':
    main()
