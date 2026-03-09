Set ws = CreateObject("Wscript.Shell")
ws.Run "cmd /c poetry run python simple_launcher.py", 0, False
