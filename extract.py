import re, json
with open('d:/AIstudioProxyAPI/AIstudioProxyAPI/launch_camoufox.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find logger.info("..."), logger.error("..."), etc.
matches = re.findall(r'logger\.(?:info|warning|error|debug|critical)\([f]?[\'"](.*?)[\'"]\)', text)
# Remove variables from f-strings for the base translation mapping if necessary, or just keep them as is.
# Some loggers are multi-line or have different formatting, but this will capture most.
unique_logs = list(set(matches))

with open('d:/AIstudioProxyAPI/AIstudioProxyAPI/logs.json', 'w', encoding='utf-8') as f:
    json.dump(unique_logs, f, indent=2, ensure_ascii=False)
print(f"Extracted {len(unique_logs)} logs.")
