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
async function switchDemoRole(roleName){await page.getByRole('button',{name:'Switch Demo Role',exact:true}).click();const modal=page.locator('.modal-backdrop');await modal.locator(`[data-role="${roleName}"]`).click();await modal.locator('[data-login-continue]').click();}
try {
 await page.goto(url);
 assert.match(await page.locator('main').innerText(),/New Client Journey/);
 assert.equal(await role("I'm a Client").count(),1);assert.equal(await role("I'm a Counselor").count(),1);assert.equal(await role("I'm an Administrator").count(),1);
 async function assertNavigation(expected){
  const views=await page.locator('#primary-navigation [data-view]').evaluateAll(els=>els.map(el=>el.dataset.view));
  assert.ok(views.includes(expected));
  if(expected!=='admin'){assert.ok(!views.includes('admin'));assert.ok(!views.includes('integrations'));}
  if(expected==='client')assert.ok(!views.includes('counselor'));
  if(expected==='counselor')assert.ok(!views.includes('client'));
 }
 await role("I'm a Client").click();await assertNavigation('client');
 assert.match(await page.locator('.dashboard-hero').innerText(),/Taylor Hayes.*ELCCC-10024/);
 const original=await page.evaluate(()=>selectedCareRecord().id);
 await role('Start Another Demo Request').click();await role('Submit Fictional Request').click();await role('Track in Client Portal').click();
 const reference=await page.evaluate(()=>clientReference(selectedCareRecord()));assert.equal(reference,'ELCCC-20001');
 await switchDemoRole('Admin');await assertNavigation('admin');await page.locator('[data-admin-panel=appointments]').first().click();
 await role('Review & Mark Contacted').click();await page.getByLabel('Assign counselor').selectOption('rachel-kim');await role('Confirm Assignment').click();await page.getByLabel('Appointment date').fill('2099-01-01');await role('Confirm Demo Appointment').click();
 await switchDemoRole('Counselor');await assertNavigation('counselor');assert.match(await page.locator('main').innerText(),/ELCCC-20001/);
 assert.equal(await page.locator('[data-approval-mode]').count(),0);
 await switchDemoRole('Client');await assertNavigation('client');assert.match(await page.locator('.dashboard-hero').innerText(),/Jordan Demo.*ELCCC-20001/);assert.match(await page.locator('main').innerText(),/2099-01-01 at 09:00/);
 await page.getByLabel('Fictional client',{exact:false}).selectOption(original);assert.match(await page.locator('.dashboard-hero').innerText(),/Taylor Hayes.*ELCCC-10024/);assert.doesNotMatch(await page.locator('.dashboard-hero').innerText(),/Jordan Demo|ELCCC-20001/);
 for(const width of [320,375,768,1024,1440,1920]){
  await page.setViewportSize({width,height:900});
  for(const roleName of ['Client','Counselor','Admin']){
   await switchDemoRole(roleName);await assertNavigation({Client:'client',Counselor:'counselor',Admin:'admin'}[roleName]);
   assert.equal(await role('Switch Demo Role').isVisible(),true);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1),false,`${width}px ${roleName}`);
  }
  await role('← Home').click();assert.equal(await role("I'm a Client").isVisible(),true);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1),false,`${width}px welcome`);
 }
 await role('Explore Services or Request Care').click();assert.equal(await page.evaluate(()=>state.demoRole),null);assert.equal(await page.evaluate(()=>state.demoRequests.length),1);
 assert.equal(await page.locator('#primary-navigation [data-view=admin]').count(),0);assert.equal(await page.locator('#primary-navigation [data-view=client]').count(),0);
 await page.getByRole('button',{name:'Switch Demo Role',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.modal-backdrop').count(),1);await page.keyboard.press('Escape');assert.equal(await page.locator('.modal-backdrop').count(),0);
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log('PASS: welcome entry, role navigation isolation, stable client reference IDs, complete cross-role onboarding, retained session state, public visitor path, six responsive widths, keyboard role switching; no browser errors or external requests.');
}finally{await browser.close();}
