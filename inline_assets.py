import os

def inline_assets():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    with open('style.css', 'r', encoding='utf-8') as f:
        css = f.read()
        
    with open('script.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # Regex or replace for strict matching
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')
    html = html.replace('<link rel="stylesheet" href="./static/style.css">', f'<style>\n{css}\n</style>')
    html = html.replace('<link rel="stylesheet" href="/static/style.css">', f'<style>\n{css}\n</style>')

    html = html.replace('<script src="script.js"></script>', f'<script>\n{js}\n</script>')
    html = html.replace('<script src="./static/script.js"></script>', f'<script>\n{js}\n</script>')
    html = html.replace('<script src="/static/script.js"></script>', f'<script>\n{js}\n</script>')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Inlining successful!")

if __name__ == '__main__':
    inline_assets()
