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
try {
 await page.goto(url);
 await role('1 · Client Portal').click();await role('Start Another Demo Request').click();await role('Submit Fictional Request').click();await role('Review in Admin CRM').click();await role('Review & Mark Contacted').click();await page.getByLabel('Assign counselor').selectOption('rachel-kim');await role('Confirm Assignment').click();await page.getByLabel('Appointment date',{exact:false}).fill('2099-01-01');await role('Confirm Demo Appointment').click();
 await page.getByLabel('Center approval routing').selectOption('counselor');
 await role('1 · Client Portal').click();await page.getByLabel('Requested date').fill('2099-01-02');await page.getByLabel('Requested time (Eastern Time)').selectOption('11:00');await role('Request Demo Reschedule').click();
 await role('2 · Admin CRM').click();assert.equal(await role('Approve Demo Reschedule').count(),0);
 await role('3 · Counselor Dashboard').click();await page.getByLabel('Alternative date').fill('2099-01-03');await page.getByLabel('Alternative time (Eastern Time)').selectOption('14:00');await role('Propose Alternative Time').click();
 await role('1 · Client Portal').click();assert.match(await page.locator('main').innerText(),/Appointment: 2099-01-01 at 09:00/);await role('Accept Proposed Alternative').click();
 await role('3 · Counselor Dashboard').click();await role('Approve Demo Reschedule').click();
 await page.getByLabel('Daily agenda date').fill('2099-01-03');await page.getByLabel('Daily agenda date').press('Tab');await role('Open Appointment Details').click();
 await role('Assign Fictional Assessment').click();await role('1 · Client Portal').click();
 const assessment=page.locator('[data-assessment-submit]');await assessment.locator('[name=q0]').selectOption('2');await assessment.locator('[name=q1]').selectOption('1');await assessment.locator('[name=q2]').selectOption('2');await role('Complete Fictional Assessment').click();
 assert.match(await page.locator('main').innerText(),/Sample score: 5\/6/);assert.match(await page.locator('main').innerText(),/No diagnosis documentation/);
 await role('3 · Counselor Dashboard').click();await page.getByLabel('Simulated workspace permission').selectOption('coordinator');assert.equal(await page.locator('[data-diagnosis-save]').count(),0);
 await page.getByLabel('Simulated workspace permission').selectOption('clinician');await role('Review Sample Screening').click();assert.match(await page.locator('main').innerText(),/No diagnosis documentation/);
 const diagnosis=page.locator('[data-diagnosis-save]');await diagnosis.locator('[name=rationale]').fill('Invented stakeholder demonstration interview rationale.');await diagnosis.locator('[name=goal]').fill('Practice a fictional supportive routine.');await diagnosis.locator('[name=followup]').fill('Review the fictional goal at the next demo appointment.');await diagnosis.locator('[name=ack]').selectOption('manual');await role('Save Fictional Diagnosis & Plan').click();
 assert.match(await page.locator('main').innerText(),/Provisional · Illustrative ICD-10-CM/);
 await page.locator('[data-diagnosis-save] [name=status]').selectOption('Confirmed');await page.locator('[data-diagnosis-save] [name=ack]').selectOption('manual');await role('Save Fictional Diagnosis & Plan').click();await role('Assign Goal-related Demo Homework').click();
 await role('1 · Client Portal').click();await page.getByLabel('Demo response (fictional text only)').fill('Fictional example: I tried the mock routine.');await role('Submit Sample Homework').click();
 await role('3 · Counselor Dashboard').click();await page.getByLabel('Fictional feedback',{exact:false}).fill('Fictional encouragement: review this mock goal next time.');await role('Save Fictional Feedback').click();
 await role('2 · Admin CRM').click();await page.getByLabel('Center approval routing').selectOption('configured');await page.locator('[data-client-routing] [name=client]').selectOption('demo-1');await page.getByLabel('Assigned approver',{exact:false}).selectOption('admin');await role('Save Demo Routing').click();
 await role('1 · Client Portal').click();await role('Request Demo Cancellation').click();await role('3 · Counselor Dashboard').click();assert.equal(await role('Approve Demo Cancellation').count(),0);await role('2 · Admin CRM').click();await role('Decline Demo Cancellation').click();
 await role('1 · Client Portal').click();assert.match(await page.locator('main').innerText(),/Appointment: 2099-01-03 at 14:00/);assert.match(await page.locator('main').innerText(),/Fictional encouragement/);await page.locator('details summary').first().click();assert.match(await page.locator('main').innerText(),/Original: 2099-01-01 at 09:00/);assert.doesNotMatch(await page.locator('main').innerText(),/\bdemo-\d|sample-client-\d/);
 await primary('integrations');
 for(const name of ['EHR / Practice Management','Telehealth','Calendar & Scheduling','Billing & Insurance','Messaging & Reminders']) {
  const card=page.locator('article').filter({has:page.getByRole('heading',{name,exact:true})});await card.getByRole('button',{name:'Enable Demo Simulation',exact:true}).click();await card.getByRole('button',{name:'Preview Simulated Sync',exact:true}).click();assert.match(await card.innerText(),/Zero records sent/);assert.match(await card.innerText(),/not connected/);
 }
 await primary('tour');assert.match(await page.locator('main').innerText(),/Stakeholder Demo Tour/);
 for(const width of [320,375,768,1024,1280,1920]) {
  await page.setViewportSize({width,height:900});
  for(const view of ['client','counselor','admin','integrations','tour']) {await page.evaluate(view=>{state.view=view;render();},view);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1),false,`${width}px ${view}`);}
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log('PASS: mobile counselor routing, alternative acceptance/finalization, agenda, assessment scoring/review, clinician-only documentation, treatment homework/feedback, configured cancellation routing, history, friendly labels, five integration simulations, tour, responsive populated views; no external requests.');
} finally {await browser.close();}
