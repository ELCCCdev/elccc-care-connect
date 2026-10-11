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
 const el={dataset,fields,value:fields?.value,addEventListener:(name,fn)=>{if(name===type) callback=fn;}};
 elements={[selector]:[el]}; run('bindEvents()'); elements={}; assert.ok(callback,selector); callback({preventDefault(){}});
}
function submit(name='Jordan Demo') {
 run('state.bookingCounselor = counselors.find(c => c.id === "rachel-kim"); state.bookingSubmitted = false');
 event('[data-booking-form]',{}, {name,concern:'Anxiety',format:'Telehealth'},'submit');
}

submit();event('[data-demo-contact]',{demoContact:'demo-1'});event('[data-demo-assign]',{demoAssign:'demo-1'},{counselor:'rachel-kim'},'submit');event('[data-demo-schedule]',{demoSchedule:'demo-1'},{date:'2099-01-01',time:'09:00'},'submit');
run('state.view="admin"');event('[data-approval-mode]',{},{value:'counselor'},'change');
run('state.view="client"');event('[data-reschedule-request]',{rescheduleRequest:'demo-1'},{date:'2099-01-02',time:'11:00',reason:''},'submit');
assert.equal(run('careDetails(selectedCareRecord()).reschedule.approver'),'counselor');
assert.equal(run('careDetails(selectedCareRecord()).reschedule.original.date'),'2099-01-01');
run('state.view="admin"');event('[data-approval-mode]',{},{value:'admin'},'change');event('[data-reschedule-approve]',{rescheduleApprove:'demo-1'});
assert.equal(run('selectedCareRecord().appointment.date'),'2099-01-01');
run('state.view="counselor";state.workspaceClientId="demo-1";state.demoCounselorId="melissa-smith"');event('[data-reschedule-approve]',{rescheduleApprove:'demo-1'});
assert.equal(run('selectedCareRecord().appointment.date'),'2099-01-01');
run('state.demoCounselorId="rachel-kim"');event('[data-propose-slot]',{proposeSlot:'demo-1'},{date:'2099-01-03',time:'14:00'},'submit');
assert.equal(run('careDetails(selectedCareRecord()).reschedule.status'),'Alternative proposed');
run('state.view="client"');event('[data-alternative-accept]',{alternativeAccept:'demo-1'});
assert.equal(run('selectedCareRecord().appointment.date'),'2099-01-01');
run('state.view="counselor"');event('[data-reschedule-approve]',{rescheduleApprove:'demo-1'});
assert.equal(run('selectedCareRecord().appointment.date'),'2099-01-03');
assert.equal(run('careDetails(selectedCareRecord()).changeHistory[0].original.date'),'2099-01-01');
assert.equal(run('careDetails(selectedCareRecord()).changeHistory[0].requested.date'),'2099-01-02');
assert.ok(run('careDetails(selectedCareRecord()).reschedule.events.length')>=4);
run('state.demoRequests[0].appointment={date:"2099-01-09",time:"09:00"}');
assert.match(run('schedulingError({id:"overlap-test",counselorId:"rachel-kim"},"2099-01-09","09:30")'),/overlapping/);
run('state.demoRequests[0].appointment={date:"2099-01-03",time:"14:00"}');
// Overlap rejects a different start time within the existing 60-minute session.
submit('Taylor Example');event('[data-demo-contact]',{demoContact:'demo-2'});event('[data-demo-assign]',{demoAssign:'demo-2'},{counselor:'rachel-kim'},'submit');
assert.match(run('schedulingError(state.demoRequests[0],"2099-01-03","14:00")'),/overlapping/);
run('state.availability["rachel-kim"]={start:780,end:1020,blocked:false}');assert.match(run('schedulingError(state.demoRequests[0],"2099-01-04","09:00")'),/availability/);
run('state.availability["rachel-kim"]={start:540,end:1020,blocked:false};state.activeRequestId="demo-1";state.workspaceClientId="demo-1";state.view="counselor"');
event('[data-assessment-assign]',{assessmentAssign:'demo-1'},{assessment:'0'},'submit');
run('state.view="client"');event('[data-assessment-submit]',{assessmentSubmit:'assessment-1',careClient:'demo-1'},{q0:'2',q1:'1',q2:'2'},'submit');
assert.equal(run('careDetails(selectedCareRecord()).assessments[0].score'),5);
assert.equal(run('careDetails(selectedCareRecord()).diagnosis'),undefined);
const documentation={code:'Z63.0',status:'Confirmed',rationale:'Fictional interview rationale',goal:'Fictional practice goal',followup:'Demo follow-up',ack:'manual'};
event('[data-diagnosis-save]',{diagnosisSave:'demo-1'},documentation,'submit');assert.equal(run('careDetails(selectedCareRecord()).diagnosis'),undefined);
run('state.view="admin"');event('[data-diagnosis-save]',{diagnosisSave:'demo-1'},documentation,'submit');assert.equal(run('careDetails(selectedCareRecord()).diagnosis'),undefined);
run('state.view="counselor";state.clinicianMode="coordinator"');event('[data-diagnosis-save]',{diagnosisSave:'demo-1'},documentation,'submit');assert.equal(run('careDetails(selectedCareRecord()).diagnosis'),undefined);
run('state.clinicianMode="clinician"');event('[data-assessment-review]',{assessmentReview:'assessment-1',careClient:'demo-1'});assert.equal(run('careDetails(selectedCareRecord()).diagnosis'),undefined);
event('[data-diagnosis-save]',{diagnosisSave:'demo-1'},{...documentation,status:'Provisional'},'submit');assert.equal(run('careDetails(selectedCareRecord()).diagnosis.status'),'Provisional');
event('[data-diagnosis-save]',{diagnosisSave:'demo-1'},documentation,'submit');assert.equal(run('careDetails(selectedCareRecord()).diagnosis.status'),'Confirmed');
event('[data-plan-homework]',{planHomework:'demo-1'});assert.equal(run('careDetails(selectedCareRecord()).homework.length'),1);
run('state.view="client"');event('[data-homework-submit]',{homeworkSubmit:'homework-1',careClient:'demo-1'});
run('state.view="counselor"');event('[data-homework-feedback]',{homeworkFeedback:'homework-1',careClient:'demo-1'},{feedback:'Fictional encouragement only'},'submit');assert.equal(run('careDetails(selectedCareRecord()).homework[0].feedback'),'Fictional encouragement only');
run('state.activeRequestId="demo-2";state.view="client"');assert.doesNotMatch(run('clinicalPanel(selectedCareRecord())'),/Fictional interview rationale/);
assert.doesNotMatch(run('clientPortal()').replace(/<select[\s\S]*?<\/select>/g,''),/demo-2<|demo-1<|Fictional encouragement/);
run('state.view="client";state.activeRequestId="demo-1";state.approvalMode="counselor"');event('[data-cancellation-request]',{cancellationRequest:'demo-1'},{reason:''},'submit');
run('state.view="admin"');event('[data-cancellation-approve]',{cancellationApprove:'demo-1'});assert.ok(run('selectedCareRecord().appointment'));
run('state.view="counselor";state.demoCounselorId="melissa-smith"');event('[data-cancellation-decline]',{cancellationDecline:'demo-1'});assert.equal(run('careDetails(selectedCareRecord()).cancellation.status'),'Pending');
run('state.demoCounselorId="rachel-kim"');event('[data-cancellation-approve]',{cancellationApprove:'demo-1'});assert.equal(run('selectedCareRecord().appointment'),null);
run('careRecords(); state.sampleCare["sample-client-03"].appointment={date:"2099-01-10",time:"10:00"}');assert.match(run('clientProfileModal(clients[2])'),/2099-01-10 at 10:00/);
run('state.view="integrations"');event('[data-integration-preview]',{integrationPreview:'ehr'});assert.match(run('integrationCenter()'),/Zero records sent/);
assert.match(run('demoTour()'),/Screening|Clinical review/);
console.log('PASS: approver snapshots, unauthorized role restrictions, alternatives, history, availability, conflicts, clinician restrictions, screening/diagnosis separation, treatment homework, feedback, identity and integration previews.');
