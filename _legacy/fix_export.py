with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the actual-newline-in-string issue in export
# Find and fix: .includes('\n')  where \n became actual newline
import re

# Replace actual newlines inside JS strings back to \n escapes
# Pattern: .includes('\n') with actual newline
broken1 = ".includes('\n')"
broken2 = ".replace(/\n/g,' ')"

# Find the export function boundaries
start = c.find('function exportStudents(){')
end = c.find('\n    }\n    function importStudents', start)
if end == -1:
    end = c.find('\n    function importStudents', start)

if start >= 0 and end >= 0:
    export_body = c[start:end+len('\n    }')]

    # Fix: replace actual newlines in JS strings with \n
    # The issue is that the export function has literal newlines where \n should be

    # Fix .includes('\n') - the \n became actual newline
    fixed = export_body
    # Replace the specific broken patterns
    fixed = fixed.replace(".includes('\n", ".includes('\\n")  # fix literal newline
    fixed = fixed.replace(".replace(/\n/g,' ')", ".replace(/\\n/g,' ')")
    fixed = fixed.replace(".join('\n')", ".join('\\n')")

    c = c[:start] + fixed + c[end+len('\n    }'):]
    print("Export fixed")
else:
    print("Export boundaries not found")

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done!")
