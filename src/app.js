import {
  appointmentRequests,
  clients,
  counselors,
  leadSources,
  monthlyAppointments,
  prayerRequests,
  resources,
  specialtyDemand
} from "./mockData.js";

const state = {
  view: "home",
  selectedCounselor: null,
  selectedClient: null,
  quiz: { person: "Adult", concern: "Anxiety", faith: "Optional", location: "Any" },
  counselorFilter: "All",
  resourceSearch: "",
  resourceCategory: "All",
  activeAdminPanel: "pipeline"
};

const root = document.getElementById("root");
const nav = [
  ["Home", "home"],
  ["Find a Counselor", "counselors"],
  ["Match Quiz", "quiz"],
  ["Resources", "resources"],
  ["Client Portal", "client"],
  ["Counselor", "counselor"],
  ["Admin CRM", "admin"]
];

const pipelineStages = ["New", "Contacted", "Assigned", "Scheduled"];
const clientStatuses = ["Lead", "Intake Pending", "Active", "Follow-up", "Discharged"];

function render() {
  root.innerHTML = `
    <div class="app-shell">
      ${disclaimerBanner()}
      <header class="site-header">
        <button class="brand" data-view="home" aria-label="ELCCC Care Connect home">
          <span class="brand-mark">☁</span><span><strong>ELCCC</strong><small>Care Connect</small></span>
        </button>
        <nav class="nav-pills" aria-label="Primary navigation">
          ${nav.map(([label, view]) => `<button data-view="${view}" class="${state.view === view ? "active" : ""}">${label}</button>`).join("")}
        </nav>
      </header>
      <main>${currentView()}</main>
      ${state.selectedCounselor ? counselorProfileModal(state.selectedCounselor) : ""}
      ${state.selectedClient ? clientProfileModal(state.selectedClient) : ""}
    </div>`;
  bindEvents();
}

function disclaimerBanner() {
  return `<div class="demo-banner"><strong>Prototype only</strong> — no real client or medical data.</div>`;
}

function currentView() {
  if (state.view === "counselors") return counselorDirectory();
  if (state.view === "quiz") return quizPage();
  if (state.view === "resources") return resourcesPage();
  if (state.view === "client") return clientPortal();
  if (state.view === "counselor") return counselorDashboard();
  if (state.view === "admin") return adminDashboard();
  return homePage();
}

function homePage() {
  const activeClients = clients.filter((client) => client.status === "Active").length;
  return `
    <section class="hero cloud-panel">
      <div class="hero-copy">
        <p class="eyebrow">Eagle's Landing Christian Counseling Center</p>
        <h1>Professional counseling care rooted in God&apos;s amazing grace.</h1>
        <p>A modern care connection experience for clients, counselors, and ministry leaders—designed to guide every person to the right next step with warmth, clarity, and hope.</p>
        <div class="cta-row"><button class="lime-button" data-view="quiz">Take the Match Quiz</button><button class="ghost-button" data-view="admin">View Executive Dashboard</button></div>
      </div>
      <div class="hero-card glass-card"><span class="live-dot"></span> Live care snapshot<h3>${appointmentRequests.filter((request) => request.status === "New").length} new appointment requests</h3><p>${activeClients} active clients receiving care this month.</p><div class="mini-stack"><span>Trauma recovery</span><span>Play therapy</span><span>Marriage care</span><span>Prayer support</span></div></div>
    </section>
    <section class="section grid-3">${feature("Find the right counselor", "Search by specialty, age group, insurance, location, faith preference, and availability.")}${feature("Manage the care journey", "Kanban pipeline, appointment request management, prayer queues, and client status tracking.")}${feature("Executive-ready dashboards", "Mock analytics, beautiful charts, utilization views, and presentation-quality SaaS layouts.")}</section>
    <section class="section presentation-section"><div><p class="eyebrow dark">Executive-ready ministry intelligence</p><h2>Beautiful dashboards for compassionate operational clarity.</h2><p>ELCCC Care Connect combines clinical intake workflows, prayer ministry touchpoints, and CRM visibility in a polished SaaS interface built for leadership presentations and day-to-day coordination.</p></div><div class="analytics-preview">${metric("New Leads", "7", "Today")}${metric("Utilization", "80%", "12 counselors")}${barChart(monthlyAppointments.slice(1))}</div></section>
    <section class="section"><div class="section-heading"><p class="eyebrow dark">Meet Our Care Team</p><h2>Specialized counselors, one shared mission.</h2></div><div class="team-strip">${counselors.slice(0, 6).map(teamCard).join("")}</div></section>
    <section class="section prayer-home cloud-panel compact-cloud"><div><p class="eyebrow">How Can We Pray For You?</p><h2>Share a confidential prayer request with the ELCCC care team.</h2><p>Offer a name or remain anonymous. If you request follow-up, the team can route your request with compassion and care.</p></div>${prayerForm()}</section>`;
}

function counselorDirectory() {
  const filters = ["All", "Trauma", "Children", "Anxiety", "Marriage", "Substance Abuse", "Play Therapy"];
  const filtered = state.counselorFilter === "All" ? counselors : counselors.filter((counselor) => counselor.specialties.includes(state.counselorFilter));
  return `<section class="page-wrap">${pageHero("Find a Counselor", "Choose care that fits your story.", "Each profile includes a professional headshot, credentials, bio, specialties, insurance, faith integration approach, and availability.")}<div class="filter-row">${filters.map((filter) => `<button data-counselor-filter="${filter}" class="${state.counselorFilter === filter ? "active" : ""}">${filter}</button>`).join("")}</div><div class="counselor-grid">${filtered.map(counselorCard).join("")}</div></section>`;
}

function quizPage() {
  const recommendation = recommendCounselor(state.quiz);
  return `<section class="page-wrap quiz-layout"><div>${pageHero("Counselor Match Quiz", "A guided path to a recommended counselor.", "Answer a few simple routing questions. This quiz does not diagnose; it simply suggests a care team member based on fit.")}${quizField("Who needs care?", "person", ["Adult", "Teen", "Child", "Couple", "Family"])}${quizField("Primary concern", "concern", ["Anxiety", "Trauma", "Children", "Marriage", "Substance Abuse", "Grief", "Depression"])}${quizField("Faith integration preference", "faith", ["High", "Optional", "Client-led"])}${quizField("Preferred location", "location", ["Any", "McDonough", "Forsyth", "Telehealth"])}</div><aside class="recommendation-card glass-card"><p class="eyebrow">Recommended Counselor</p><img src="${recommendation.headshot}" alt="${recommendation.name} professional headshot" /><h2>${recommendation.name}</h2><p>${recommendation.credentials}</p><div class="score-ring">94% fit</div><p>${recommendation.specialties.slice(0, 3).join(" · ")}</p><button class="lime-button full" data-counselor="${recommendation.id}">Open Recommended Profile</button></aside></section>`;
}

function resourcesPage() {
  const categories = ["All", ...new Set(resources.map((resource) => resource.category))];
  const query = state.resourceSearch.toLowerCase();
  const filtered = resources.filter((resource) => {
    const matchesCategory = state.resourceCategory === "All" || resource.category === state.resourceCategory;
    const matchesSearch = !query || `${resource.title} ${resource.category} ${resource.audience}`.toLowerCase().includes(query);
    return matchesCategory && matchesSearch;
  });
  return `<section class="page-wrap">${pageHero("Resources Library", "Searchable resources for every care pathway.", "Use mock articles, worksheets, and care guides for anxiety, trauma recovery, parenting, marriage, grief, addiction recovery, and faith wellness.")}<div class="resource-tools"><input data-resource-search placeholder="Search resources, topics, or audiences" value="${escapeHtml(state.resourceSearch)}" /><select data-resource-category>${categories.map((category) => `<option ${state.resourceCategory === category ? "selected" : ""}>${category}</option>`).join("")}</select><strong>${filtered.length} resources</strong></div><div class="resource-grid">${filtered.slice(0, 36).map(resourceCard).join("")}</div></section>`;
}

function clientPortal() {
  const myClient = clients[2];
  return dashboardLayout("Client Portal", `Welcome back, ${myClient.name}. Your care plan and next steps are ready.`, `
    <div class="dashboard-grid">${metric("Next Appointment", "Jun 12", "Confirmed session")}${metric("Forms", "3", "Need completion")}${metric("Messages", "2", "Unread secure messages")}${metric("Resources", "8", "Recommended")}</div>
    <div class="portal-layout">
      ${panel("Care Plan Snapshot", `<div class="care-plan"><h3>${myClient.concern} Support Pathway</h3><p>Your mock care plan includes intake forms, one upcoming appointment, recommended resources, and secure follow-up reminders.</p><button class="lime-button" data-client="${myClient.id}">Open My Profile</button></div>`)}
      ${panel("Upcoming Appointments", appointmentList())}
      ${panel("Forms & Messages", taskList())}
      ${panel("Recommended Resources", resources.slice(0, 5).map(compactResource).join(""))}
    </div>`);
}

function counselorDashboard() {
  return dashboardLayout("Counselor Dashboard", "Assigned clients, schedule, tasks, new referrals, and follow-up tracking.", `
    <div class="dashboard-grid">${metric("Assigned Clients", "24", "18 active · 6 intake")}${metric("Today", "7", "Confirmed appointments")}${metric("New Referrals", "5", "Awaiting review")}${metric("Follow-ups", "9", "3 overdue")}</div>
    <div class="two-column">${panel("Assigned Clients", clientTable(clients.slice(0, 10)))}${panel("Schedule", counselorSchedule())}</div>
    <div class="two-column">${panel("New Referrals", referralCards())}${panel("Follow-up Tracking", followUps())}</div>`);
}

function adminDashboard() {
  const active = clients.filter((client) => client.status === "Active").length;
  const utilization = Math.round(counselors.reduce((sum, counselor) => sum + counselor.utilization, 0) / counselors.length);
  return dashboardLayout("Admin CRM", "Executive CRM for lead management, assignment, client status, prayer requests, appointment requests, reporting, search, and filters.", `
    <div class="dashboard-grid five">${metric("New Leads", String(appointmentRequests.filter((request) => request.status === "New").length), "Awaiting intake review", "+18%")}${metric("Active Clients", String(active), "Across 12 counselors", "+7%")}${metric("Appointments This Month", "88", "172 projected", "+12%")}${metric("Prayer Requests", String(prayerRequests.length), "5 request follow-up", "+5%")}${metric("Counselor Utilization", `${utilization}%`, "Healthy capacity range", "Optimal")}</div>
    <div class="admin-tabs"><button data-admin-panel="pipeline" class="${state.activeAdminPanel === "pipeline" ? "active" : ""}">Care Journey Pipeline</button><button data-admin-panel="appointments" class="${state.activeAdminPanel === "appointments" ? "active" : ""}">Appointment Requests</button><button data-admin-panel="prayer" class="${state.activeAdminPanel === "prayer" ? "active" : ""}">Prayer Requests</button><button data-admin-panel="clients" class="${state.activeAdminPanel === "clients" ? "active" : ""}">Client Profiles</button></div>
    ${adminPanel()}
    <div class="chart-grid">${panel("Appointments by Month", barChart(monthlyAppointments))}${panel("Lead Sources", donutChart(leadSources))}${panel("Specialty Demand", horizontalBars(specialtyDemand))}</div>
    <div class="two-column">${panel("Lead Management", leadTable())}${panel("Counselor Utilization", utilizationList())}</div>`);
}

function adminPanel() {
  if (state.activeAdminPanel === "appointments") return panel("Appointment Request Management", appointmentManagement());
  if (state.activeAdminPanel === "prayer") return panel("Prayer Request Management", prayerManagement());
  if (state.activeAdminPanel === "clients") return panel("Client Profile Directory", clientDirectory());
  return panel("Care Journey Pipeline", kanbanBoard());
}

function kanbanBoard() {
  return `<div class="kanban-board">${pipelineStages.map((stage) => `<section class="kanban-column"><h3>${stage}<span>${appointmentRequests.filter((request) => request.status === stage).length}</span></h3>${appointmentRequests.filter((request) => request.status === stage).slice(0, 5).map((request) => `<article class="kanban-card"><strong>${request.name}</strong><p>${request.preferredCare}</p><small>${request.source} · ${request.urgency}</small></article>`).join("")}</section>`).join("")}</div>`;
}

function appointmentManagement() {
  return `<div class="management-list">${appointmentRequests.map((request) => `<article><div><strong>${request.name}</strong><p>${request.concern} · ${request.preferredCare}</p></div><span class="pill ${request.urgency.toLowerCase()}">${request.urgency}</span><span>${request.source}</span><em>${request.status}</em><button>Assign</button></article>`).join("")}</div>`;
}

function prayerManagement() {
  return `<div class="management-list prayer-management">${prayerRequests.map((request) => `<article><div><strong>${request.name}</strong><p>${request.request}</p></div><span>${request.category}</span><em>${request.status}</em><button>${request.followUp ? "Follow up" : "Mark prayed"}</button></article>`).join("")}</div>`;
}

function clientDirectory() {
  return `<div class="client-directory">${clientStatuses.map((status) => `<div><h3>${status}</h3>${clients.filter((client) => client.status === status).slice(0, 5).map((client) => `<button data-client="${client.id}"><strong>${client.name}</strong><span>${client.concern} · ${client.ageGroup}</span></button>`).join("")}</div>`).join("")}</div>`;
}

function clientProfileModal(client) {
  const counselor = counselors.find((item) => item.id === client.counselorId) || counselors[0];
  return `<div class="modal-backdrop" role="dialog" aria-modal="true"><article class="profile-modal client-modal"><button class="close-button" data-close-client>×</button><div class="profile-hero"><div class="client-avatar">${client.name.split(" ").map((part) => part[0]).join("")}</div><div><p class="eyebrow">Client Profile</p><h2>${client.name}</h2><p class="credential-line white">${client.ageGroup} · ${client.status} · Assigned to ${counselor.name}</p><div class="tags light"><span>${client.concern}</span><span>Next: ${client.nextAppointment}</span></div></div></div><div class="profile-content">${info("Care status", client.status)}${info("Primary concern", client.concern)}${info("Assigned counselor", `${counselor.name}, ${counselor.credentials}`)}${info("Last contact", client.lastContact)}${info("Next appointment", client.nextAppointment)}${info("Mock notes", "Forms, appointments, follow-up tasks, billing placeholders, and message summaries are prototype-only mock data.")}</div></article></div>`;
}

function counselorProfileModal(counselor) {
  return `<div class="modal-backdrop" role="dialog" aria-modal="true"><article class="profile-modal"><button class="close-button" data-close-counselor>×</button><div class="profile-hero"><img src="${counselor.headshot}" alt="${counselor.name} professional headshot" /><div><p class="eyebrow">Counselor Profile</p><h2>${counselor.name}</h2><p class="credential-line white">${counselor.credentials} · ${counselor.role}</p><div class="tags light">${counselor.populations.map((tag) => `<span>${tag}</span>`).join("")}</div></div></div><div class="profile-content">${info("Bio", counselor.bio)}${info("Specialties", counselor.specialties.join(", "))}${info("Insurance accepted", counselor.insurance.join(", "))}${info("Faith integration approach", counselor.faithApproach)}${info("Availability", `${counselor.availability} · ${counselor.location}`)}${info("Utilization", `${counselor.utilization}% mock caseload utilization`)}</div></article></div>`;
}

function recommendCounselor(answers) {
  return counselors.map((counselor) => {
    let score = counselor.acceptingNew ? 20 : 0;
    if (counselor.specialties.includes(answers.concern)) score += 40;
    if (counselor.populations.includes(answers.person) || (answers.person === "Couple" && counselor.populations.includes("Couples"))) score += 20;
    if (answers.location === "Any" || counselor.location === answers.location) score += 15;
    if (counselor.faithApproach.toLowerCase().includes(answers.faith.toLowerCase())) score += 5;
    return { counselor, score };
  }).sort((a, b) => b.score - a.score)[0].counselor;
}

function feature(title, text) { return `<article class="feature-card"><span>✦</span><h3>${title}</h3><p>${text}</p></article>`; }
function teamCard(counselor) { return `<button class="team-card" data-counselor="${counselor.id}"><img src="${counselor.headshot}" alt="${counselor.name} professional headshot" /><strong>${counselor.name}</strong><span>${counselor.credentials}</span><small>${counselor.specialties.slice(0, 2).join(" • ")}</small></button>`; }
function counselorCard(counselor) { return `<article class="counselor-card"><img src="${counselor.headshot}" alt="${counselor.name} professional headshot" /><div class="card-body"><div class="between"><h3>${counselor.name}</h3><span class="${counselor.acceptingNew ? "status green" : "status muted"}">${counselor.acceptingNew ? "Open" : "Waitlist"}</span></div><p class="credential-line">${counselor.credentials} · ${counselor.role}</p><p>${counselor.bio}</p><div class="tags">${counselor.specialties.slice(0, 4).map((tag) => `<span>${tag}</span>`).join("")}</div><button class="lime-button full" data-counselor="${counselor.id}">View Profile</button></div></article>`; }
function quizField(label, key, options) { return `<fieldset class="quiz-field"><legend>${label}</legend>${options.map((option) => `<button type="button" data-quiz-key="${key}" data-quiz-value="${option}" class="${state.quiz[key] === option ? "active" : ""}">${option}</button>`).join("")}</fieldset>`; }
function resourceCard(resource) { return `<article class="resource-card"><span>${resource.category}</span><h3>${resource.title}</h3><p>${resource.audience} · ${resource.readTime}</p></article>`; }
function compactResource(resource) { return `<p class="compact-resource"><strong>${resource.title}</strong><span>${resource.category} · ${resource.readTime}</span></p>`; }
function pageHero(eyebrow, title, text) { return `<div class="page-hero cloud-panel"><p class="eyebrow">${eyebrow}</p><h1>${title}</h1><p>${text}</p></div>`; }
function metric(label, value, detail, trend = "") { return `<article class="metric-card"><span>${label}</span><strong>${value}</strong><p>${detail}</p>${trend ? `<em>${trend}</em>` : ""}</article>`; }
function panel(title, body) { return `<section class="panel"><div class="panel-title"><h3>${title}</h3><span>Mock data</span></div>${body}</section>`; }
function dashboardLayout(title, subtitle, children) { return `<section class="dashboard-shell"><div class="dashboard-hero"><div><p class="eyebrow">ELCCC Care Connect</p><h1>${title}</h1><p>${subtitle}</p></div><button class="lime-button">Export Presentation</button></div>${children}</section>`; }
function barChart(data) { const max = Math.max(...data.map((item) => item.value)); return `<div class="bar-chart">${data.map((item) => `<div class="bar-item"><div style="height:${(item.value / max) * 100}%"></div><span>${item.month}</span><strong>${item.value}</strong></div>`).join("")}</div>`; }
function donutChart(data) { return `<div class="donut-wrap"><div class="donut"></div><div>${data.map((item) => `<p><span class="legend-dot"></span>${item.label}: ${item.value}%</p>`).join("")}</div></div>`; }
function horizontalBars(data) { const max = Math.max(...data.map((item) => item.value)); return `<div class="hbars">${data.map((item) => `<div><span>${item.label}</span><div><i style="width:${(item.value / max) * 100}%"></i></div><strong>${item.value}</strong></div>`).join("")}</div>`; }
function prayerForm() { return `<form class="prayer-card"><input placeholder="Name or Anonymous" /><select><option>Prayer category</option><option>Anxiety</option><option>Family</option><option>Recovery</option></select><textarea placeholder="How can we pray for you?"></textarea><button type="button" class="lime-button full">Submit Prayer Request</button></form>`; }
function appointmentList() { return `<div class="list">${clients.slice(0, 4).map((client) => `<p><strong>${client.nextAppointment}</strong><span>${client.concern} session · Confirmed</span></p>`).join("")}</div>`; }
function taskList() { return `<div class="list"><p><strong>Adult intake</strong><span>Due before first session</span></p><p><strong>Insurance details</strong><span>Needs update</span></p><p><strong>Message from intake</strong><span>Unread</span></p></div>`; }
function clientTable(items) { return `<div class="table-list">${items.map((client) => `<div><button data-client="${client.id}" class="link-button"><strong>${client.name}</strong></button><span>${client.concern}</span><em>${client.status}</em></div>`).join("")}</div>`; }
function counselorSchedule() { return `<div class="schedule-list">${clients.slice(0, 6).map((client, index) => `<article><time>${9 + index}:00</time><div><strong>${client.name}</strong><span>${client.concern} · ${index % 2 ? "Telehealth" : "McDonough"}</span></div></article>`).join("")}</div>`; }
function referralCards() { return `<div class="referral-grid">${appointmentRequests.slice(0, 6).map((request) => `<article><strong>${request.name}</strong><p>${request.preferredCare}</p><span>${request.urgency} · ${request.source}</span><button>Review referral</button></article>`).join("")}</div>`; }
function followUps() { return `<div class="list">${appointmentRequests.slice(0, 5).map((request) => `<p><strong>${request.name}</strong><span>${request.status} · ${request.urgency}</span></p>`).join("")}</div>`; }
function leadTable() { return `<div class="table-list">${appointmentRequests.slice(0, 7).map((request) => `<div><strong>${request.name}</strong><span>${request.preferredCare}</span><em>${request.status}</em></div>`).join("")}</div>`; }
function utilizationList() { return `<div class="util-list">${counselors.slice(0, 8).map((counselor) => `<div><span>${counselor.name}</span><div><i style="width:${counselor.utilization}%"></i></div><strong>${counselor.utilization}%</strong></div>`).join("")}</div>`; }
function info(title, text) { return `<div class="info-block"><h4>${title}</h4><p>${text}</p></div>`; }
function escapeHtml(text) { return text.replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]); }

function bindEvents() {
  document.querySelectorAll("[data-view]").forEach((el) => el.addEventListener("click", () => { state.view = el.dataset.view; window.scrollTo(0, 0); render(); }));
  document.querySelectorAll("[data-counselor]").forEach((el) => el.addEventListener("click", () => { state.selectedCounselor = counselors.find((counselor) => counselor.id === el.dataset.counselor); render(); }));
  document.querySelectorAll("[data-client]").forEach((el) => el.addEventListener("click", () => { state.selectedClient = clients.find((client) => client.id === el.dataset.client); render(); }));
  document.querySelectorAll("[data-counselor-filter]").forEach((el) => el.addEventListener("click", () => { state.counselorFilter = el.dataset.counselorFilter; render(); }));
  document.querySelectorAll("[data-admin-panel]").forEach((el) => el.addEventListener("click", () => { state.activeAdminPanel = el.dataset.adminPanel; render(); }));
  document.querySelectorAll("[data-quiz-key]").forEach((el) => el.addEventListener("click", () => { state.quiz[el.dataset.quizKey] = el.dataset.quizValue; render(); }));
  document.querySelectorAll("[data-close-counselor]").forEach((el) => el.addEventListener("click", () => { state.selectedCounselor = null; render(); }));
  document.querySelectorAll("[data-close-client]").forEach((el) => el.addEventListener("click", () => { state.selectedClient = null; render(); }));
  const resourceSearch = document.querySelector("[data-resource-search]");
  if (resourceSearch) resourceSearch.addEventListener("input", (event) => {
    const cursor = event.target.selectionStart || event.target.value.length;
    state.resourceSearch = event.target.value;
    render();
    const nextSearch = document.querySelector("[data-resource-search]");
    if (nextSearch) {
      nextSearch.focus();
      nextSearch.setSelectionRange(cursor, cursor);
    }
  });
  const resourceCategory = document.querySelector("[data-resource-category]");
  if (resourceCategory) resourceCategory.addEventListener("change", (event) => { state.resourceCategory = event.target.value; render(); });
}

render();
