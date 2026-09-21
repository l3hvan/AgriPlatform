import os

print("Already set as a real OS environment variable:", 'SECRET_KEY' in os.environ)

with open('.env') as f:
    found = False
    for line in f:
        if line.startswith('SECRET_KEY='):
            found = True
            raw_value = line[len('SECRET_KEY='):].rstrip('\n').rstrip('\r')
            print("Raw .env line length (before any processing):", len(raw_value))
            print("Contains a # character:", '#' in raw_value)
            break
    if not found:
        print("No SECRET_KEY= line found in .env at all!")