import json

with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Read the old export function from the file
start = c.find('function exportStudents(){')
end = c.find('\n    }\n    function importStudents', start)
if end >= 0:
    old_export = c[start:end+len('\n    }')]
else:
    print("Export not found!")
    exit(1)

# Build the new export function with proper escaping
new_export = (
    'function exportStudents(){\n'
    "      const BOM='﻿';\n"
    "      const escCSV=v=>{if(!v)return'';const s=String(v);return s.includes(',')||s.includes('\"')||s.includes('\\n')?'\"'+s.replace(/\"/g,'\"\"')+'\"':s;};\n"
    "      const dateStr=new Date().toISOString().slice(0,10);\n"
    "      const header1='学生ID,姓名,学段,学科,家长称呼,学校,入班时间,总课时,优点,缺点,选科,考试记录,反馈记录\\n';\n"
    "      const rows1=store.students.map(s=>{\n"
    "        const p=s.profile||{};\n"
    "        return [s.id,escCSV(s.name),GRADE_LABEL[s.grade]||'',SUBJECT_LABEL[s.subject]||'',escCSV(s.parentName||''),escCSV(p.school||''),p.enrollDate||'',escCSV(p.totalHours||0),escCSV(p.strengths||''),escCSV(p.weaknesses||''),escCSV((p.selectedSubjects||[]).join('|')),escCSV((p.exams||[]).map(e=>[e.name,e.score+'/'+e.totalScore,e.classRank+'/'+e.classTotalCount,e.gradeRank+'/'+e.gradeTotalCount,e.date,e.subject,e.note].filter(Boolean).join(':')).join('|')),escCSV(((store.feedbacks||{})[s.id]||[]).map(fb=>[fb.createdAt.slice(0,10),fb.type==='group'?'群':'个',fb.topic||'',(fb.resultText||'').slice(0,200).replace(/\\n/g,' ')].filter(Boolean).join(':')).join('||'))].join(',');\n"
    "      }).join('\\n');\n"
    "      const csv1=BOM+header1+rows1;\n"
    "      const blob1=new Blob([csv1],{type:'text/csv;charset=utf-8'});\n"
    "      const url1=URL.createObjectURL(blob1);\n"
    "      const a1=document.createElement('a');\n"
    "      a1.href=url1;a1.download='学生档案-'+dateStr+'.csv';\n"
    "      a1.click();URL.revokeObjectURL(url1);\n"
    "      setTimeout(()=>{\n"
    "        const header2='班级名称,班级ID,学段,学科,学生ID,学生姓名,上课计划\\n';\n"
    "        const rows2=[];\n"
    "        store.classes.forEach(c=>{\n"
    "          const sc=c.schedule?c.schedule.map(x=>x.date+(x.time?' '+x.time:'')).join('|'):'';\n"
    "          if(c.studentIds.length){c.studentIds.forEach(sid=>{rows2.push([escCSV(c.name),c.id,GRADE_LABEL[c.grade]||'',SUBJECT_LABEL[c.subject]||'',sid,escCSV(sName(sid)),sc].join(','));});}\n"
    "          else{rows2.push([escCSV(c.name),c.id,GRADE_LABEL[c.grade]||'',SUBJECT_LABEL[c.subject]||'','','(无学生)',sc].join(','));}\n"
    "        });\n"
    "        const csv2=BOM+header2+rows2.join('\\n');\n"
    "        const blob2=new Blob([csv2],{type:'text/csv;charset=utf-8'});\n"
    "        const url2=URL.createObjectURL(blob2);\n"
    "        const a2=document.createElement('a');\n"
    "        a2.href=url2;a2.download='班级信息-'+dateStr+'.csv';\n"
    "        a2.click();URL.revokeObjectURL(url2);\n"
    "        vant.showSuccessToast('导出完成：学生档案 + 班级信息');\n"
    "      },500);\n"
    "    }"
)

c = c.replace(old_export, new_export)
print("Export replaced")

# Now apply all other changes

# enrollDate in profile
c = c.replace(
    'profile:s.profile||{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:""}',
    'profile:s.profile||{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:"",enrollDate:""}')
c = c.replace(
    'profile:{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:""}',
    'profile:{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:"",enrollDate:""}')

# Add enrollDate field to dialog after school
old_school = '<div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学校</span><input :value="(profileStudent.profile||{}).school||\'\'" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.school=e.target.value;}" placeholder="未填写" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>'
new_school = old_school + '\n      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">入班</span><input type="date" :value="(profileStudent.profile||{}).enrollDate||\'\'" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.enrollDate=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>'
c = c.replace(old_school, new_school)

# Exam field renames
c = c.replace(
    "examForm=reactive({id:'',name:'',date:'',score:'',totalScore:'',rank:'',totalRank:'',subject:'',note:''});",
    "examForm=reactive({id:'',name:'',date:'',score:'',totalScore:'',classRank:'',classTotalCount:'',gradeRank:'',gradeTotalCount:'',subject:'',note:''});")
c = c.replace(
    'examForm.rank="";examForm.totalRank="";examForm.subject="";examForm.note="";showExamForm.value=false;',
    'examForm.classRank="";examForm.classTotalCount="";examForm.gradeRank="";examForm.gradeTotalCount="";examForm.subject="";examForm.note="";showExamForm.value=false;')
c = c.replace(
    'examForm.totalRank=e.totalRank;examForm.subject=e.subject;examForm.note=e.note;showExamForm.value=true;',
    'examForm.classRank=e.classRank||"";examForm.classTotalCount=e.classTotalCount||"";examForm.gradeRank=e.gradeRank||"";examForm.gradeTotalCount=e.gradeTotalCount||"";examForm.subject=e.subject;examForm.note=e.note;showExamForm.value=true;')
c = c.replace(
    "Object.assign(ex,{name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,rank:examForm.rank,totalRank:examForm.totalRank,subject:examForm.subject,note:examForm.note});",
    "Object.assign(ex,{name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,classRank:examForm.classRank,classTotalCount:examForm.classTotalCount,gradeRank:examForm.gradeRank,gradeTotalCount:examForm.gradeTotalCount,subject:examForm.subject,note:examForm.note});")
c = c.replace(
    "s.profile.exams.push({id:uid(),name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,rank:examForm.rank,totalRank:examForm.totalRank,subject:examForm.subject,note:examForm.note});",
    "s.profile.exams.push({id:uid(),name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,classRank:examForm.classRank,classTotalCount:examForm.classTotalCount,gradeRank:examForm.gradeRank,gradeTotalCount:examForm.gradeTotalCount,subject:examForm.subject,note:examForm.note});")

# Save exam validation fix
c = c.replace(
    "function saveExam(){const s=store.students.find(x=>x.id===profileStudentId.value);if(!s||!examForm.name.trim()){vant.showToast('请输入考试名称');return;}",
    "function saveExam(){const s=store.students.find(x=>x.id===profileStudentId.value);if(!s||!examForm.name.trim()){vant.showToast('请输入考试名称');return false;}if(!examForm.date){vant.showToast('请选择考试日期');return false;}")
c = c.replace(
    '}resetExamForm();saveStudentProfile();}',
    '}resetExamForm();saveStudentProfile();showExamForm.value=false;}')

# Exam dialog before-close
c = c.replace(
    '<van-dialog v-model:show="showExamForm" :title="examForm.id?\'编辑考试\':\'添加考试\'" show-cancel-button @confirm="saveExam">',
    '<van-dialog v-model:show="showExamForm" :title="examForm.id?\'编辑考试\':\'添加考试\'" show-cancel-button :before-close="(action)=>action===\'cancel\'?true:(saveExam(),false)">')

# Exam display
c = c.replace(
    '<span v-if="ex.rank" style="margin-left:6px">排名 {{ex.rank}}<span v-if="ex.totalRank">/{{ex.totalRank}}</span></span>',
    '<span v-if="ex.classRank" style="margin-left:6px">班级 {{ex.classRank}}<span v-if="ex.classTotalCount">/{{ex.classTotalCount}}</span></span><span v-if="ex.gradeRank" style="margin-left:6px">年级 {{ex.gradeRank}}<span v-if="ex.gradeTotalCount">/{{ex.gradeTotalCount}}</span></span>')

# Exam form inputs
c = c.replace(
    '<input v-model="examForm.rank" placeholder="排名" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>\n      <input v-model="examForm.totalRank" placeholder="总人数" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>',
    '<input v-model="examForm.classRank" placeholder="班级排名" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>\n      <input v-model="examForm.classTotalCount" placeholder="班级总人数" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>\n    </div>\n    <div style="display:flex;gap:8px;margin-top:6px">\n      <input v-model="examForm.gradeRank" placeholder="年级排名" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>\n      <input v-model="examForm.gradeTotalCount" placeholder="年级总人数" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>')

# Import: handle new student archive format
c = c.replace(
    "const name=(cols[0]||'').trim();",
    "const hasStudentId=headerCols[0]==='学生ID';const importSid=hasStudentId?(cols[0]||'').trim():'';const nameColIdx=hasStudentId?1:0;const name=(cols[nameColIdx]||'').trim();")
c = c.replace(
    "const gradeVal=Object.entries(GRADE_LABEL).find(([,v])=>v===cols[1])?.[0]||'junior';\n            const subjectVal=Object.entries(SUBJECT_LABEL).find(([,v])=>v===cols[2])?.[0]||'math';\n            const parentName=(cols[3]||'').trim();\n            const cname=(cols[4]||'').trim();\n            const scRaw=(cols[5]||'').trim();",
    "const gIdx=hasStudentId?2:1;const sIdx=hasStudentId?3:2;const pIdx=hasStudentId?4:3;\n            const gradeVal=Object.entries(GRADE_LABEL).find(([,v])=>v===cols[gIdx])?.[0]||'junior';\n            const subjectVal=Object.entries(SUBJECT_LABEL).find(([,v])=>v===cols[sIdx])?.[0]||'math';\n            const parentName=(cols[pIdx]||'').trim();\n            const cname=hasStudentId?'':(cols[4]||'').trim();\n            const scRaw=hasStudentId?'':(cols[5]||'').trim();")
c = c.replace(
    "const school=hasProfile?(cols[6]||'').trim():'';",
    "const school=hasProfile?(hasStudentId?(cols[5]||'').trim():(cols[6]||'').trim()):'';")
c = c.replace(
    "const profile={strengths,weaknesses,selectedSubjects,totalHours,exams,school:school||''};",
    "const enrollDate=hasProfile&&hasStudentId?(cols[6]||'').trim():'';\n            const profile={strengths,weaknesses,selectedSubjects,totalHours,exams,school:school||'',enrollDate:enrollDate||''};")
c = c.replace(
    'profile:r.profile||{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:""}',
    'profile:r.profile||{strengths:"",weaknesses:"",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:"",enrollDate:""}')

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("All changes applied!")
