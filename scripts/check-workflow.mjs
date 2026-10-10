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
submit(); assert.equal(run('state.demoRequests.length'),1);
assert.match(run('adminDashboard()'),/Jordan Demo/);
event('[data-demo-contact]',{demoContact:'demo-1'}); assert.equal(run('state.demoRequests[0].status'),'Contacted');
event('[data-demo-assign]',{demoAssign:'demo-1'},{counselor:'rachel-kim'},'submit');
assert.equal(run('state.demoRequests[0].status'),'Assigned');
assert.match(run('counselorDashboard()'),/Jordan Demo/);
event('[data-demo-schedule]',{demoSchedule:'demo-1'},{date:'2000-01-01',time:'09:00'},'submit');
assert.equal(run('state.demoRequests[0].status'),'Assigned');
event('[data-demo-schedule]',{demoSchedule:'demo-1'},{date:'2099-01-01',time:'09:00'},'submit');
assert.equal(run('state.demoRequests[0].status'),'Scheduled');
for (const page of ['adminDashboard()','clientPortal()','counselorDashboard()']) assert.match(run(page),/2099-01-01 at 09:00/);
assert.match(run('kanbanBoard()'),/Jordan Demo/);
submit('Taylor Example');
event('[data-demo-contact]',{demoContact:'demo-2'});
event('[data-demo-assign]',{demoAssign:'demo-2'},{counselor:'rachel-kim'},'submit');
event('[data-demo-schedule]',{demoSchedule:'demo-2'},{date:'2099-01-01',time:'09:00'},'submit');
assert.equal(run('state.demoRequests[0].status'),'Assigned'); assert.match(run('state.notice'),/already has/);
run('state.demoCounselorId = "melissa-smith"'); assert.doesNotMatch(run('demoCounselorPanel()'),/Jordan Demo/);
for (const view of ['home','counselors','quiz','resources','client','counselor','admin']) {run(`state.view = '${view}'; render()`); assert.ok(root.innerHTML.length>1000); assert.match(root.innerHTML,/← Home/);}
for (const fn of ['counselorProfileModal(counselors[0])','clientProfileModal(clients[0])','loginModal()','presentationModal()']) assert.ok(run(fn).length>100);
assert.match(run('bookingModal(counselors[0])'),/fictional/i);
console.log('PASS: submission, review, assignment, scheduling, cross-role views, past-date and conflict rejection, counselor isolation, all existing views and modals.');
