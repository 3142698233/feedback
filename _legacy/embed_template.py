import os

# Read the markdown file
md_path = r"C:\Users\Yh\WorkBuddy\2026-05-20-task-6\12岁以下游泳课课后反馈细则.md"
with open(md_path, "r", encoding="utf-8") as f:
    swim_md = f.read()

# Escape for JavaScript template literal
swim_escaped = swim_md.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

src_path = os.path.join(os.path.dirname(__file__), "index.src.html")
with open(src_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find and replace FEEDBACK_TEMPLATES
start = content.find("const FEEDBACK_TEMPLATES={")
end = content.find("};", start) + 2

new_templates = "const FEEDBACK_TEMPLATES={\n  swimming:`" + swim_escaped + "`\n};"

content = content[:start] + new_templates + content[end:]

# Update fallback message
old_fb = "'暂无该科目话术模板，请联系彤彤老师添加'"
new_fb = "'该科目暂无话术模板，请联系彤彤老师添加'"
content = content.replace(old_fb, new_fb)

with open(src_path, "w", encoding="utf-8") as f:
    f.write(content)
print("OK - full swimming template embedded")
print(f"Template length: {len(swim_md)} chars")
