with open('index.src.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ====== 1. Add classType to profile data model ======
# Migration
c = c.replace('exams:[],school:"",enrollDate:""}', 'exams:[],school:"",enrollDate:"",classType:""}')
# doAddStu already has the same pattern, second replace handles it
c = c.replace('exams:[],school:"",enrollDate:""}', 'exams:[],school:"",enrollDate:"",classType:""}')

# ====== 2. Compact basic info to 2 fields per row ======
old_info = '''    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📌 基本信息</div>
    <div style="margin-bottom:12px;font-size:13px">
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">姓名</span><input :value="profileStudent.name" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.name=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学段</span><select :value="profileStudent.grade" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.grade=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option v-for="g in GRADES" :key="g.value" :value="g.value">{{g.label}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学科</span><select :value="profileStudent.subject" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.subject=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option v-for="s in SUBJECTS.filter(x=>(GRADE_SUBJECTS[profileStudent.grade]||[]).includes(x.value))" :key="s.value" :value="s.value">{{s.label}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">家长</span><input :value="profileStudent.parentName||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.parentName=e.target.value;}" placeholder="如：子涵妈妈" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">班级</span><select :value="(store.classes.find(c=>c.studentIds.includes(profileStudent.id))||{}).id||''" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(!st)return;const oldCls=store.classes.find(c=>c.studentIds.includes(st.id));if(oldCls)oldCls.studentIds=oldCls.studentIds.filter(x=>x!==st.id);const newCls=store.classes.find(c=>c.id===e.target.value);if(newCls)newCls.studentIds.push(st.id);}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px;background:#fff"><option value="">未加入</option><option v-for="c in store.classes.filter(x=>x.grade===profileStudent.grade&&x.subject===profileStudent.subject)" :key="c.id" :value="c.id">{{c.name}}</option></select></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">学校</span><input :value="(profileStudent.profile||{}).school||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.school=e.target.value;}" placeholder="未填写" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
      <div style="display:flex;align-items:center;margin-bottom:4px"><span style="color:#969799;width:42px;flex-shrink:0">入班</span><input type="date" :value="(profileStudent.profile||{}).enrollDate||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.enrollDate=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:5px 8px;font-size:13px"/></div>
    </div>'''

new_info = '''    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📌 基本信息</div>
    <div style="margin-bottom:12px;font-size:13px;display:grid;grid-template-columns:1fr 1fr;gap:4px 8px">
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">姓名</span><input :value="profileStudent.name" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.name=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 6px;font-size:12px;min-width:0"/></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">学段</span><select :value="profileStudent.grade" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.grade=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:12px;background:#fff;min-width:0"><option v-for="g in GRADES" :key="g.value" :value="g.value">{{g.label}}</option></select></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">学科</span><select :value="profileStudent.subject" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.subject=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:12px;background:#fff;min-width:0"><option v-for="s in SUBJECTS.filter(x=>(GRADE_SUBJECTS[profileStudent.grade]||[]).includes(x.value))" :key="s.value" :value="s.value">{{s.label}}</option></select></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">家长</span><input :value="profileStudent.parentName||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.parentName=e.target.value;}" placeholder="如：子涵妈妈" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 6px;font-size:12px;min-width:0"/></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">班型</span><input :value="(profileStudent.profile||{}).classType||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.classType=e.target.value;}" placeholder="一对一/小班…" list="classTypeList" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 6px;font-size:12px;min-width:0"/><datalist id="classTypeList"><option value="一对一"/><option value="一对二"/><option value="一对三"/><option value="一对四"/><option value="小班"/><option value="大班"/></datalist></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">班级</span><select :value="(store.classes.find(c=>c.studentIds.includes(profileStudent.id))||{}).id||''" @change="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(!st)return;const oldCls=store.classes.find(c=>c.studentIds.includes(st.id));if(oldCls)oldCls.studentIds=oldCls.studentIds.filter(x=>x!==st.id);const newCls=store.classes.find(c=>c.id===e.target.value);if(newCls)newCls.studentIds.push(st.id);}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:12px;background:#fff;min-width:0"><option value="">未加入</option><option v-for="c in store.classes.filter(x=>x.grade===profileStudent.grade&&x.subject===profileStudent.subject)" :key="c.id" :value="c.id">{{c.name}}</option></select></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">学校</span><input :value="(profileStudent.profile||{}).school||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.school=e.target.value;}" placeholder="未填写" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 6px;font-size:12px;min-width:0"/></div>
      <div style="display:flex;align-items:center"><span style="color:#969799;width:36px;flex-shrink:0;font-size:12px">入班</span><input type="date" :value="(profileStudent.profile||{}).enrollDate||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st&&st.profile)st.profile.enrollDate=e.target.value;}" style="flex:1;border:1.5px solid #e8e8e8;border-radius:6px;padding:3px 4px;font-size:12px;min-width:0"/></div>
    </div>'''

if old_info in c:
    c = c.replace(old_info, new_info)
    print("Basic info compacted + classType added")
else:
    print("Basic info NOT FOUND - checking...")
    idx = c.find('📌 基本信息')
    if idx >= 0:
        print(f"Found at {idx}: {c[idx:idx+100]}")

# ====== 3. Remove strengths/weaknesses section ======
old_sw = '''    <!-- 优缺点 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">💪 学生优点</div>
    <textarea :value="(profileStudent.profile||{}).strengths||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.strengths=e.target.value;}" placeholder="记录学生的优点特长..." rows="2" style="width:100%;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px;resize:vertical;margin-bottom:12px;box-sizing:border-box"></textarea>
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">🔧 待改进</div>
    <textarea :value="(profileStudent.profile||{}).weaknesses||''" @input="(e)=>{const st=store.students.find(x=>x.id===profileStudentId);if(st)st.profile.weaknesses=e.target.value;}" placeholder="记录需要改进的地方..." rows="2" style="width:100%;border:1.5px solid #e8e8e8;border-radius:8px;padding:8px;font-size:13px;resize:vertical;margin-bottom:12px;box-sizing:border-box"></textarea>'''

if old_sw in c:
    c = c.replace(old_sw, '')
    print("Strengths/weaknesses removed")
else:
    print("S/W section NOT FOUND")

# ====== 4. Replace exam records with table + deltas ======
# This is complex - need to show table with score delta and rank delta
# Remove old exam section
old_exam_start = '<!-- 考试记录 -->'
old_exam_section_start = c.find(old_exam_start)
if old_exam_section_start >= 0:
    # Find the end of exams section (before <!-- 反馈历史 -->)
    feedback_start = c.find('<!-- 反馈历史 -->', old_exam_section_start)
    if feedback_start >= 0:
        old_exam_section = c[old_exam_section_start:feedback_start]

        new_exam_section = '''<!-- 考试记录 -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <div style="font-weight:700;font-size:14px">📝 考试记录</div>
      <van-button size="small" plain round @click="resetExamForm();showExamForm=true">+ 添加</van-button>
    </div>
    <div v-if="!(profileStudent.profile||{}).exams||!((profileStudent.profile||{}).exams||[]).length" style="font-size:12px;color:#c8c9cc;padding:8px 0;margin-bottom:12px">暂无考试记录</div>
    <div v-else style="overflow-x:auto;margin-bottom:12px;font-size:11px">
      <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:1px;background:#e8e8e8;border-radius:8px;overflow:hidden">
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">名称</div>
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">日期</div>
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">分数</div>
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">±分</div>
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">排名</div>
        <div style="background:#f7f8fa;padding:5px 4px;font-weight:600;text-align:center">±名</div>
        <template v-for="(ex,i) in ((profileStudent.profile||{}).exams||[]).sort((a,b)=>a.date.localeCompare(b.date))" :key="ex.id">
          <template v-for="prev in [((profileStudent.profile||{}).exams||[]).sort((a,b)=>a.date.localeCompare(b.date))[i-1]]">
            <div style="background:#fff;padding:5px 4px;cursor:pointer;text-align:center" @click="editExam(ex)">{{ex.name}}</div>
            <div style="background:#fff;padding:5px 4px;text-align:center">{{ex.date}}</div>
            <div style="background:#fff;padding:5px 4px;text-align:center" @click="editExam(ex)">{{ex.score}}<span v-if="ex.totalScore">/{{ex.totalScore}}</span></div>
            <div style="background:#fff;padding:5px 4px;text-align:center" :style="{color:(ex.score&&prev&&prev.score?(+ex.score>+prev.score?'#07c160':+ex.score<+prev.score?'#ee0a24':'#969799'):'#969799')}">{{ex.score&&prev&&prev.score?((+ex.score)-(+prev.score)>0?'+':'')+((+ex.score)-(+prev.score)):'-'}}</div>
            <div style="background:#fff;padding:5px 4px;text-align:center" @click="editExam(ex)">{{ex.classRank||'-'}}<span v-if="ex.classTotalCount">/{{ex.classTotalCount}}</span></div>
            <div style="background:#fff;padding:5px 4px;text-align:center" :style="{color:(ex.classRank&&prev&&prev.classRank?(+ex.classRank<+prev.classRank?'#07c160':+ex.classRank>+prev.classRank?'#ee0a24':'#969799'):'#969799')}">{{ex.classRank&&prev&&prev.classRank?((+prev.classRank)-(+ex.classRank)>0?'+':'')+((+prev.classRank)-(+ex.classRank)):'-'}}</div>
          </template>
        </template>
      </div>
      <div style="font-size:10px;color:#c8c9cc;margin-top:4px;text-align:center">点击分数/排名可编辑，±为较上次的增减</div>
    </div>'''

        c = c[:old_exam_section_start] + new_exam_section + c[feedback_start:]
        print("Exam table with deltas added")
    else:
        print("Feedback section not found")
else:
    print("Exam section not found")

# ====== 5. Feedback records: compact, click to expand ======
old_fb_section = '''<!-- 反馈历史 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📜 反馈记录</div>
    <div v-if="!((store.feedbacks||{})[profileStudent.id]||[]).length" style="font-size:12px;color:#c8c9cc;padding:8px 0">暂无反馈记录</div>
    <div v-for="fb in ((store.feedbacks||{})[profileStudent.id]||[]).sort((a,b)=>b.createdAt.localeCompare(a.createdAt)).slice(0,10)" :key="fb.id" style="background:#f7f8fa;border-radius:8px;padding:8px 10px;margin-bottom:4px;font-size:11px;color:#646566">
      <div style="display:flex;justify-content:space-between">
        <span :style="{color:fb.type==='group'?'#4f6ef7':'#323233'}">{{fb.type==='group'?'👥 群反馈':'👤 单独反馈'}}</span>
        <span style="color:#c8c9cc">{{fb.createdAt.slice(0,10)}}</span>
      </div>
      <div v-if="fb.topic" style="margin-top:2px;color:#323233">课题：{{fb.topic}}</div>
      <div style="margin-top:2px;white-space:pre-wrap;line-height:1.5;max-height:60px;overflow:hidden;text-overflow:ellipsis">{{fb.resultText.slice(0,100)}}</div>
    </div>'''

# Add showFbDetail ref if not exists
if 'showFbDetail' not in c:
    c = c.replace("const showHoursLog=ref(false);",
                  "const showHoursLog=ref(false);const showFbDetail=ref(false);const fbDetail=ref(null);")

new_fb_section = '''<!-- 反馈历史 -->
    <div style="font-weight:700;font-size:14px;margin-bottom:6px">📜 反馈记录 <span v-if="((store.feedbacks||{})[profileStudent.id]||[]).length" style="font-size:11px;color:#969799;font-weight:400">({{((store.feedbacks||{})[profileStudent.id]||[]).length}}条)</span></div>
    <div v-if="!((store.feedbacks||{})[profileStudent.id]||[]).length" style="font-size:12px;color:#c8c9cc;padding:8px 0">暂无反馈记录</div>
    <div v-for="fb in ((store.feedbacks||{})[profileStudent.id]||[]).sort((a,b)=>b.createdAt.localeCompare(a.createdAt))" :key="fb.id" style="display:flex;justify-content:space-between;align-items:center;padding:5px 8px;margin-bottom:2px;background:#f7f8fa;border-radius:6px;cursor:pointer;font-size:12px" @click="fbDetail=fb;showFbDetail=true">
      <span>{{fb.classDate||fb.createdAt.slice(0,10)}} {{weekday(fb.classDate||fb.createdAt.slice(0,10))}}</span>
      <span style="color:#c8c9cc">{{fb.type==='group'?'👥群':'👤个'}} {{fb.courseContent||fb.topic||''}}</span>
    </div>

    <!-- 反馈详情弹窗 -->
    <van-dialog v-model:show="showFbDetail" :title="'📜 反馈详情 - '+(fbDetail?fbDetail.classDate||fbDetail.createdAt.slice(0,10):'')" show-cancel-button cancel-button-text="关闭" :show-confirm-button="false" @cancel="showFbDetail=false">
      <div style="padding:8px 16px 16px;max-height:60vh;overflow-y:auto" v-if="fbDetail">
        <div style="font-size:12px;color:#969799;margin-bottom:8px">
          <span>{{fbDetail.type==='group'?'👥 群反馈':'👤 单独反馈'}}</span>
          <span style="margin-left:8px">{{fbDetail.createdAt.slice(0,10)}}</span>
          <span v-if="fbDetail.classDate&&fbDetail.classDate!==fbDetail.createdAt.slice(0,10)" style="margin-left:4px">上课：{{fbDetail.classDate}}</span>
        </div>
        <div v-if="fbDetail.topic||fbDetail.courseContent" style="font-size:13px;color:#323233;margin-bottom:8px"><b>课题：</b>{{fbDetail.courseContent||fbDetail.topic}}</div>
        <div v-if="fbDetail.attendance" style="font-size:12px;color:#323233;margin-bottom:4px"><b>出勤：</b>{{fbDetail.attendance==='on_time'?'✅ 准时':fbDetail.attendance==='late'?'⏰ 迟到':fbDetail.attendance==='leave'?'📋 请假':fbDetail.attendance==='absent'?'❌ 缺课':fbDetail.attendance}}</div>
        <div v-if="fbDetail.focus" style="font-size:12px;color:#323233;margin-bottom:4px"><b>专注度：</b>{{fbDetail.focus}}</div>
        <div v-if="fbDetail.understand" style="font-size:12px;color:#323233;margin-bottom:4px"><b>理解：</b>{{fbDetail.understand}}</div>
        <div style="font-size:13px;color:#323233;margin-top:8px;white-space:pre-wrap;line-height:1.7;background:#f7f8fa;border-radius:8px;padding:10px">{{fbDetail.resultText}}</div>
      </div>
    </van-dialog>'''

c = c.replace(old_fb_section, new_fb_section)
print("Feedback section updated")

# Add showFbDetail to return block
c = c.replace(",showHoursLog,examForm", ",showHoursLog,showFbDetail,fbDetail,examForm")

with open('index.src.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("All done!")
