with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ---- Part A: Add refs ----
old = "const editingClass=ref(null);"
new = "const editingClass=ref(null);const profileStudentId=ref(null);const showStudentProfile=ref(false);const showExamForm=ref(false);const examForm=reactive({id:'',name:'',date:'',score:'',totalScore:'',rank:'',totalRank:'',subject:'',note:''});"
if old in c:
    c = c.replace(old, new)
    print("Refs added")
else:
    print("Refs NOT FOUND")

# ---- Part B: Add computed ----
old = "const classStuStudents=computed(()=>store.students.filter(s=>classStuIds.value.includes(s.id)));"
new = "const classStuStudents=computed(()=>store.students.filter(s=>classStuIds.value.includes(s.id)));const profileStudent=computed(()=>store.students.find(s=>s.id===profileStudentId.value)||null);"
if old in c:
    c = c.replace(old, new)
    print("Computed added")
else:
    print("Computed NOT FOUND")

# ---- Part C: Add profile functions after delClass ----
old = "function delClass(id){store.classes=store.classes.filter(c=>c.id!==id);saveStore({...store});}\n\n    // 导入导出"
funcs = """function getStudentHours(sid){const s=store.students.find(x=>x.id===sid);const p=(s||{}).profile||{};const cls=store.classes.find(c=>c.studentIds.includes(sid));const autoCompleted=cls&&cls.schedule?cls.schedule.filter(s=>s.date<todayStr()).length:0;const scheduleTotal=cls&&cls.schedule?cls.schedule.length:0;return{completed:p.completedHours!=null?p.completedHours:autoCompleted,total:scheduleTotal};}function openStudentProfile(sid){profileStudentId.value=sid;showStudentProfile.value=true;}function saveStudentProfile(){const s=store.students.find(x=>x.id===profileStudentId.value);if(!s)return;s.profile={...s.profile};saveStore({...store});vant.showSuccessToast("已保存");}function resetExamForm(){examForm.id="";examForm.name="";examForm.date="";examForm.score="";examForm.totalScore="";examForm.rank="";examForm.totalRank="";examForm.subject="";examForm.note="";showExamForm.value=false;}function saveExam(){const s=store.students.find(x=>x.id===profileStudentId.value);if(!s||!examForm.name.trim()){vant.showToast("请输入考试名称");return;}if(examForm.id){const ex=s.profile.exams.find(e=>e.id===examForm.id);if(ex){Object.assign(ex,{name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,rank:examForm.rank,totalRank:examForm.totalRank,subject:examForm.subject,note:examForm.note});}}else{s.profile.exams.push({id:uid(),name:examForm.name.trim(),date:examForm.date,score:examForm.score,totalScore:examForm.totalScore,rank:examForm.rank,totalRank:examForm.totalRank,subject:examForm.subject,note:examForm.note});}resetExamForm();saveStudentProfile();}function editExam(e){examForm.id=e.id;examForm.name=e.name;examForm.date=e.date;examForm.score=e.score;examForm.totalScore=e.totalScore;examForm.rank=e.rank;examForm.totalRank=e.totalRank;examForm.subject=e.subject;examForm.note=e.note;showExamForm.value=true;}function delExam(eid){const s=store.students.find(x=>x.id===profileStudentId.value);if(s)s.profile.exams=s.profile.exams.filter(e=>e.id!==eid);saveStudentProfile();}"""
new = old + "\n" + funcs + "\n    // 导入导出"
if old in c and "getStudentHours" not in c:
    c = c.replace(old, new)
    print("Profile functions added")
else:
    print("Functions NOT FOUND or already exist")

# ---- Part D: Add profile dialog HTML before <!-- 添加学生弹窗 --> ----
dialog_html = """<!-- 学生档案弹窗 -->
<van-dialog v-model:show="showStudentProfile" :title="'📋 学生档案 - '+(profileStudent?profileStudent.name:'')" :show-confirm-button="false" close-on-click-overlay style="width:94%;max-width:520px">
  <div style="padding:8px 16px 12px;max-height:65vh;overflow-y:auto" v-if="profileStudent">
    <!-- 基本信息 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📌 基本信息</div>
    <div style="margin-bottom:12px;font-size:13px">
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">姓名</span><input :value="profileStudent.name" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.name=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学段</span><select :value="profileStudent.grade" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.grade=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option v-for="g in GRADES" :key="g.value" :value="g.value">{{g.label}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学科</span><select :value="profileStudent.subject" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.subject=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option v-for="s in SUBJECTS.filter(x=>(GRADE_SUBJECTS[profileStudent.grade]||[]).includes(x.value))" :key="s.value" :value="s.value">{{s.label}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">家长</span><input :value="profileStudent.parentName||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.parentName=e.target.value;}" placeholder="如：子涵妈妈" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">班级</span><select :value="(store.classes.find(c=>c.studentIds.includes(profileStudent.id))||{}).id||''" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(!st)return;const oldCls=store.classes.find(c=>c.studentIds.includes(st.id));if(oldCls)oldCls.studentIds=oldCls.studentIds.filter(x=>x!==st.id);const newCls=store.classes.find(c=>c.id===e.target.value);if(newCls)newCls.studentIds.push(st.id);}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option value="">未加入</option><option v-for="c in store.classes.filter(x=>x.grade===profileStudent.grade&&x.subject===profileStudent.subject)" :key="c.id" :value="c.id">{{c.name}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学校</span><input :value="(profileStudent.profile||{}).school||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.school=e.target.value;}" placeholder="未填写" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
    </div>

    <!-- 课时信息 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📊 课时信息</div>
    <div style="display:flex;gap:6px;align-items:center;margin-bottom:12px;font-size:13px;flex-wrap:wrap">
      <span style="color:#969799">总课时：</span><input type="number" min="0" :value="(profileStudent.profile||{}).totalHours||0" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.totalHours=parseInt(e.target.value)||0;}" style="width:46px;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:13px;text-align:center"/><span style="font-size:11px;color:#969799">h</span>
      <span style="color:#969799;margin-left:8px">已上：</span><input type="number" min="0" :value="getStudentHours(profileStudent.id).completed" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.completedHours=parseInt(e.target.value)||0;}" style="width:46px;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:13px;text-align:center"/><span style="font-size:11px;color:#969799">h</span>
      <span style="color:#969799;margin-left:8px">剩余：</span><span style="font-weight:600;font-size:14px" :style="{color:(profileStudent.profile||{}).totalHours-getStudentHours(profileStudent.id).completed<=0?'#ee0a24':'#07c160'}">{{Math.max(0,(profileStudent.profile||{}).totalHours-getStudentHours(profileStudent.id).completed)}}</span><span style="font-size:11px;color:#969799">h</span>
    </div>

    <!-- 选科（仅高中） -->
    <div v-if="profileStudent.grade==='senior'" style="margin-bottom:12px">
      <div style="font-weight:700;font-size:14px;margin-bottom:6px">📚 选考科目</div>
      <div style="display:flex;flex-wrap:wrap;gap:4px">
        <span v-for="sj in SUBJECTS.filter(x=>GRADE_SUBJECTS.senior.includes(x.value)&&x.category==='culture')" :key="sj.value" class="tag" style="font-size:11px;padding:4px 10px" :class="{on:(profileStudent.profile||{}).selectedSubjects.includes(sj.value)}" @click="()=>{const st=store.students.find(x=>x.id===profileStudentId);if(st){const arr=st.profile.selectedSubjects;const i=arr.indexOf(sj.value);i>-1?arr.splice(i,1):arr.push(sj.value);}}">{{sj.label}}</span>
      </div>
    </div>

    <!-- 优缺点 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">💪 学生优点</div>
    <textarea :value="(profileStudent.profile||{}).strengths||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.strengths=e.target.value;}" placeholder="记录学生的优点特长..." rows="2" style="width:100%;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px;resize:vertical;margin-bottom:12px;box-sizing:border-box"></textarea>
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">🔧 待改进</div>
    <textarea :value="(profileStudent.profile||{}).weaknesses||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.weaknesses=e.target.value;}" placeholder="记录需要改进的地方..." rows="2" style="width:100%;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px;resize:vertical;margin-bottom:12px;box-sizing:border-box"></textarea>

    <!-- 考试记录 -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <div style="font-weight:700;font-size:14px">📝 考试记录</div>
      <van-button size="small" plain round @click="resetExamForm();showExamForm=true">+ 添加</van-button>
    </div>
    <div v-if="!(profileStudent.profile||{}).exams||!((profileStudent.profile||{}).exams||[]).length" style="font-size:12px;color:#c8c9cc;padding:8px 0;margin-bottom:12px">暂无考试记录</div>
    <div v-for="ex in ((profileStudent.profile||{}).exams||[]).sort((a,b)=>b.date.localeCompare(a.date))" :key="ex.id" style="background:#f7f8fa;border-radius:8px;padding:8px 10px;margin-bottom:6px;font-size:12px;color:#323233">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:600">{{ex.name}}</span>
        <span style="color:#c8c9cc">{{ex.date}}</span>
      </div>
      <div style="margin-top:2px;color:#646566">
        <span v-if="ex.subject">{{SUBJECT_LABEL[ex.subject]||ex.subject}} · </span>
        <span v-if="ex.score">分数 {{ex.score}}<span v-if="ex.totalScore">/{{ex.totalScore}}</span></span>
        <span v-if="ex.rank" style="margin-left:6px">排名 {{ex.rank}}<span v-if="ex.totalRank">/{{ex.totalRank}}</span></span>
      </div>
      <div v-if="ex.note" style="margin-top:2px;color:#969799">{{ex.note}}</div>
      <div style="margin-top:4px;display:flex;gap:6px">
        <span style="color:#4f6ef7;cursor:pointer;font-size:11px" @click="editExam(ex)">编辑</span>
        <span style="color:#ee0a24;cursor:pointer;font-size:11px" @click="delExam(ex.id)">删除</span>
      </div>
    </div>

    <!-- 反馈历史 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📜 反馈记录</div>
    <div v-if="!((store.feedbacks||{})[profileStudent.id]||[]).length" style="font-size:12px;color:#c8c9cc;padding:8px 0">暂无反馈记录</div>
    <div v-for="fb in ((store.feedbacks||{})[profileStudent.id]||[]).sort((a,b)=>b.createdAt.localeCompare(a.createdAt)).slice(0,10)" :key="fb.id" style="background:#f7f8fa;border-radius:8px;padding:8px 10px;margin-bottom:4px;font-size:11px;color:#646566">
      <div style="display:flex;justify-content:space-between">
        <span :style="{color:fb.type==='group'?'#4f6ef7':'#323233'}">{{fb.type==='group'?'👥 群反馈':'👤 单独反馈'}}</span>
        <span style="color:#c8c9cc">{{fb.createdAt.slice(0,10)}}</span>
      </div>
      <div v-if="fb.topic" style="margin-top:2px;color:#323233">课题：{{fb.topic}}</div>
      <div style="margin-top:2px;white-space:pre-wrap;line-height:1.5;max-height:60px;overflow:hidden;text-overflow:ellipsis">{{fb.resultText.slice(0,100)}}</div>
    </div>
  </div>
  <div style="padding:8px 16px 12px;border-top:1px solid #f0f0f0">
    <van-button round block type="primary" @click="saveStudentProfile();showStudentProfile=false">保存并关闭</van-button>
  </div>
</van-dialog>

<!-- 考试表单弹窗 -->
<van-dialog v-model:show="showExamForm" :title="examForm.id?'编辑考试':'添加考试'" show-cancel-button @confirm="saveExam">
  <div style="padding:8px 16px 12px">
    <van-field v-model="examForm.name" placeholder="考试名称（如：期中考试）"></van-field>
    <div style="display:flex;gap:8px;margin-top:6px">
      <input type="date" v-model="examForm.date" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:14px"/>
    </div>
    <div style="display:flex;gap:8px;margin-top:6px">
      <input v-model="examForm.score" placeholder="分数" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>
      <input v-model="examForm.totalScore" placeholder="满分" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>
    </div>
    <div style="display:flex;gap:8px;margin-top:6px">
      <input v-model="examForm.rank" placeholder="排名" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>
      <input v-model="examForm.totalRank" placeholder="总人数" style="flex:1;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px"/>
    </div>
    <van-field v-model="examForm.note" placeholder="备注（可选）" style="margin-top:6px"></van-field>
  </div>
</van-dialog>

"""

old = "<!-- 添加学生弹窗 -->"
if old in c:
    c = c.replace(old, dialog_html + "\n" + old)
    print("Dialogs added")
else:
    print("Dialogs NOT FOUND")

# ---- Part E: Add to return block ----
c = c.replace(',showTemplateMgr,showSaveTemplate,showInfoPopup',
              ',showTemplateMgr,showSaveTemplate,showInfoPopup,showStudentProfile,profileStudentId,profileStudent,showExamForm,examForm')
c = c.replace(',delClass,calDays',
              ',delClass,getStudentHours,openStudentProfile,saveStudentProfile,resetExamForm,saveExam,editExam,delExam,calDays')

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Step 2 done!")
