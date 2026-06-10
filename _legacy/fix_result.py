with open('index.src.html','r',encoding='utf-8') as f:
    c = f.read()
c = c.replace('<div v-if="result" style="padding:0 16px 4px">',
               '<div style="padding:0 16px 4px">')
c = c.replace('<div class="empty-hint" v-else>选择上方选项后自动生成，或点击「🤖 AI 生成」</div>', '')
with open('index.src.html','w',encoding='utf-8') as f:
    f.write(c)
print('Done')
