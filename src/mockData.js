const headshot = (seed) => `https://i.pravatar.cc/420?img=${(seed % 70) + 1}`;

export const counselors = [
  {
    id: "denice-colson",
    name: "Dr. Denice Colson",
    credentials: "PhD, LPC, MAC, CPCS",
    role: "Clinical Director",
    headshot: headshot(1551836022),
    bio: "Denice provides clinical leadership for trauma-informed care, addiction recovery, and counselor development with a deeply compassionate Christian counseling posture.",
    specialties: ["Trauma", "Addiction", "Clinical Supervision", "DUI Evaluations"],
    insurance: ["Self-pay", "Aetna", "BCBS"],
    faithApproach: "Faith-forward care with client consent, integrating prayer, Scripture, and evidence-based trauma recovery when desired.",
    availability: "Limited availability · Tue mornings · Consultation only",
    acceptingNew: false,
    utilization: 96,
    location: "McDonough",
    populations: ["Adults", "Teens"]
  },
  {
    id: "staci-stephens",
    name: "Staci Stephens",
    credentials: "LPC, RPT",
    role: "Play Therapist",
    headshot: headshot(1494790108377),
    bio: "Staci supports children and families through play therapy, parent coaching, and gentle trauma-informed interventions.",
    specialties: ["Play Therapy", "Children", "Family Systems", "Anxiety"],
    insurance: ["Aetna", "Anthem BCBS", "Cigna", "United Healthcare"],
    faithApproach: "Client-led faith integration with age-appropriate spiritual encouragement for children and parents.",
    availability: "Accepting new child clients · Mon/Wed afternoons",
    acceptingNew: true,
    utilization: 88,
    location: "McDonough",
    populations: ["Children", "Families"]
  },
  {
    id: "melissa-smith",
    name: "Melissa Smith",
    credentials: "MA, BCCC",
    role: "Counselor",
    headshot: headshot(1544005313),
    bio: "Melissa offers warm counseling for adults navigating grief, burnout, relationships, anxiety, depression, and spiritual formation.",
    specialties: ["Grief", "Relationships", "Anxiety", "Depression", "Spiritual Formation"],
    insurance: ["Self-pay", "Sliding scale"],
    faithApproach: "Highly faith-integrated for clients who want pastoral encouragement woven into clinical care.",
    availability: "Telehealth openings · Tue/Thu evenings",
    acceptingNew: true,
    utilization: 79,
    location: "Telehealth",
    populations: ["Adults", "Couples"]
  },
  {
    id: "jonathan-reeves",
    name: "Jonathan Reeves",
    credentials: "LPC, NCC",
    role: "Counselor",
    headshot: headshot(1500648767791),
    bio: "Jonathan helps men, couples, and teens build practical tools for anxiety, conflict, anger, and life transitions.",
    specialties: ["Men's Issues", "Couples", "Anxiety", "Anger", "Teens"],
    insurance: ["Aetna", "Cigna", "Self-pay"],
    faithApproach: "Collaborative faith integration focused on identity, purpose, and practical growth.",
    availability: "Accepting new clients · Fridays and evenings",
    acceptingNew: true,
    utilization: 72,
    location: "Forsyth",
    populations: ["Adults", "Teens", "Couples"]
  },
  {
    id: "rachel-kim",
    name: "Rachel Kim",
    credentials: "LCSW",
    role: "Counselor",
    headshot: headshot(1534528741775),
    bio: "Rachel specializes in anxiety, depression, cultural stress, parenting, and family relationships with calm, strengths-based care.",
    specialties: ["Anxiety", "Depression", "Parenting", "Family Systems", "Cultural Stress"],
    insurance: ["BCBS", "United Healthcare", "Self-pay"],
    faithApproach: "Optional faith integration; clients set the pace and level of spiritual conversation.",
    availability: "Accepting new clients · Mon/Tue mornings",
    acceptingNew: true,
    utilization: 68,
    location: "McDonough",
    populations: ["Adults", "Families"]
  },
  {
    id: "amy-parker",
    name: "Amy Parker",
    credentials: "APRN, PMHNP-BC",
    role: "Psychiatric Nurse Practitioner",
    headshot: headshot(1580489944761),
    bio: "Amy provides medication management consultation with a holistic view of emotional, physical, and spiritual wellness.",
    specialties: ["Medication Management", "Depression", "Anxiety", "Mood Concerns"],
    insurance: ["Aetna", "BCBS", "Cigna", "Self-pay"],
    faithApproach: "Respectful whole-person care with optional prayer and spiritual support when requested.",
    availability: "New evaluations · Wednesdays",
    acceptingNew: true,
    utilization: 83,
    location: "McDonough",
    populations: ["Adults", "Teens"]
  },
  {
    id: "brian-holloway",
    name: "Brian Holloway",
    credentials: "LAPC",
    role: "Counselor",
    headshot: headshot(1519085360753),
    bio: "Brian serves teens and young adults experiencing stress, identity questions, school pressure, and family conflict.",
    specialties: ["Teens", "Young Adults", "Identity", "Stress", "Family Conflict"],
    insurance: ["Self-pay", "Sliding scale"],
    faithApproach: "Mentoring-oriented faith integration, always guided by client and guardian preference.",
    availability: "Accepting new clients · After-school hours",
    acceptingNew: true,
    utilization: 61,
    location: "Forsyth",
    populations: ["Teens", "Adults"]
  },
  {
    id: "sarah-williams",
    name: "Sarah Williams",
    credentials: "LMFT",
    role: "Marriage & Family Therapist",
    headshot: headshot(1544725176),
    bio: "Sarah works with couples and families to restore communication, rebuild trust, and develop healthier relational patterns.",
    specialties: ["Marriage", "Family Systems", "Premarital", "Communication", "Trust Repair"],
    insurance: ["BCBS", "Cigna", "Self-pay"],
    faithApproach: "Biblically informed relationship care for couples and families who request it.",
    availability: "Waitlist · Couples intensives monthly",
    acceptingNew: false,
    utilization: 94,
    location: "McDonough",
    populations: ["Couples", "Families", "Adults"]
  },
  {
    id: "maria-gonzalez",
    name: "Maria Gonzalez",
    credentials: "LPC",
    role: "Trauma Counselor",
    headshot: headshot(1508214751196),
    bio: "Maria provides stabilizing trauma care for adults healing from abuse, grief, panic, and difficult life transitions.",
    specialties: ["Trauma", "Abuse Recovery", "Panic", "Grief", "Life Transitions"],
    insurance: ["Aetna", "United Healthcare", "Self-pay"],
    faithApproach: "Gentle, consent-based spiritual care that emphasizes safety, dignity, and hope.",
    availability: "Accepting new clients · Thu/Fri afternoons",
    acceptingNew: true,
    utilization: 77,
    location: "Telehealth",
    populations: ["Adults"]
  },
  {
    id: "kevin-brooks",
    name: "Kevin Brooks",
    credentials: "CADC-II, LAPC",
    role: "Recovery Counselor",
    headshot: headshot(1530268729831),
    bio: "Kevin supports clients and families navigating substance use, relapse prevention, recovery planning, and accountability.",
    specialties: ["Substance Abuse", "Recovery", "Relapse Prevention", "Family Support"],
    insurance: ["Self-pay", "Sliding scale", "Selected insurance"],
    faithApproach: "Recovery-oriented Christian care that can include prayer, confession, community, and practical relapse prevention.",
    availability: "Accepting new clients · Evening groups",
    acceptingNew: true,
    utilization: 74,
    location: "McDonough",
    populations: ["Adults", "Families"]
  },
  {
    id: "lauren-bennett",
    name: "Lauren Bennett",
    credentials: "LPC",
    role: "Child & Adolescent Counselor",
    headshot: headshot(1524504388940),
    bio: "Lauren helps children, teens, and parents build emotional regulation skills and stronger family connection.",
    specialties: ["Children", "Teens", "ADHD", "Emotional Regulation", "Parent Coaching"],
    insurance: ["Aetna", "BCBS", "Peachstate", "Self-pay"],
    faithApproach: "Optional child-friendly faith integration with guardian consent and client comfort.",
    availability: "Accepting new clients · Mon-Thu afternoons",
    acceptingNew: true,
    utilization: 81,
    location: "Forsyth",
    populations: ["Children", "Teens", "Families"]
  },
  {
    id: "thomas-green",
    name: "Thomas Green",
    credentials: "PhD, LPC",
    role: "Senior Counselor",
    headshot: headshot(1507003211169),
    bio: "Thomas provides thoughtful care for executives, ministry leaders, and adults facing burnout, depression, and major decisions.",
    specialties: ["Burnout", "Leadership", "Depression", "Spiritual Direction", "Life Transitions"],
    insurance: ["Self-pay", "BCBS"],
    faithApproach: "Deeply integrative care for clients seeking clinical wisdom and spiritual discernment.",
    availability: "Limited openings · Executive blocks",
    acceptingNew: true,
    utilization: 86,
    location: "Telehealth",
    populations: ["Adults"]
  }
];

const firstNames = ["Avery", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Harper", "Parker", "Elliot", "Quinn", "Reese", "Cameron", "Logan", "Maya", "Noah", "Olivia", "Ethan", "Sophia", "Caleb", "Grace"];
const lastNames = ["Bennett", "Carter", "Davis", "Edwards", "Foster", "Gray", "Hayes", "Johnson", "King", "Lewis", "Mitchell", "Nelson", "Owens", "Price", "Reed", "Simmons", "Turner", "Walker", "Young", "Brooks"];
const concerns = ["Anxiety", "Depression", "Trauma", "Grief", "Marriage", "Parenting", "Substance Abuse", "Stress", "Child Behavior", "Spiritual Direction"];

export const clients = Array.from({ length: 50 }, (_, index) => {
  const counselor = counselors[index % counselors.length];
  const status = ["Lead", "Intake Pending", "Active", "Follow-up", "Discharged"];
  return {
    id: `client-${String(index + 1).padStart(2, "0")}`,
    name: `${firstNames[index % firstNames.length]} ${lastNames[(index * 3) % lastNames.length]}`,
    ageGroup: index % 7 === 0 ? "Child" : index % 5 === 0 ? "Teen" : "Adult",
    counselorId: counselor.id,
    status: status[index % status.length],
    concern: concerns[(index * 2) % concerns.length],
    lastContact: `2026-05-${String((index % 27) + 1).padStart(2, "0")}`,
    nextAppointment: `2026-06-${String((index % 24) + 5).padStart(2, "0")}`
  };
});

export const appointmentRequests = Array.from({ length: 25 }, (_, index) => ({
  id: `request-${String(index + 1).padStart(2, "0")}`,
  name: `${firstNames[(index + 4) % firstNames.length]} ${lastNames[(index * 5) % lastNames.length]}`,
  concern: concerns[(index * 3) % concerns.length],
  preferredCare: ["Individual Counseling", "Play Therapy", "Marriage Counseling", "Medication Management", "Trauma Recovery"][index % 5],
  urgency: (["Routine", "Soon", "High"])[index % 3],
  source: (["Website", "Match Quiz", "Phone", "Referral"])[index % 4],
  status: (["New", "Contacted", "Assigned", "Scheduled"])[index % 4],
  submitted: `2026-06-${String((index % 4) + 1).padStart(2, "0")}`
}));

export const prayerRequests = Array.from({ length: 10 }, (_, index) => ({
  id: `prayer-${String(index + 1).padStart(2, "0")}`,
  name: index % 3 === 0 ? "Anonymous" : `${firstNames[(index + 8) % firstNames.length]} ${lastNames[(index * 4) % lastNames.length]}`,
  category: ["Anxiety", "Family", "Marriage", "Recovery", "Grief", "Health", "Parenting", "Spiritual Direction", "Work", "Caregiving"][index],
  request: [
    "Please pray for peace as our family begins counseling.",
    "Pray for wisdom in a difficult parenting season.",
    "Please pray for healing and renewed trust in our marriage.",
    "Pray for courage and consistency in recovery.",
    "Please pray for comfort after a recent loss.",
    "Pray for strength during treatment and medical decisions.",
    "Please pray for patience and connection at home.",
    "Pray that I can hear God's direction clearly.",
    "Please pray for balance and reduced workplace anxiety.",
    "Pray for endurance while caring for an aging parent."
  ][index],
  followUp: index % 2 === 0,
  status: (["New", "Prayed For", "Follow-up Needed"])[index % 3]
}));

const resourceCategories = ["Anxiety", "Depression", "Trauma Recovery", "Parenting", "Marriage", "Grief", "Addiction Recovery", "Faith & Wellness", "Children", "Getting Started"];
const resourceTopics = [
  "Grounding Skills", "First Visit Guide", "When Your Child Feels Overwhelmed", "Restoring Communication", "Grief in Daily Life",
  "Recovery Planning", "Calming Breath Prayer", "Understanding Trauma Responses", "Healthy Boundaries", "Preparing for Intake"
];

export const resources = Array.from({ length: 100 }, (_, index) => ({
  id: `resource-${String(index + 1).padStart(3, "0")}`,
  title: `${resourceTopics[index % resourceTopics.length]} ${index > 9 ? `· Part ${Math.floor(index / 10) + 1}` : ""}`.trim(),
  category: resourceCategories[index % resourceCategories.length],
  audience: ["Adults", "Parents", "Teens", "Couples", "Families"][index % 5],
  readTime: `${4 + (index % 8)} min read`,
  featured: index < 8
}));

export const monthlyAppointments = [
  { month: "Jan", value: 116 }, { month: "Feb", value: 124 }, { month: "Mar", value: 141 },
  { month: "Apr", value: 156 }, { month: "May", value: 172 }, { month: "Jun", value: 88 }
];

export const leadSources = [
  { label: "Website", value: 38 },
  { label: "Match Quiz", value: 24 },
  { label: "Phone", value: 18 },
  { label: "Referral", value: 20 }
];

export const specialtyDemand = [
  { label: "Anxiety", value: 28 },
  { label: "Trauma", value: 22 },
  { label: "Children", value: 17 },
  { label: "Marriage", value: 14 },
  { label: "Recovery", value: 11 },
  { label: "Grief", value: 8 }
];
