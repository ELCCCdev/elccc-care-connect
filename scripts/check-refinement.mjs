import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=readFileSync('index.html','utf8');
const root={innerHTML:''};
const document={getElementById:()=>root,querySelectorAll:()=>[],querySelector:()=>null};
const context=vm.createContext({document,window:{scrollTo(){}},console});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
const run=code=>vm.runInContext(code,context);
run("selectDemoRole('Admin')");
let nav=run('adminNavigation()');
assert.equal((nav.match(/<button/g)||[]).length,6); // Five primary areas, one Overview shortcut.
for(const label of ['Overview','Clients','Appointments','Care Journey','Reports'])assert.ok(nav.includes('>'+label+'</button>'));
assert.doesNotMatch(nav,/Approval Settings|data-admin-panel="settings"/);
run("state.activeAdminPanel='prospective'");nav=run('adminNavigation()');
for(const label of ['Prospective Clients','Established Clients','Reference Profiles'])assert.ok(nav.includes('>'+label+'</button>'));
assert.equal(run('adminGroup()'),'clients');
run("state.activeAdminPanel='established'");assert.equal(run('adminGroup()'),'clients');
run("state.activeAdminPanel='settings'");assert.doesNotMatch(run('adminPanel()'),/data-approval-mode|Center approval routing/);
assert.match(run('routingPanel()'),/data-approval-mode/); // Implementation retained.
for(const role of ['Client','Counselor','Admin']){
 run(`selectDemoRole('${role}');render()`);
 assert.match(root.innerHTML,/About this environment/);
 assert.match(root.innerHTML,/not HIPAA-ready/);
 assert.match(root.innerHTML,/MYIO are not connected/);
 assert.match(root.innerHTML,/not authentication or authorization/);
}
console.log('PASS: five primary Admin areas, grouped client sections, hidden Approval Settings with retained implementation, and shared notices across roles.');
