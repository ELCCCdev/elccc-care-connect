import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html = readFileSync('index.html', 'utf8');
const root = {innerHTML:''};
let elements = {};
const document = {getElementById:()=>root, querySelectorAll:s=>elements[s] || [], querySelector:()=>null};
class DemoFormData { constructor(form) {this.fields=form.fields;} get(key) {return this.fields[key];} }
const context = vm.createContext({document, window:{scrollTo(){}}, FormData:DemoFormData, console});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
const run = code=>vm.runInContext(code,context);
function event(selector, dataset, fields, type='click') {
 let callback;
 const el={dataset,fields,addEventListener:(name,fn)=>{if(name===type) callback=fn;}};
 elements={[selector]:[el]}; run('bindEvents()'); elements={}; assert.ok(callback,selector); callback({preventDefault(){}});
}
function submit(name='Jordan Demo') {
 run('state.bookingCounselor = counselors.find(c => c.id === "rachel-kim"); state.bookingSubmitted = false');
 event('[data-booking-form]',{}, {name,concern:'Anxiety',format:'Telehealth'},'submit');
}
run("state.view='admin';state.activeAdminPanel='overview'");
assert.match(run('adminDashboard()'),/Session Referrals/);
assert.doesNotMatch(run('adminDashboard()'),/\+18%|Executive CRM/);
event('[data-prayer-submit]',{}, {name:'Jordan Demo',category:'Family',followup:'yes'},'submit');
assert.equal(run('prayerQueue()[0].session'),true);
assert.match(run('prayerManagement()'),/Created this session/);
event('[data-prayer-action]',{prayerAction:'0',action:'prayed'});
event('[data-prayer-action]',{prayerAction:'0',action:'followed'});
assert.equal(run('prayerQueue()[0].prayed && prayerQueue()[0].followed'),true);
run("state.view='client'");event('[data-prayer-action]',{prayerAction:'1',action:'followed'});
assert.equal(run('prayerQueue()[1].followed'),false);
run("state.view='admin'");event('[data-admin-followup]',{adminFollowup:run('careRecords()[0].id')});
assert.equal(run('careRecords()[0].adminFollowed'),true);
assert.notEqual(run('careRecords()[1].adminFollowed'),true);
event('[data-profile-details]',{profileDetails:run('careRecords()[0].id')});assert.match(run('clientDirectory()'),/Open Counselor Workspace/);
event('[data-demo-review]',{demoReview:String(run('appointmentRequests[0].id'))});
assert.equal(run('state.demoRequests.length'),1);assert.equal(run('state.demoRequests[0].status'),'New');
assert.match(run('state.demoRequests[0].source'),/Session copy/);
assert.match(run('kanbanBoard()'),/Session-created referrals only/);
assert.doesNotMatch(run('assessmentPanel(selectedCareRecord(),true)'),/data-diagnosis-save|Clinician-authored documentation/);
assert.doesNotMatch(run('treatmentPanel(selectedCareRecord(),true)'),/data-assessment-assign/);
assert.match(run('integrationCenter()'),/Client care records|Technical information/);
assert.match(run('demoTour()'),/data-tour-admin/);
console.log('PASS: overview metrics, fictional prayer submission and administrative permissions, isolated profile follow-up, historical referral copying, separate screening/planning, plain-English integrations, tour routing.');
