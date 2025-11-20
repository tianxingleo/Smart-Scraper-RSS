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

try:
    from app.ui.components import log_viewer
    print("[OK] app.ui.components.log_viewer imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.components.log_viewer import failed: {e}")

try:
    from app.ui.pages import dashboard
    print("[OK] app.ui.pages.dashboard imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.pages.dashboard import failed: {e}")

try:
    from app.ui.pages import sources
    print("[OK] app.ui.pages.sources imported successfully")
except Exception as e:
    print(f"[FAIL] app.ui.pages.sources import failed: {e}")
