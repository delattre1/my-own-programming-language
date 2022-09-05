import my_own


while True:
    text = input('OWN> ')

    if text == 'quit()' or text == 'exit()':
        exit()

    #print(text)
    res, error = my_own.run(text)

    if error: print(error.as_string())
    else: print(res)
