import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
let chromium;
try { ({chromium} = require('playwright')); }
catch { throw new Error('Install Playwright in your test environment to run browser checks. It is not an application dependency.'); }
const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless:true, args:['--no-sandbox']});
const page = await browser.newPage();
const errors=[];
page.on('pageerror', e=>errors.push(e.message));
const url=process.env.PROTOTYPE_URL || 'http://127.0.0.1:4173/';
async function noOverflow(label) {
 const problems = await page.evaluate(()=>{
  const width=document.documentElement.clientWidth;
  return {document:document.documentElement.scrollWidth > width+1, elements:[...document.querySelectorAll('main *, header *, .modal-backdrop *')].filter(el=>{
   const r=el.getBoundingClientRect(); const style=getComputedStyle(el);
   return r.width && style.position!=='absolute' && (r.right > width+1 || r.left < -1);
  }).slice(0,8).map(el=>`${el.tagName}.${el.className}`)};
 });
 assert.equal(problems.document,false,`${label}: document overflow ${JSON.stringify(problems)}`);
 assert.deepEqual(problems.elements,[],`${label}: elements outside viewport`);
}
try {
 await page.goto(url);
 for(const width of [320,375,390,480,640,768,1024,1280,1440,1920]) {
  await page.setViewportSize({width,height:900});
  for(const view of ['home','counselors','quiz','resources','client','counselor','admin']) {
   await page.evaluate(view=>{state.view=view; state.menuOpen=false;render();},view);
   await noOverflow(`${width}px ${view}`);
  }
  await page.evaluate(()=>{state.menuOpen=true;render();});
  await noOverflow(`${width}px expanded navigation`);
  for(const modal of ['login','booking','profile','client','presentation']) {
   await page.evaluate(modal=>{state.menuOpen=false;state.showLogin=modal==='login';state.bookingCounselor=modal==='booking'?counselors[0]:null;state.selectedCounselor=modal==='profile'?counselors[0]:null;state.selectedClient=modal==='client'?clients[0]:null;state.showPresentation=modal==='presentation';render();},modal);
   await noOverflow(`${width}px ${modal} dialog`);
   assert.ok(await page.locator('.modal-backdrop').getAttribute('aria-labelledby'));
   await page.keyboard.press('Escape');
   assert.equal(await page.locator('.modal-backdrop').count(),0);
  }
 }
 // Exercise the complete connected workflow through browser controls at mobile width.
 await page.setViewportSize({width:375,height:812});
 await page.getByRole('button',{name:'1 · Client Portal',exact:true}).click();
 await page.getByRole('button',{name:'Start Another Demo Request'}).click();
 await page.getByRole('button',{name:'Submit Fictional Request'}).click();
 await page.getByRole('button',{name:'Review in Admin CRM'}).click();
 await page.getByRole('button',{name:'Review & Mark Contacted'}).click();
 await page.getByLabel('Assign counselor').selectOption('rachel-kim');
 await page.getByRole('button',{name:'Confirm Assignment',exact:true}).click();
 await page.getByLabel('Appointment date').fill('2099-01-01');
 await page.getByRole('button',{name:'Confirm Demo Appointment'}).click();
 await noOverflow('mobile scheduled admin');
 await page.getByRole('button',{name:'3 · Counselor Dashboard',exact:true}).click();
 await page.getByLabel('Demo counselor').selectOption('rachel-kim');
 assert.match(await page.locator('main').innerText(),/2099-01-01 at 09:00/);
 await page.getByRole('button',{name:'1 · Client Portal',exact:true}).click();
 assert.match(await page.locator('main').innerText(),/Status: Scheduled/);
 assert.match(await page.locator('main').innerText(),/2099-01-01 at 09:00/);
 await noOverflow('mobile updated client');
 await page.getByRole('button',{name:'← Home',exact:true}).click();
 await page.getByRole('button',{name:'Menu',exact:true}).click();
 assert.equal(await page.getByRole('button',{name:'Menu',exact:true}).getAttribute('aria-expanded'),'true');
 await page.keyboard.press('Escape');
 assert.equal(await page.getByRole('button',{name:'Menu',exact:true}).getAttribute('aria-expanded'),'false');
 await page.getByRole('button',{name:'Menu',exact:true}).click();
 await page.getByRole('button',{name:'Switch Demo Role',exact:true}).click();
 const first=page.locator('.modal-backdrop button').first();
 await first.focus(); await page.keyboard.press('Shift+Tab');
 assert.equal(await page.evaluate(()=>document.activeElement.hasAttribute('data-login-continue')),true);
 await page.keyboard.press('Tab'); assert.equal(await first.evaluate(el=>el===document.activeElement),true);
 await page.keyboard.press('Escape');
 if (process.env.QA_SCREENSHOTS) {
  for (const width of [375,1280]) {
   await page.setViewportSize({width,height:900});
   await page.evaluate(()=>{state.view='admin';render();});
   await page.evaluate(()=>{window.scrollTo(0,0);});
   await page.screenshot({path:`work/admin-${width}.png`});
  }
 }
 assert.deepEqual(errors,[]);
 console.log('PASS: 10 viewport widths × 7 pages, expanded navigation, 5 dialog types, mobile onboarding through all roles, menu Escape, dialog focus trapping; no horizontal overflow or JavaScript errors.');
} finally {await browser.close();}
