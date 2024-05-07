import termcolor

def log(color: str, *args):
    print(termcolor.colored('|'.join(map(str, args)), color))

def err(*args):
    log('light_red', *args)

def fatal(*args):
    log('magenta', *args)