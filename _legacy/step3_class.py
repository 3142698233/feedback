with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ---- A: Replace class page HTML ----
old_start = '<div class="page" :class="{show:tab===\'classes\'}">'
old_end = '</div>\n\n<!-- ========== 历史页 ========== -->'

new_page = '''<div class="page" :class="{show:tab==='classes'}">
  <div style="background:#fff;padding:16px;border-bottom:1px solid #f0f0f0">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div style="font-size:18px;font-weight:700">🏫 班级 & 学生</div>
      <div style="display:flex;gap:6px">
        <van-button size="small" plain @click="triggerImport">📥 导入</van-button>
        <van-button size="small" plain @click="exportStudents">📤 导出</van-button>
      </div>
    </div>
  </div>

  <!-- 学生档案区 -->
  <div style="background:#fff;margin:12px 16px 0;border-radius:12px;padding:12px 14px;box-shadow:0 1px 3px rgba(0,0,0,.04)">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
      <div style="font-size:15px;font-weight:700">👤 学生档案 <span style="font-size:11px;color:#969799;font-weight:400">({{store.students.length}}人)</span></div>
      <van-button size="small" plain round @click="openAddStudent()">+ 新增学生</van-button>
    </div>
    <div v-if="!store.students.length" style="text-align:center;padding:20px 0;color:#c8c9cc">
      <div style="font-size:28px;margin-bottom:4px">📭</div>
      <div style="font-size:13px">暂无学生，点击右上角新增</div>
    </div>
    <div v-for="s in store.students" :key="s.id" style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f7f8fa">
      <div style="display:flex;align-items:center;gap:6px;flex:1;min-width:0">
        <span style="font-size:13px;cursor:pointer;color:#4f6ef7;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" @click="openStudentProfile(s.id)">{{s.name}}</span>
        <span class="badge" style="font-size:10px;flex-shrink:0">{{GRADE_LABEL[s.grade]||''}}</span>
        <span class="badge" style="font-size:10px;flex-shrink:0">{{SUBJECT_LABEL[s.subject]||''}}</span>
        <span v-if="(store.classes.find(c=>c.studentIds.includes(s.id))||{}).name" class="badge" style="font-size:10px;flex-shrink:0;background:#e8f3ff;color:#4f6ef7">📚{{store.classes.find(c=>c.studentIds.includes(s.id)).name}}</span>
      </div>
      <span style="color:#ee0a24;font-size:16px;cursor:pointer;padding:2px 4px;flex-shrink:0" @click="delStudent(s.id)">×</span>
    </div>
  </div>

  <!-- 班级管理区 -->
  <div style="margin-top:16px">
    <div style="padding:0 16px 8px;display:flex;justify-content:space-between;align-items:center">
      <div style="font-size:15px;font-weight:700">📚 班级管理</div>
      <van-button size="small" plain round @click="openAddClass">+ 新建班级</van-button>
    </div>
    <div v-if="!store.classes.length" style="text-align:center;padding:20px 0;color:#c8c9cc">
      <div style="font-size:24px;margin-bottom:4px">📭</div>
      <div style="font-size:12px">暂无班级</div>
    </div>
    <div v-for="c in store.classes" :key="c.id" class="class-card" style="margin:8px 16px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:15px;font-weight:600">{{c.name}}</span>
        <span style="font-size:11px;color:#c8c9cc;cursor:pointer" @click="delClass(c.id)">删除</span>
      </div>
      <div style="margin-top:4px">
        <span class="badge">{{GRADE_LABEL[c.grade]}}</span>
        <span class="badge">{{SUBJECT_LABEL[c.subject]}}</span>
        <span class="badge">{{c.studentIds.length}}名学生</span>
      </div>
      <div style="margin-top:4px;font-size:12px">
        <span v-if="!c.studentIds.length" style="color:#c8c9cc">暂无学生</span>
        <span v-for="sid in c.studentIds" :key="sid" style="display:inline-flex;align-items:center;margin-right:4px;background:#f0f4ff;border-radius:4px;padding:1px 4px">
          <span style="color:#4f6ef7;cursor:pointer" @click="openStudentProfile(sid)">{{sName(sid)}}</span>
          <span style="color:#c8c9cc;cursor:pointer;margin-left:2px;font-size:11px" @click="removeFromClass(sid,c.id)">×</span>
        </span>
      </div>
      <van-button size="small" plain round style="margin-top:6px" @click="editClass(c)">管理班级</van-button>
    </div>
    <input type="file" accept=".csv" ref="importFileInput" @change="importStudents" style="display:none"/>
  </div>
</div>

<!-- ========== 历史页 ========== -->'''

start_idx = c.find(old_start)
end_idx = c.find(old_end)
if start_idx >= 0 and end_idx >= 0:
    c = c[:start_idx] + new_page + c[end_idx + len(old_end):]
    print("Class page replaced")
else:
    print(f"NOT FOUND: start={start_idx}, end={end_idx}")

# ---- B: Add removeFromClass ----
old = "function delClass(id){store.classes=store.classes.filter(c=>c.id!==id);saveStore({...store});}"
new = old + "function removeFromClass(sid,cid){const c=store.classes.find(x=>x.id===cid);if(c){c.studentIds=c.studentIds.filter(x=>x!==sid);saveStore({...store});vant.showSuccessToast('已移除');}}"
if old in c:
    c = c.replace(old, new)
    print("removeFromClass added")

# ---- C: Add togClassStu ----
old = "function tog(arr,v){const i=arr.indexOf(v);if(i>-1)arr.splice(i,1);else arr.push(v);}"
new = old + "function togClassStu(sid){tog(classStuIds.value,sid);}"
if old in c:
    c = c.replace(old, new)
    print("togClassStu added")

# ---- D: Update class dialog student section ----
old = '''    <div class="section-label">添加学生加入班级</div>
    <div style="display:flex;flex-wrap:wrap">
      <span class="tag" style="border-style:dashed;color:#969799" @click="openAddStudent">+ 新增学生</span>
      <span v-for="s in classStuStudents" :key="s.id" class="tag on">{{s.name}}<span style="font-size:10px;color:#c8c9cc;margin-left:2px">{{GRADE_LABEL[s.grade]}}·{{SUBJECT_LABEL[s.subject]}}</span><span style="margin-left:4px;font-size:12px;cursor:pointer" @click.stop="openRename(s.id,s.name)">&#9998;</span><span class="del-x" style="margin-left:2px" @click.stop="classStuIds.splice(classStuIds.indexOf(s.id),1)">×</span></span>
      <span v-if="!classStuIds.length" style="font-size:12px;color:#c8c9cc;padding:4px">暂无学生</span>
    </div>'''

new = '''    <div class="section-label">选择学生加入班级（点击切换）</div>
    <div style="display:flex;flex-wrap:wrap;gap:4px;max-height:200px;overflow-y:auto">
      <span class="tag" style="border-style:dashed;color:#969799" @click="openAddStudent()">+ 新增学生</span>
      <span v-for="s in store.students" :key="s.id" class="tag" :class="{on:classStuIds.includes(s.id)}" @click="togClassStu(s.id)" style="cursor:pointer">{{s.name}}<span style="font-size:10px;color:#c8c9cc;margin-left:2px">{{GRADE_LABEL[s.grade]}}·{{SUBJECT_LABEL[s.subject]}}</span></span>
      <span v-if="!store.students.length" style="font-size:12px;color:#c8c9cc;padding:4px">暂无学生，请先在学生档案中添加</span>
    </div>'''

if old in c:
    c = c.replace(old, new)
    print("Class dialog student section updated")

# ---- E: Return block ----
c = c.replace('sName,gsf,tog,togPreTestStu', 'sName,gsf,tog,togClassStu,togPreTestStu')
c = c.replace('delClass,calDays', 'delClass,removeFromClass,calDays')

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Step 3 done!")
