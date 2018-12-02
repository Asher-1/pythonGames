def indefinite(name):
  if name[0].lower() in 'aeiou': return "an " + name
  return "a " + name
  
def conjunction(strings):
  strings = list(strings)
  if len(strings) == 0:
    return ""
  elif len(strings) == 1:
    return strings[0]
  else:
    return ", ".join(strings[:-1]) + " and " + strings[-1]