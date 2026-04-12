from promptcruncher import crunch
result = crunch("Hello there! I would be absolutely more than happy to help you with your request today. It is important to remember that when you are writing code, you should always try to keep it clean. I hope this information is helpful to you and that you have a wonderful afternoon!", aggressive=True)
print(result.text)
result.report()