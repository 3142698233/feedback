with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add profile migration in loadStore
old = "if(!d.tagConfig)d.tagConfig={};return d;"
new = "if(!d.tagConfig)d.tagConfig={};d.students=(d.students||[]).map(s=>({...s,profile:s.profile||{strengths:\"\",weaknesses:\"\",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:\"\"},...s.profile}));return d;"
if old in c:
    c = c.replace(old, new)
    print("1. loadStore migration added")
else:
    print("1. loadStore NOT FOUND")

# 2. Add profile to doAddStu
old = "store.students.push({id:sid,name:n,grade:addGrade.value,subject:addSubject.value,parentName:addParentName.value||'',classId:null,createdAt:new Date().toISOString()});"
new = "store.students.push({id:sid,name:n,grade:addGrade.value,subject:addSubject.value,parentName:addParentName.value||'',classId:null,createdAt:new Date().toISOString(),profile:{strengths:\"\",weaknesses:\"\",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:\"\"}});"
if old in c:
    c = c.replace(old, new)
    print("2. doAddStu updated")
else:
    print("2. doAddStu NOT FOUND")

# 3. Add profile to importStudents student push
old = "store.students.push({id:sid,name:r.name,grade:r.gradeVal,subject:r.subjectVal,parentName:r.parentName,classId:null,createdAt:new Date().toISOString()});"
new = "store.students.push({id:sid,name:r.name,grade:r.gradeVal,subject:r.subjectVal,parentName:r.parentName,classId:null,createdAt:new Date().toISOString(),profile:{strengths:\"\",weaknesses:\"\",selectedSubjects:[],totalHours:0,completedHours:0,exams:[],school:\"\"}});"
if old in c:
    c = c.replace(old, new)
    print("3. importStudents updated")
else:
    print("3. importStudents NOT FOUND")

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Step 1 done!")
