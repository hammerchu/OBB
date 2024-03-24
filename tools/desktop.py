import AppKit


# [(screen.frame().size.width, screen.frame().size.height)
#     for screen in AppKit.NSScreen.screens()]

for screen in AppKit.NSScreen.screens():
    print (screen.frame().size.width)
    print (screen.frame().size.height)
    print (screen.frame())

# from screeninfo import get_monitors
# for m in get_monitors():
#     print(str(m))