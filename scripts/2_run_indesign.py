"""
2_run_indesign.py
Запускає InDesign для кожного варіанту журналу
"""
import subprocess
import time
import sys
from pathlib import Path

class InDesignRunner:
    def __init__(self, indesign_path: str = None):
        """
        Ініціалізація
        
        Args:
            indesign_path: Шлях до InDesign (опціонально)
        """
        self.output_dir = Path('output')
        self.scripts_dir = Path('scripts')
        self.indesign_path = indesign_path
        
    def find_variants(self):
        """Знаходить всі варіанти для обробки"""
        if not self.output_dir.exists():
            return []
        
        variants = []
        for variant_dir in sorted(self.output_dir.iterdir()):
            if variant_dir.is_dir() and variant_dir.name.startswith('variant_'):
                plan_json = variant_dir / 'plan.json'
                if plan_json.exists():
                    variant_num = variant_dir.name.split('_')[-1]
                    variants.append({
                        'num': int(variant_num),
                        'dir': variant_dir,
                        'plan': plan_json
                    })
        
        return sorted(variants, key=lambda x: x['num'])
    
    def run_indesign_for_variant(self, variant: dict):
        """
        Запускає InDesign для одного варіанту
        
        Args:
            variant: Словник з даними варіанту
        """
        variant_num = variant['num']
        plan_json = variant['plan'].absolute()
        
        print(f"\n{'='*60}")
        print(f"📄 ОБРОБКА ВАРІАНТУ {variant_num}")
        print(f"{'='*60}")
        print(f"   План: {plan_json}")
        print(f"   Запускаю InDesign...")
        
        # Шлях до VBScript лончера
        vbs_script = self.scripts_dir / 'runjsx.vbs'
        
        if not vbs_script.exists():
            print(f"   ❌ VBScript не знайдено: {vbs_script}")
            print(f"   💡 Створіть файл runjsx.vbs для запуску InDesign")
            return False
        
        # Запускаємо через VBScript (для Windows)
        try:
            cmd = [
                'cscript',
                '//Nologo',
                str(vbs_script.absolute()),
                str(plan_json)
            ]
            
            print(f"   🔧 Команда: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 хвилин таймаут
            )
            
            if result.returncode == 0:
                print(f"   ✅ Варіант {variant_num} успішно оброблено!")
                print(f"   📁 Результати в: {variant['dir']}")
                return True
            else:
                print(f"   ❌ Помилка при обробці варіанту {variant_num}")
                if result.stderr:
                    print(f"   Помилка: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Таймаут! InDesign працює надто довго")
            return False
        except FileNotFoundError:
            print(f"   ❌ cscript не знайдено. Переконайтесь що запускаєте на Windows")
            return False
        except Exception as e:
            print(f"   ❌ Непередбачена помилка: {e}")
            return False
    
    def process_all_variants(self, pause_between: int = 5):
        """
        Обробляє всі варіанти
        
        Args:
            pause_between: Пауза між варіантами в секундах
        """
        print("\n" + "="*60)
        print("🚀 ЗАПУСК ГЕНЕРАЦІЇ ЖУРНАЛІВ")
        print("="*60)
        
        variants = self.find_variants()
        
        if not variants:
            print("\n❌ Варіанти не знайдені!")
            print("💡 Спочатку запустіть: python scripts/1_prepare_variants.py")
            return
        
        print(f"\n📋 Знайдено варіантів: {len(variants)}")
        
        # Підтвердження
        print("\n⚠️  InDesign буде запущено автоматично.")
        response = input("   Продовжити? (y/n): ")
        
        if response.lower() != 'y':
            print("❌ Скасовано")
            return
        
        # Обробка варіантів
        results = []
        
        for i, variant in enumerate(variants, 1):
            success = self.run_indesign_for_variant(variant)
            results.append({
                'variant': variant['num'],
                'success': success
            })
            
            # Пауза між варіантами (крім останнього)
            if i < len(variants):
                print(f"\n⏸️  Пауза {pause_between} сек перед наступним варіантом...")
                time.sleep(pause_between)
        
        # Підсумок
        print("\n" + "="*60)
        print("📊 ПІДСУМОК ОБРОБКИ")
        print("="*60)
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"\n✅ Успішно: {successful}/{len(results)}")
        if failed > 0:
            print(f"❌ Помилки: {failed}")
            print("\nВаріанти з помилками:")
            for r in results:
                if not r['success']:
                    print(f"   - Варіант {r['variant']}")
        
        if successful == len(results):
            print("\n🎉 ВСІ ВАРІАНТИ ГОТОВІ!")
            print(f"📂 Результати в папці: output/")
            print("\n💡 Наступні кроки:")
            print("   1. Перегляньте PDF файли в папках output/variant_*/")
            print("   2. Виберіть найкращий варіант")
            print("   3. Відкрийте .indd файл для фінальних правок")
        
        print()


def main():
    """Головна функція"""
    # Можна передати шлях до InDesign (опціонально)
    indesign_path = None
    if len(sys.argv) > 1:
        indesign_path = sys.argv[1]
    
    runner = InDesignRunner(indesign_path)
    runner.process_all_variants(pause_between=5)


if __name__ == '__main__':
    main()
