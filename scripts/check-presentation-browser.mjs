import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:375,height:812}});
const errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));
const url=process.env.PROTOTYPE_URL || 'http://127.0.0.1:4173/?tools=1';
page.on('request',r=>{if(!r.url().startsWith(new URL(url).origin))external.push(r.url());});
const role=name=>page.getByRole('button',{name,exact:true});
async function primary(view) {const button=page.locator(`#primary-navigation [data-view="${view}"]`);if(!await button.isVisible())await role('Menu').click();await button.click();}
async function switchDemoRole(roleName){await page.getByRole('button',{name:'Switch Role',exact:true}).click();const modal=page.locator('.modal-backdrop');await modal.locator(`[data-role="${roleName}"]`).click();await modal.locator('[data-login-continue]').click();}
try {
 await page.goto(url);
 await switchDemoRole('Admin');
 assert.match(await page.locator('main').innerText(),/Center Overview/);
 await page.locator('[data-admin-panel=prayer]').first().click();
 await page.getByLabel('Requester').selectOption('Morgan Sample');
 await role('Submit Prayer Request').click();
 assert.match(await page.locator('main').innerText(),/No message was sent/);
 await page.locator('[data-prayer-action][data-action=prayed]').first().click();
 await page.locator('[data-prayer-action][data-action=followed]').first().click();
 assert.match(await page.locator('main').innerText(),/Follow-up Completed/);
 await page.getByRole('button',{name:'Clients',exact:true}).click();await page.locator('[data-admin-panel=clients]').click();
 await role('View Profile Details').click();await role('Complete Administrative Follow-up').click();
 assert.match(await page.locator('main').innerText(),/No external message was sent/);
 await page.getByLabel('Client profile').selectOption('sample-'+await page.evaluate(()=>clients[1].id));
 assert.equal(await role('Complete Administrative Follow-up').count(),1);
 await page.locator('[data-admin-panel=appointments]').first().click();
 await page.getByText('Archived Referrals',{exact:true}).first().click();await role('Create Referral').first().click();
 await role('Review & Mark Contacted').click();
 assert.match(await page.locator('main').innerText(),/Contacted/);
 for(const width of [320,375,768,1024,1440,1920]){
  await page.setViewportSize({width,height:900});
  for(const area of ['overview','intake','appointments','pipeline','prayer','clients','reports']){
   if(area==='clients')await role('Clients').click();
   if(area==='prayer')await page.locator('[data-admin-panel=overview]').click();
   await page.locator(`[data-admin-panel=${area}]`).first().click();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1),false,`${width}px admin ${area}`);
  }
 }
 await switchDemoRole('Counselor');
 await page.getByRole('link',{name:'Screening',exact:true}).click();
 assert.equal(await page.locator('#area-assessment-screening [data-diagnosis-save]').count(),0);
 await page.getByRole('link',{name:'Treatment Planning',exact:true}).click();
 assert.equal(await page.locator('#area-diagnosis-treatment-planning [data-assessment-assign]').count(),0);
 await switchDemoRole('Admin');await primary('tour');await role('Open Intake coordination').click();
 assert.equal(await page.locator('[data-admin-panel=appointments]').first().getAttribute('aria-current'),'page');
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log('PASS: presentation overview, prayer and profile actions, historical referral workflow, grouped Admin areas at six viewport widths, separate clinical navigation, guided tour routing; no browser errors or external requests.');
}finally{await browser.close();}
