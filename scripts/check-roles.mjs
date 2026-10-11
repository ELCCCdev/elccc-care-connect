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
assert.equal(run('state.view'),'welcome');assert.equal(run('state.demoRole'),null);
assert.match(root.innerHTML,/I'm a Client/);assert.match(root.innerHTML,/I'm a Counselor/);assert.match(root.innerHTML,/I'm an Administrator/);assert.match(root.innerHTML,/New Client Journey/);
for(const [role,view] of [['Client','client'],['Counselor','counselor'],['Admin','admin']]){
 event('[data-welcome-role]',{welcomeRole:role});assert.equal(run('state.view'),view);assert.equal(run('state.demoRole'),role);
 const nav=run('roleNavItems().map(x=>x[1])');assert.ok(nav.includes(view));
 if(role!=='Admin'){assert.ok(!nav.includes('admin'));assert.ok(!nav.includes('integrations'));}
 if(role==='Client'){assert.ok(!nav.includes('counselor'));assert.doesNotMatch(run('roleNavigation()'),/Admin CRM|Counselor Dashboard/);assert.doesNotMatch(run('demoTour()'),/Intake coordination|Clinical review/);}
 if(role==='Counselor')assert.doesNotMatch(run('roleNavigation()'),/Admin CRM/);
}
run("selectDemoRole('Client')");const original=run('selectedCareRecord().id');assert.equal(run('clientReference(selectedCareRecord())'),'ELCCC-10024');
assert.match(run('clientPortal()'),/ELCCC-10024/);assert.match(run('clientPortal()'),/not a login credential/);
submit();run("navigateDemoView('client')");const requestId=run('selectedCareRecord().id');const reference=run('clientReference(selectedCareRecord())');assert.equal(reference,'ELCCC-20001');
run("selectDemoRole('Admin');selectDemoRole('Client')");assert.equal(run('selectedCareRecord().id'),requestId);assert.equal(run('clientReference(selectedCareRecord())'),reference);
run("state.activeRequestId="+JSON.stringify(original));assert.notEqual(run('clientReference(selectedCareRecord())'),reference);
event('[data-visitor]',{});assert.equal(run('state.demoRole'),null);assert.equal(run('state.view'),'home');assert.equal(run('state.demoRequests.length'),1);
run("state.view='admin'");assert.match(run('currentView()'),/A compassionate place to begin/);
assert.match(run('loginModal()'),/not authentication or access protection/);assert.doesNotMatch(run('loginModal()'),/Demo credentials|password input/);
console.log('PASS: welcome role selection, role-scoped navigation/tours, direct-view fallback, visitor services, stable distinct client references, preserved session state and explicit non-authentication labels.');
