function exportStudents(){
      const BOM='﻿';
      const esc=v=>{if(v==null)return'';const s=String(v);return s.includes(',')||s.includes('"')||s.includes('\\n')?'"'+s.replace(/"/g,'""')+'"':s;};
      const dateStr=new Date().toISOString().slice(0,10);
      const lines=[];

      // 表1：学生基本信息
      lines.push('=== 学生基本信息 ===');
      lines.push('学生ID,姓名,学段,学科,家长称呼,学校,入班时间,班型');
      store.students.forEach(s=>{lines.push([s.id,esc(s.name),GRADE_LABEL[s.grade]||'',SUBJECT_LABEL[s.subject]||'',esc(s.parentName||''),esc((s.profile||{}).school||''),(s.profile||{}).enrollDate||'',esc((s.profile||{}).classType||'')].join(','));});

      // 表2：班级信息
      lines.push('');lines.push('=== 班级信息 ===');
      lines.push('班级ID,班级名称,学段,学科,上课计划');
      store.classes.forEach(c=>{lines.push([c.id,esc(c.name),GRADE_LABEL[c.grade]||'',SUBJECT_LABEL[c.subject]||'',esc((c.schedule||[]).map(x=>x.date+(x.time?' '+x.time:'')).join('|'))].join(','));});

      // 表3：班级学生关联
      lines.push('');lines.push('=== 班级学生关联 ===');
      lines.push('班级ID,班级名称,学生ID,学生姓名');
      store.classes.forEach(c=>{c.studentIds.forEach(sid=>{lines.push([c.id,c.name,sid,sName(sid)].join(','));});});

      // 表4：学生档案
      lines.push('');lines.push('=== 学生档案 ===');
      lines.push('学生ID,总课时,已上课时,选科');
      store.students.forEach(s=>{const p=s.profile||{};lines.push([s.id,esc(p.totalHours||0),esc(getStudentHours(s.id).completed),esc((p.selectedSubjects||[]).join('|'))].join(','));});

      // 表5：考试记录
      lines.push('');lines.push('=== 考试记录 ===');
      lines.push('考试ID,学生ID,名称,日期,分数,满分,班级排名,班级总人数,年级排名,年级总人数,科目,备注');
      store.students.forEach(s=>{const p=s.profile||{};(p.exams||[]).forEach(e=>{lines.push([e.id,s.id,esc(e.name),e.date,e.score||'',e.totalScore||'',e.classRank||'',e.classTotalCount||'',e.gradeRank||'',e.gradeTotalCount||'',esc(e.subject||''),esc(e.note||'')].join(','));});});

      // 表6：反馈记录
      lines.push('');lines.push('=== 反馈记录 ===');
      lines.push('反馈ID,学生ID,类型,保存日期,上课日期,开始时间,课题,课时,是否消课,出勤,专注度,理解度,反馈内容');
      store.students.forEach(s=>{(store.feedbacks[s.id]||[]).forEach(fb=>{lines.push([fb.id,s.id,fb.type||'',fb.createdAt.slice(0,10),fb.classDate||'',fb.classTimeExt||'',esc(fb.courseContent||fb.topic||''),fb.hours||'',fb.hoursCounted===false?'否':'是',fb.attendance||'',({very_focused:'高度专注',focused:'比较专注',distracted:'偶有分心',very_distracted:'容易走神'})[fb.focus]||fb.focus||'',({mastered:'完全掌握',mostly:'基本理解',partial:'部分理解',confused:'理解困难'})[fb.understand]||fb.understand||'',esc((fb.resultText||'').slice(0,500).replace(/\\n/g,' '))].join(','));});});

      const csv=BOM+lines.join('\\n');
      const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      const a=document.createElement('a');
      a.href=url;a.download='数据导出-'+dateStr+'.csv';
      a.click();URL.revokeObjectURL(url);
      vant.showSuccessToast('导出完成：6个数据表');
    }
