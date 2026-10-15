import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:375,height:812}});
const errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));
const url=process.env.PROTOTYPE_URL || 'http://127.0.0.1:4173/';
page.on('request',r=>{if(!r.url().startsWith(new URL(url).origin))external.push(r.url());});
const role=name=>page.getByRole('button',{name,exact:true});
async function primary(view) {const button=page.locator(`#primary-navigation [data-view="${view}"]`);if(!await button.isVisible())await role('Menu').click();await button.click();}
async function switchDemoRole(roleName){await page.getByRole('button',{name:'Switch Role',exact:true}).click();const modal=page.locator('.modal-backdrop');await modal.locator(`[data-role="${roleName}"]`).click();await modal.locator('[data-login-continue]').click();}
try {
 await page.goto(url);
 await switchDemoRole('Client');await role('Start Another Request').click();await role('Submit Request').click();await role('Open Admin CRM').click();await role('Review & Mark Contacted').click();await page.getByLabel('Assign counselor').selectOption('rachel-kim');await role('Confirm Assignment').click();await page.getByLabel('Appointment date',{exact:false}).fill('2099-01-01');await role('Confirm Appointment').click();
 // Administrative appointment directory controls exercise the existing scheduled record.
 await page.getByLabel('Search appointments',{exact:true}).fill('Jordan');
 await page.getByLabel('Appointment counselor',{exact:true}).selectOption('rachel-kim');
 await page.getByLabel('Filter by date',{exact:true}).fill('2099-01-01');
 await page.getByLabel('Filter by date',{exact:true}).press('Tab');
 assert.equal(await page.locator('[data-appointment-row]').count(),1);
 await page.getByRole('button',{name:'Name',exact:true}).click();assert.equal(await page.getByLabel('Sort appointments',{exact:true}).inputValue(),'name');
 await page.getByRole('button',{name:'Name',exact:true}).click();assert.equal(await page.getByLabel('Sort appointments',{exact:true}).inputValue(),'namedesc');
 await page.getByRole('button',{name:'Date',exact:true}).click();assert.equal(await page.getByLabel('Sort appointments',{exact:true}).inputValue(),'soonest');
 await page.getByRole('button',{name:'Date',exact:true}).click();assert.equal(await page.getByLabel('Sort appointments',{exact:true}).inputValue(),'latest');
 assert.equal(await page.getByLabel('Search appointments',{exact:true}).inputValue(),'Jordan');
 assert.equal(await page.getByLabel('Appointment counselor',{exact:true}).inputValue(),'rachel-kim');

 await page.getByLabel('Appointment status',{exact:true}).selectOption('Cancelled');
 assert.equal(await page.locator('[data-appointment-row]').count(),0);
 await page.getByLabel('Appointment status',{exact:true}).selectOption('Confirmed');
 await role('Calendar preview').click();await page.getByLabel('Calendar month',{exact:true}).fill('2099-01');await page.getByLabel('Calendar month',{exact:true}).press('Tab');
 await page.getByRole('button',{name:'2099-01-01, 1 appointments',exact:true}).click();
 assert.equal(await page.locator('[data-appointment-row]').count(),1);
 await role('Review appointment').click();await page.getByRole('heading',{name:'Jordan Demo appointment',exact:true}).waitFor();await role('Close appointment review').click();
 await role('Clear filters').click();
 // Approval Settings is hidden; seed the retained routing logic for this regression.
 await page.evaluate(()=>{state.approvalMode='counselor';});
 await switchDemoRole('Client');await page.getByLabel('Requested date').fill('2099-01-02');await page.getByLabel('Requested time (Eastern Time)').selectOption('11:00');await role('Request Reschedule').click();
 await switchDemoRole('Admin');assert.equal(await role('Approve Reschedule').count(),0);
 await switchDemoRole('Counselor');await page.getByLabel('Alternative date').fill('2099-01-03');await page.getByLabel('Alternative time (Eastern Time)').selectOption('14:00');await role('Propose Alternative Time').click();
 await switchDemoRole('Client');assert.match(await page.locator('main').innerText(),/Appointment: 2099-01-01 at 09:00/);await role('Accept Proposed Alternative').click();
 await switchDemoRole('Counselor');await role('Approve Reschedule').click();
 await page.getByLabel('Daily agenda date').fill('2099-01-03');await page.getByLabel('Daily agenda date').press('Tab');await role('Open Appointment Details').click();
 await role('Assign Screening').click();await switchDemoRole('Client');
 const assessment=page.locator('[data-assessment-submit]');await assessment.locator('[name=q0]').selectOption('2');await assessment.locator('[name=q1]').selectOption('1');await assessment.locator('[name=q2]').selectOption('2');await role('Complete Screening').click();
 assert.match(await page.locator('main').innerText(),/Screening score: 5\/6/);assert.match(await page.locator('main').innerText(),/No diagnosis documentation/);
 await switchDemoRole('Counselor');await page.getByLabel('Workspace mode (test only)').selectOption('coordinator');assert.equal(await page.locator('[data-diagnosis-save]').count(),0);
 await page.getByLabel('Workspace mode (test only)').selectOption('clinician');await role('Review Screening').click();assert.match(await page.locator('main').innerText(),/No diagnosis documentation/);
 const diagnosis=page.locator('[data-diagnosis-save]');await diagnosis.locator('[name=rationale]').fill('Invented stakeholder demonstration interview rationale.');await diagnosis.locator('[name=goal]').fill('Practice a fictional supportive routine.');await diagnosis.locator('[name=followup]').fill('Review the fictional goal at the next session appointment.');await diagnosis.locator('[name=ack]').selectOption('manual');await role('Save Diagnosis & Plan').click();
 assert.match(await page.locator('main').innerText(),/Provisional · Illustrative ICD-10-CM/);
 await page.locator('[data-diagnosis-save] [name=status]').selectOption('Confirmed');await page.locator('[data-diagnosis-save] [name=ack]').selectOption('manual');await role('Save Diagnosis & Plan').click();await role('Assign Goal-related Homework').click();
 await switchDemoRole('Client');await page.getByLabel('Response (test records only)').fill('Fictional example: I tried the mock routine.');await role('Submit Homework').click();
 await switchDemoRole('Counselor');await page.getByLabel('Feedback (test records only)',{exact:false}).fill('Fictional encouragement: review this mock goal next time.');await role('Save Feedback').click();
 await switchDemoRole('Admin');await page.evaluate(()=>{state.approvalMode='configured';ensureOperations(careRecords().find(r=>r.id==='demo-1')).routing='admin';});
 await switchDemoRole('Client');await role('Request Cancellation').click();await switchDemoRole('Counselor');assert.equal(await role('Approve Cancellation').count(),0);await switchDemoRole('Admin');await page.locator('[data-admin-panel=appointments]').first().click();await role('Decline Cancellation').click();
 await switchDemoRole('Client');assert.match(await page.locator('main').innerText(),/Appointment: 2099-01-03 at 14:00/);assert.match(await page.locator('main').innerText(),/Fictional encouragement/);await page.getByText('Appointment & request history',{exact:false}).click();assert.match(await page.locator('main').innerText(),/Original: 2099-01-01 at 09:00/);assert.doesNotMatch(await page.locator('main').innerText(),/\bdemo-\d|sample-client-\d/);
 await switchDemoRole('Admin');await primary('integrations');
 for(const name of ['Client care records','Video appointments','Appointment calendar','Payments & insurance','Appointment reminders']) {
  const card=page.locator('article').filter({has:page.getByRole('heading',{name,exact:true})});await card.getByRole('button',{name:'Enable Preview',exact:true}).click();await card.getByRole('button',{name:'Preview Data Flow',exact:true}).click();assert.match(await card.innerText(),/Zero records sent/);assert.match(await card.innerText(),/not connected/i);
 }
 await primary('tour');assert.match(await page.locator('main').innerText(),/Workflow Guide/);
 for(const width of [320,375,768,1024,1280,1920]) {
  await page.setViewportSize({width,height:900});
  for(const view of ['client','counselor','admin','integrations','tour']) {await page.evaluate(view=>{state.demoRole={client:'Client',counselor:'Counselor',admin:'Admin',integrations:'Admin'}[view]||null;state.view=view;render();},view);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1),false,`${width}px ${view}`);}
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log('PASS: mobile counselor routing, alternative acceptance/finalization, agenda, assessment scoring/review, clinician-only documentation, treatment homework/feedback, configured cancellation routing, history, friendly labels, five integration simulations, tour, responsive populated views; no external requests.');
} finally {await browser.close();}
