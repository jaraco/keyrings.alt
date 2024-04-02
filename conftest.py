import platform

off_windows = platform.system() != 'Windows'

collect_ignore = [] + ['keyrings/alt/_win_crypto.py'] * off_windows
