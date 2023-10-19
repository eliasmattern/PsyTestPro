text = "_8__ Stunden / ___32 Minuten"
splitted_text = text.split("/")
result = []
result.append(''.join([i for i in splitted_text[0] if i.isdigit()])) 
if len(splitted_text) > 1:
    result.append(''.join([i for i in splitted_text[1] if i.isdigit()])) 
result = list(filter(lambda item: item, result))
answer = result[0] + ":" + result[1] if len(result) == 2 else result[0]

print(answer)