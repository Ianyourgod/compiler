import amp
print("AMP Version 0.0.1\nUse 'exit()' to exit")
while True:
    code = input(">>> ")
    if code == "exit()":
        break
    out,error = amp.main("<stdin>",code,1)
    if error:
        print(error)
    else:
        print(out)