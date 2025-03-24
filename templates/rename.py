import re

email  = 'johnDoe12@gmail.com'

# pattern = r'^([a-zA-Z0-9.-_%+-]+)@'
pattern = r'^([a-zA-Z0-9._%+-]+)@'

if re.match(pattern, email):
    print(re.match(pattern, email).group(1))
else:
    print('Invalid Email')