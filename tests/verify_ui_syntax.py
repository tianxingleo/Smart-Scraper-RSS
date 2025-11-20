import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Verifying UI modules syntax...")

try:
    from app.ui import layout
    print("[OK] app.ui.layout imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.layout import failed: {e}")

try:
    from app.ui.components import stats_card
    print("[OK] app.ui.components.stats_card imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.components.stats_card import failed: {e}")

try:
    from app.ui.components import data_table
    print("[OK] app.ui.components.data_table imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.components.data_table import failed: {e}")
