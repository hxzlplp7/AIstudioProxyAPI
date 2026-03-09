import traceback
import sys

try:
    import launch_camoufox
except Exception as e:
    with open('d:/AIstudioProxyAPI/AIstudioProxyAPI/dump_error.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
