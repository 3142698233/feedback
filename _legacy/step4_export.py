with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ---- A: Replace exportStudents ----
old_export = "function exportStudents(){\n      const BOM='﻿';\n      const header='姓名,学段,学科,家长称呼,班级,上课计划\\n';\n      const rows=store.students.map(s=>{\n        const cls=store.classes.find(c=>c.studentIds.includes(s.id));\n        const cname=cls?cls.name:'';\n        const sc=cls&&cls.schedule?cls.schedule.map(x=>x.date+(x.time?' '+x.time:'')).join('|'):'';\n        return [s.name,GRADE_LABEL[s.grade]||'',SUBJECT_LABEL[s.subject]||'',s.parentName||'',cname,sc].join(',');\n      }).join('\\n');\n      const csv=BOM+header+rows;\n      const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});\n      const url=URL.createObjectURL(blob);\n      const a=document.createElement('a');\n      a.href=url;a.download='students-'+new Date().toISOString().slice(0,10)+'.csv';\n      a.click();URL.revokeObjectURL(url);\n      vant.showSuccessToast('导出成功');\n    }"

new_export = """function exportStudents(){
      const BOM='﻿';
      const header='姓名,学段,学科,家长称呼,班级,上课计划,学校,总课时,优点,缺点,选科,考试记录,反馈记录\\n';
      const escCSV=v=>{if(!v)return'';const s=String(v);return s.includes(',')||s.includes('"')||s.includes('\\n')?'"'+s.replace(/"/g,'""')+'"':s;};
      const rows=store.students.map(s=>{
        const p=s.profile||{};
        const cls=store.classes.find(c=>c.studentIds.includes(s.id));
        const cname=cls?cls.name:'';
        const sc=cls&&cls.schedule?cls.schedule.map(x=>x.date+(x.time?' '+x.time:'')).join('|'):'';
        return [
          escCSV(s.name),
          GRADE_LABEL[s.grade]||'',
          SUBJECT_LABEL[s.subject]||'',
          escCSV(s.parentName||''),
          escCSV(cname),
          sc,
          escCSV(p.school||''),
          escCSV(p.totalHours||0),
          escCSV(p.strengths||''),
          escCSV(p.weaknesses||''),
          escCSV((p.selectedSubjects||[]).join('|')),
          escCSV((p.exams||[]).map(e=>[e.name,e.score+'/'+e.totalScore,e.rank+'/'+e.totalRank,e.date,e.subject,e.note].filter(Boolean).join(':')).join('|')),
          escCSV(((store.feedbacks||{})[s.id]||[]).map(fb=>[fb.createdAt.slice(0,10),fb.type==='group'?'群':'个',fb.topic||'',(fb.resultText||'').slice(0,200).replace(/\\n/g,' ')].filter(Boolean).join(':')).join('||'))
        ].join(',');
      }).join('\\n');
      const csv=BOM+header+rows;
      const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      const a=document.createElement('a');
      a.href=url;a.download='students-'+new Date().toISOString().slice(0,10)+'.csv';
      a.click();URL.revokeObjectURL(url);
      vant.showSuccessToast('导出成功');
    }"""

if old_export in c:
    c = c.replace(old_export, new_export)
    print("Export updated")
else:
    print("Export NOT FOUND")

# ---- B: Replace importStudents start (from function to records.push) ----
old_import = "    function importStudents(e){\n      const file=e.target.files[0];\n      if(!file)return;\n      const reader=new FileReader();\n      reader.onload=ev=>{\n        try{\n          const text=ev.target.result;\n          const lines=text.replace(/^﻿/,'').split('\\n').filter(l=>l.trim());\n          if(lines.length<2){vant.showToast('文件为空或无数据');return;}\n          const records=[];const dupLines=[];\n          for(let i=1;i<lines.length;i++){\n            const cols=lines[i].split(',');\n            const name=(cols[0]||'').trim();\n            if(!name)continue;\n            const gradeVal=Object.entries(GRADE_LABEL).find(([,v])=>v===cols[1])?.[0]||'junior';\n            const subjectVal=Object.entries(SUBJECT_LABEL).find(([,v])=>v===cols[2])?.[0]||'math';\n            const parentName=(cols[3]||'').trim();\n            const cname=(cols[4]||'').trim();\n            const scRaw=(cols[5]||'').trim();\n            const schedule=scRaw?scRaw.split('|').filter(Boolean).map(s=>{const sp=s.indexOf(' ');return{date:sp>-1?s.slice(0,sp):s,time:sp>-1?s.slice(sp+1):''};}):[];\n            const exists=store.students.find(s=>s.name===name&&s.grade===gradeVal&&s.subject===subjectVal);\n            if(exists){\n              const oldCls=store.classes.find(c=>c.studentIds.includes(exists.id));\n              const oldCname=oldCls?oldCls.name:'(无)';\n              dupLines.push(name+'：班级 '+oldCname+' → '+(cname||'(无)'));\n            }\n            records.push({name,gradeVal,subjectVal,parentName,cname,schedule,exists});\n          }"

new_import = """    function importStudents(e){
      const file=e.target.files[0];
      if(!file)return;
      const reader=new FileReader();
      reader.onload=ev=>{
        try{
          const text=ev.target.result;
          const parseCSVLine=line=>{const result=[];let current='';let inQuotes=false;for(let i=0;i<line.length;i++){const ch=line[i];if(inQuotes){if(ch==='"'){if(i+1<line.length&&line[i+1]==='"'){current+='"';i++;}else{inQuotes=false;}}else{current+=ch;}}else{if(ch==='"'){inQuotes=true;}else if(ch===','){result.push(current);current='';}else{current+=ch;}}}result.push(current);return result;};
          const lines=text.replace(/^﻿/,'').split('\\n').filter(l=>l.trim());
          if(lines.length<2){vant.showToast('文件为空或无数据');return;}
          const headerCols=parseCSVLine(lines[0]);
          const hasProfile=headerCols.length>6;
          const records=[];const dupLines=[];
          for(let i=1;i<lines.length;i++){
            const cols=parseCSVLine(lines[i]);
            const name=(cols[0]||'').trim();
            if(!name)continue;
            const gradeVal=Object.entries(GRADE_LABEL).find(([,v])=>v===cols[1])?.[0]||'junior';
            const subjectVal=Object.entries(SUBJECT_LABEL).find(([,v])=>v===cols[2])?.[0]||'math';
            const parentName=(cols[3]||'').trim();
            const cname=(cols[4]||'').trim();
            const scRaw=(cols[5]||'').trim();
            const schedule=scRaw?scRaw.split('|').filter(Boolean).map(s=>{const sp=s.indexOf(' ');return{date:sp>-1?s.slice(0,sp):s,time:sp>-1?s.slice(sp+1):''};}):[];
            const school=hasProfile?(cols[6]||'').trim():'';
            const totalHours=hasProfile?parseInt(cols[7])||0:0;
            const strengths=hasProfile?(cols[8]||'').trim():'';
            const weaknesses=hasProfile?(cols[9]||'').trim():'';
            const selSubsRaw=hasProfile?(cols[10]||'').trim():'';
            const selectedSubjects=selSubsRaw?selSubsRaw.split('|').filter(Boolean):[];
            const examsRaw=hasProfile?(cols[11]||'').trim():'';
            let exams=[];
            if(examsRaw){examsRaw.split('|').forEach(part=>{const segs=part.split(':');if(segs.length>=1){const name=segs[0]||'';const scoreInfo=(segs[1]||'').split('/');const rankInfo=(segs[2]||'').split('/');exams.push({id:uid(),name,date:segs[3]||'',score:scoreInfo[0]||'',totalScore:scoreInfo[1]||'',rank:rankInfo[0]||'',totalRank:rankInfo[1]||'',subject:segs[4]||'',note:segs[5]||''});}});}
            const fbRaw=hasProfile?(cols[12]||'').trim():'';
            const feedbacks=[];
            if(fbRaw){fbRaw.split('||').forEach(part=>{const segs=part.split(':');if(segs.length>=3){feedbacks.push({createdAt:segs[0]+'T00:00:00.000Z',type:segs[1]==='群'?'group':'personal',topic:segs[2]||'',resultText:segs.slice(3).join(':')||'',photos:[],id:uid()});}});}
            const profile={strengths,weaknesses,selectedSubjects,totalHours,exams,school:school||''};
            const exists=store.students.find(s=>s.name===name&&s.grade===gradeVal&&s.subject===subjectVal);
            if(exists){
              const oldCls=store.classes.find(c=>c.studentIds.includes(exists.id));
              const oldCname=oldCls?oldCls.name:'(无)';
              dupLines.push(name+'：班级 '+oldCname+' → '+(cname||'(无)'));
            }
            records.push({name,gradeVal,subjectVal,parentName,cname,schedule,profile,feedbacks,exists});
          }"""

if old_import in c:
    c = c.replace(old_import, new_import)
    print("Import updated")
else:
    print("Import NOT FOUND")
    idx = c.find('function importStudents(e){')
    if idx >= 0:
        print(f"Found at {idx}: {c[idx:idx+100]}")

# ---- C: Update import student creation to include profile and feedbacks ----
old_push = "store.students.push({id:sid,name:r.name,grade:r.gradeVal,subject:r.subjectVal,parentName:r.parentName,classId:null,createdAt:new Date().toISOString(),profile:{strengths:\"\",weaknesses:\"\",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:\"\"}});"
new_push = "store.students.push({id:sid,name:r.name,grade:r.gradeVal,subject:r.subjectVal,parentName:r.parentName,classId:null,createdAt:new Date().toISOString(),profile:r.profile||{strengths:\"\",weaknesses:\"\",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:\"\"}});if(r.feedbacks&&r.feedbacks.length){if(!store.feedbacks[sid])store.feedbacks[sid]=[];store.feedbacks[sid].push(...r.feedbacks);}"
if old_push in c:
    c = c.replace(old_push, new_push)
    print("Import push updated")
else:
    print("Push NOT FOUND")

# ---- D: Update overwrite case ----
old_exists = "const stu=r.exists;\n                const oldCls"
new_exists = "const stu=r.exists;if(r.profile){stu.profile={...stu.profile,...r.profile};}\n                const oldCls"
if old_exists in c:
    c = c.replace(old_exists, new_exists)
    print("Overwrite updated")
else:
    print("Overwrite NOT FOUND")

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Step 4 done!")
