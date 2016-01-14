import platform

collect_ignore = []

if platform.system() != 'Windows':
    collect_ignore.append('keyrings/alt/_win_crypto.py')
