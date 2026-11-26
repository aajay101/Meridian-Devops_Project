<template>
  <div class="landing">
    <!-- ===== HEADER ===== -->
    <header class="header">
      <div class="header-inner">
        <div class="header-left">
          <router-link to="/" class="brand">
            <i class="bi bi-mortarboard-fill brand-icon"></i>
            <span class="brand-name">Meridian</span>
          </router-link>
        </div>
        <nav class="header-nav" :class="{ open: mobileNavOpen }">
          <a href="#drives" class="nav-link" @click="mobileNavOpen = false">Explore Drives</a>
          <a href="#companies" class="nav-link" @click="mobileNavOpen = false">Companies</a>
          <a href="#roles" class="nav-link" @click="mobileNavOpen = false">Roles</a>
          <a href="#colleges" class="nav-link" @click="mobileNavOpen = false">Colleges</a>
          <a href="#how-it-works" class="nav-link" @click="mobileNavOpen = false">How It Works</a>
        </nav>
        <div class="header-right">
          <router-link to="/login" class="btn-header-text">Sign In</router-link>
          <router-link to="/register" class="btn-header-primary">Get Started</router-link>
        </div>
        <button class="mobile-toggle" @click="mobileNavOpen = !mobileNavOpen" aria-label="Toggle navigation">
          <i :class="mobileNavOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
        </button>
      </div>
    </header>

    <!-- ===== HERO ===== -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-eyebrow">PLACEMENT MANAGEMENT PLATFORM</div>
        <h1 class="hero-title">Find the right placement opportunity</h1>
        <p class="hero-sub">
          Discover placement drives, companies and roles based on your academic profile and eligibility.
        </p>


      </div>
    </section>

    <!-- ===== POPULAR CATEGORIES ===== -->
    <section class="section section--alt" id="categories">
      <div class="container">
        <div class="section-head">
          <h2 class="section-title">Explore Placement Categories</h2>
          <p class="section-sub">Discover opportunities across popular placement domains.</p>
        </div>
        <div class="cat-grid">
          <a v-for="cat in categories" :key="cat.name" href="#drives" class="cat-card">
            <div class="cat-icon"><i :class="cat.icon"></i></div>
            <div class="cat-info">
              <div class="cat-name">{{ cat.name }}</div>
              <div class="cat-count">{{ cat.label }}</div>
            </div>
            <i class="bi bi-chevron-right cat-arrow"></i>
          </a>
        </div>
      </div>
    </section>

    <!-- ===== LATEST PLACEMENT DRIVES ===== -->
    <section class="section" id="drives">
      <div class="container">
        <div class="section-head">
          <div>
            <h2 class="section-title">Latest Placement Drives</h2>
            <p class="section-sub">Recently posted opportunities from leading companies.</p>
          </div>
          <router-link to="/login" class="view-all">View all drives <i class="bi bi-arrow-right"></i></router-link>
        </div>
        <div class="drive-list">
          <router-link v-for="drive in placementDrives" :key="drive.id" to="/login" class="drive-card">
            <div class="drive-title">{{ drive.title }}</div>
            <div class="drive-company">{{ drive.company }}</div>
            <div class="drive-meta">
              <span><i class="bi bi-mortarboard"></i> {{ drive.branch }}</span>
              <span><i class="bi bi-calendar3"></i> {{ drive.year }}</span>
              <span><i class="bi bi-graph-up-arrow"></i> CGPA {{ drive.cgpa }}+</span>
            </div>
            <div class="drive-bottom">
              <span class="drive-deadline">
                <i class="bi bi-clock"></i> {{ drive.daysAgo }} days ago
              </span>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== TOP COMPANIES HIRING NOW ===== -->
    <section class="section section--alt" id="companies">
      <div class="container">
        <div class="section-head">
          <div>
            <h2 class="section-title">Top Companies Hiring on Campus</h2>
            <p class="section-sub">Explore companies actively recruiting for graduate and entry-level roles.</p>
          </div>
        </div>
        <div class="company-rail">
          <div v-for="cat in companyCategories" :key="cat.name" class="company-cat-card">
            <div class="company-cat-name">{{ cat.name }}</div>
            <div class="company-cat-label">{{ cat.label }}</div>
            <div class="company-logos">
              <img
                v-for="co in cat.companies"
                :key="co.name"
                :src="co.logo"
                :alt="co.name"
                class="company-logo-img"
                loading="lazy"
                @error="(e) => e.target.style.display = 'none'"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== FEATURED COMPANIES ===== -->
    <section class="section" id="featured">
      <div class="container">
        <div class="section-head">
          <div>
            <h2 class="section-title">Featured Companies Actively Hiring</h2>
            <p class="section-sub">Leading organizations looking for campus talent.</p>
          </div>
          <a href="#companies" class="view-all">View all companies <i class="bi bi-arrow-right"></i></a>
        </div>
        <div class="featured-grid">
          <div v-for="co in featuredCompanies" :key="co.name" class="featured-card">
            <img :src="co.logo" :alt="co.name" class="featured-logo" loading="lazy" @error="(e) => e.target.style.display = 'none'" />
            <div class="featured-body">
              <div class="featured-name">{{ co.name }}</div>
              <p class="featured-desc">{{ co.desc }}</p>
              <div class="featured-tags">
                <span v-for="t in co.tags" :key="t" class="pill">{{ t }}</span>
              </div>
            </div>
            <a :href="co.officialWebsite" target="_blank" rel="noopener noreferrer" class="featured-link">View opportunities <i class="bi bi-box-arrow-up-right"></i></a>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== IN-DEMAND PLACEMENT ROLES (CAROUSEL) ===== -->
    <section class="section section--alt" id="roles">
      <div class="container">
        <div class="section-head">
          <div>
            <h2 class="section-title">In-Demand Placement Roles</h2>
            <p class="section-sub">Explore roles that top companies are hiring for on campus.</p>
          </div>
        </div>
        <div class="roles-carousel-wrap">
          <button
            class="carousel-arrow carousel-arrow--left"
            :class="{ 'carousel-arrow--hidden': !canScrollLeft }"
            @click="scrollRoles(-1)"
            aria-label="Scroll left"
          >
            <i class="bi bi-chevron-left"></i>
          </button>
          <div class="roles-rail" ref="rolesRail" @scroll="checkRoleScroll">
            <a v-for="role in popularRoles" :key="role.title" href="#drives" class="role-card">
              <img :src="role.companyLogo" :alt="role.company" class="role-card-logo" loading="lazy" @error="(e) => e.target.style.display = 'none'" />
              <div class="role-card-title">{{ role.title }}</div>
              <div class="role-card-company">{{ role.company }}</div>
              <div class="role-card-meta">{{ role.category }}</div>
              <i class="bi bi-arrow-right role-card-arrow"></i>
            </a>
          </div>
          <button
            class="carousel-arrow carousel-arrow--right"
            :class="{ 'carousel-arrow--hidden': !canScrollRight }"
            @click="scrollRoles(1)"
            aria-label="Scroll right"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- ===== TOP COLLEGES ===== -->
    <section class="section" id="colleges">
      <div class="container">
        <div class="section-head">
          <div>
            <h2 class="section-title">Top Colleges on Meridian</h2>
            <p class="section-sub">Premier institutions with active placement programs.</p>
          </div>
        </div>
        <div class="college-carousel-wrap">
          <button
            class="carousel-arrow carousel-arrow--left"
            :class="{ 'carousel-arrow--hidden': !canScrollCollegesLeft }"
            @click="scrollColleges(-1)"
            aria-label="Scroll left"
          >
            <i class="bi bi-chevron-left"></i>
          </button>
          <div class="college-rail" ref="collegesRail" @scroll="checkCollegeScroll">
            <div v-for="clg in topColleges" :key="clg.name" class="college-card">
              <img :src="clg.logo" :alt="clg.name" class="college-logo-img" />
              <div class="college-name">{{ clg.name }}</div>
              <p class="college-desc">{{ clg.desc }}</p>
              <div class="college-tags">
                <span v-for="t in clg.tags" :key="t" class="pill">{{ t }}</span>
              </div>
            </div>
          </div>
          <button
            class="carousel-arrow carousel-arrow--right"
            :class="{ 'carousel-arrow--hidden': !canScrollCollegesRight }"
            @click="scrollColleges(1)"
            aria-label="Scroll right"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- ===== HOW IT WORKS ===== -->
    <section class="section section--alt" id="how-it-works">
      <div class="container">
        <div class="section-head">
          <h2 class="section-title">How Meridian Works</h2>
        </div>
        <div class="steps">
          <div v-for="(step, i) in howItWorks" :key="i" class="step-card">
            <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <h4 class="step-title">{{ step.title }}</h4>
            <p class="step-desc">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== WHY PLACEMENT PORTAL ===== -->
    <section class="section" id="why">
      <div class="container">
        <div class="section-head">
          <h2 class="section-title">Why Meridian?</h2>
        </div>
        <div class="why-grid">
          <div v-for="item in whyItems" :key="item.title" class="why-card">
            <div class="why-icon"><i :class="item.icon"></i></div>
            <h4 class="why-title">{{ item.title }}</h4>
            <p class="why-desc">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== COMPACT CTA ===== -->
    <section class="cta-compact">
      <div class="container cta-compact-inner">
        <div class="cta-text">
          <h3 class="cta-heading">Ready to explore your next opportunity?</h3>
          <p class="cta-sub">Discover placement drives and companies recruiting on campus.</p>
        </div>
        <div class="cta-actions">
          <router-link to="/register" class="btn-cta-primary">Create Account</router-link>
        </div>
      </div>
    </section>

    <!-- ===== FOOTER ===== -->
    <footer class="footer">
      <div class="container">
        <div class="footer-top">
          <div class="footer-brand-col">
            <div class="footer-brand">
              <i class="bi bi-mortarboard-fill brand-icon"></i>
              <span>Meridian</span>
            </div>
            <p class="footer-about">
              A centralized platform for campus placements, helping students discover opportunities,
              companies manage recruitment, and placement teams coordinate the process.
            </p>
          </div>
          <div class="footer-links">
            <div class="footer-col">
              <h5 class="footer-col-title">Students</h5>
              <router-link to="/login">Explore Drives</router-link>
              <router-link to="/student/applications">Applications</router-link>
              <router-link to="/student/history">Placement History</router-link>
              <router-link to="/student/profile">Profile</router-link>
            </div>
            <div class="footer-col">
              <h5 class="footer-col-title">Companies</h5>
              <router-link to="/register">Company Registration</router-link>
              <router-link to="/company/drives">Placement Drives</router-link>
              <router-link to="/company/drives">Applicants</router-link>
              <router-link to="/company/profile">Company Profile</router-link>
            </div>
            <div class="footer-col">
              <h5 class="footer-col-title">Placement Cell</h5>
              <router-link to="/login">Admin Login</router-link>
              <router-link to="/admin/drives">Manage Drives</router-link>
              <router-link to="/admin/students">Student Management</router-link>
              <router-link to="/admin/reports">Reports</router-link>
            </div>
            <div class="footer-col">
              <h5 class="footer-col-title">Platform</h5>
              <a href="#how-it-works">How It Works</a>
              <a href="#how-it-works">About</a>
              <a href="mailto:placement@meridian.local">Contact</a>
              <a href="#how-it-works">Privacy</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <span>&copy; {{ currentYear }} Meridian</span>
          <span>Built for campus placements.</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const currentYear = new Date().getFullYear()
const mobileNavOpen = ref(false)

/* ============================================
   ROLE CAROUSEL
   ============================================ */
const rolesRail = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)

const checkRoleScroll = () => {
  const el = rolesRail.value
  if (!el) return
  canScrollLeft.value = el.scrollLeft > 4
  canScrollRight.value = el.scrollLeft < el.scrollWidth - el.clientWidth - 4
}

const scrollRoles = (dir) => {
  const el = rolesRail.value
  if (!el) return
  const cardW = el.querySelector('.role-card')?.offsetWidth || 200
  el.scrollBy({ left: dir * (cardW + 12) * 2, behavior: 'smooth' })
}

onMounted(() => nextTick(checkRoleScroll))

/* ============================================
   COLLEGE CAROUSEL
   ============================================ */
const collegesRail = ref(null)
const canScrollCollegesLeft = ref(false)
const canScrollCollegesRight = ref(true)

const checkCollegeScroll = () => {
  const el = collegesRail.value
  if (!el) return
  canScrollCollegesLeft.value = el.scrollLeft > 4
  canScrollCollegesRight.value = el.scrollLeft < el.scrollWidth - el.clientWidth - 4
}

const scrollColleges = (dir) => {
  const el = collegesRail.value
  if (!el) return
  const cardW = el.querySelector('.college-card')?.offsetWidth || 200
  el.scrollBy({ left: dir * (cardW + 14) * 2, behavior: 'smooth' })
}

onMounted(() => nextTick(checkCollegeScroll))

/* ============================================
   LOGOS: Imported official brand assets
   ============================================ */
import tcsLogo from '@/assets/logos/companies/tcs.svg'
import infosysLogo from '@/assets/logos/companies/infosys.svg'
import wiproLogo from '@/assets/logos/companies/wipro.svg'
import cognizantLogo from '@/assets/logos/companies/cognizant.svg'
import microsoftLogo from '@/assets/logos/companies/microsoft.svg'
import amazonLogo from '@/assets/logos/companies/amazon.svg'
import oracleLogo from '@/assets/logos/companies/oracle.svg'
import ciscoLogo from '@/assets/logos/companies/cisco.svg'
import deloitteLogo from '@/assets/logos/companies/deloitte.svg'
import accentureLogo from '@/assets/logos/companies/accenture.svg'
import eyLogo from '@/assets/logos/companies/ey.svg'
import pwcLogo from '@/assets/logos/companies/pwc.svg'
import kpmgLogo from '@/assets/logos/companies/kpmg.svg'
import jpmorganLogo from '@/assets/logos/companies/jpmorgan-chase.svg'
import goldmanLogo from '@/assets/logos/companies/goldman-sachs.svg'
import wellsfargoLogo from '@/assets/logos/companies/wells-fargo.svg'
import siemensLogo from '@/assets/logos/companies/siemens.svg'
import boschLogo from '@/assets/logos/companies/bosch.svg'
import honeywellLogo from '@/assets/logos/companies/honeywell.svg'
import schneiderLogo from '@/assets/logos/companies/schneider-electric.svg'
import ibmLogo from '@/assets/logos/companies/ibm.svg'
import sapLogo from '@/assets/logos/companies/sap.svg'
import techmLogo from '@/assets/logos/companies/tech-mahindra.svg'
import hclLogo from '@/assets/logos/companies/hcltech.svg'

import iitbLogo from '@/assets/logos/colleges/iit-bombay.svg'
import iitdLogo from '@/assets/logos/colleges/iit-delhi.png'
import iitmLogo from '@/assets/logos/colleges/iit-madras.png'
import bitsLogo from '@/assets/logos/colleges/bits-pilani.webp'
import iiscLogo from '@/assets/logos/colleges/iisc-bangalore.jpg'
import iiitbLogo from '@/assets/logos/colleges/iiit-bangalore.png'
import nittLogo from '@/assets/logos/colleges/nit-trichy.png'
import rvceLogo from '@/assets/logos/colleges/rvce.png'
import bmsceLogo from '@/assets/logos/colleges/bmsce.svg'
import pesLogo from '@/assets/logos/colleges/pes.png'

const L = {
  tcs: tcsLogo,
  infosys: infosysLogo,
  wipro: wiproLogo,
  cognizant: cognizantLogo,
  microsoft: microsoftLogo,
  amazon: amazonLogo,
  oracle: oracleLogo,
  cisco: ciscoLogo,
  deloitte: deloitteLogo,
  accenture: accentureLogo,
  ey: eyLogo,
  pwc: pwcLogo,
  kpmg: kpmgLogo,
  jpmorgan: jpmorganLogo,
  goldman: goldmanLogo,
  wellsfargo: wellsfargoLogo,
  siemens: siemensLogo,
  bosch: boschLogo,
  honeywell: honeywellLogo,
  schneider: schneiderLogo,
  ibm: ibmLogo,
  sap: sapLogo,
  techm: techmLogo,
  hcl: hclLogo,
  iitb: iitbLogo,
  iitd: iitdLogo,
  iitm: iitmLogo,
  bits: bitsLogo,
  iisc: iiscLogo,
  nitt: nittLogo,
  iiitb: iiitbLogo,
  rvce: rvceLogo,
  bmsce: bmsceLogo,
  pes: pesLogo,
}

/* ============================================
   DATA: CATEGORIES
   ============================================ */
const categories = [
  { name: 'Software Engineering', label: 'Explore roles', icon: 'bi bi-code-slash' },
  { name: 'Data Science & Analytics', label: 'Explore roles', icon: 'bi bi-bar-chart-line' },
  { name: 'Artificial Intelligence', label: 'Explore roles', icon: 'bi bi-cpu' },
  { name: 'Backend Development', label: 'Explore roles', icon: 'bi bi-server' },
  { name: 'Frontend Development', label: 'Explore roles', icon: 'bi bi-window' },
  { name: 'Full Stack Development', label: 'Explore roles', icon: 'bi bi-stack' },
  { name: 'Cyber Security', label: 'Explore roles', icon: 'bi bi-shield-lock' },
  { name: 'Cloud Computing', label: 'Explore roles', icon: 'bi bi-cloud' },
  { name: 'Finance & Accounting', label: 'Explore roles', icon: 'bi bi-currency-rupee' },
  { name: 'Consulting', label: 'Explore roles', icon: 'bi bi-people' },
]

/* ============================================
   DATA: PLACEMENT DRIVES (real companies + real roles)
   ============================================ */
const placementDrives = [
  { id: 1, title: 'Software Engineer', company: 'Tata Consultancy Services', branch: 'CSE / IT', year: '4th Year', cgpa: 7.0, daysAgo: 5 },
  { id: 2, title: 'Associate Software Engineer', company: 'Accenture', branch: 'CSE / IT / ECE', year: '3rd / 4th Year', cgpa: 6.5, daysAgo: 10 },
  { id: 3, title: 'Graduate Engineer Trainee', company: 'Bosch', branch: 'Mechanical / ECE / EEE', year: '4th Year', cgpa: 7.0, daysAgo: 14 },
  { id: 4, title: 'Systems Engineer', company: 'Infosys', branch: 'CSE / IT / ECE', year: '4th Year', cgpa: 6.0, daysAgo: 7 },
  { id: 5, title: 'Data Analyst', company: 'Deloitte', branch: 'CSE / IT / Statistics', year: '3rd / 4th Year', cgpa: 7.5, daysAgo: 12 },
  { id: 6, title: 'Software Development Engineer', company: 'Amazon', branch: 'CSE / IT', year: '4th Year', cgpa: 8.0, daysAgo: 3 },
]

/* ============================================
   DATA: COMPANY CATEGORIES (real companies + real logos via Clearbit)
   ============================================ */
const companyCategories = [
  {
    name: 'IT Services & Consulting',
    label: 'Graduate roles available',
    companies: [
      { name: 'TCS', logo: L.tcs },
      { name: 'Infosys', logo: L.infosys },
      { name: 'Wipro', logo: L.wipro },
      { name: 'Cognizant', logo: L.cognizant },
    ],
  },
  {
    name: 'Technology & Product',
    label: 'Graduate roles available',
    companies: [
      { name: 'Microsoft', logo: L.microsoft },
      { name: 'Amazon', logo: L.amazon },
      { name: 'Oracle', logo: L.oracle },
      { name: 'Cisco', logo: L.cisco },
    ],
  },
  {
    name: 'Consulting & Advisory',
    label: 'Graduate roles available',
    companies: [
      { name: 'Deloitte', logo: L.deloitte },
      { name: 'EY', logo: L.ey },
      { name: 'PwC', logo: L.pwc },
      { name: 'KPMG', logo: L.kpmg },
    ],
  },
  {
    name: 'Banking & Financial Services',
    label: 'Graduate roles available',
    companies: [
      { name: 'JPMorgan Chase', logo: L.jpmorgan },
      { name: 'Goldman Sachs', logo: L.goldman },
      { name: 'Wells Fargo', logo: L.wellsfargo },
    ],
  },
  {
    name: 'Core Engineering',
    label: 'Graduate roles available',
    companies: [
      { name: 'Siemens', logo: L.siemens },
      { name: 'Bosch', logo: L.bosch },
      { name: 'Honeywell', logo: L.honeywell },
      { name: 'Schneider Electric', logo: L.schneider },
    ],
  },
  {
    name: 'Technology & Services',
    label: 'Graduate roles available',
    companies: [
      { name: 'IBM', logo: L.ibm },
      { name: 'SAP', logo: L.sap },
      { name: 'Tech Mahindra', logo: L.techm },
      { name: 'HCLTech', logo: L.hcl },
    ],
  },
]

/* ============================================
   DATA: FEATURED COMPANIES (real companies)
   ============================================ */
const featuredCompanies = [
  {
    name: 'Infosys',
    logo: L.infosys,
    officialWebsite: 'https://www.infosys.com/',
    desc: 'Global leader in next-generation digital services and consulting, serving clients across 56 countries.',
    tags: ['IT Services', 'Consulting'],
  },
  {
    name: 'Tata Consultancy Services',
    logo: L.tcs,
    officialWebsite: 'https://www.tcs.com/',
    desc: 'India\'s largest IT services company, providing consulting, technology and outsourcing solutions worldwide.',
    tags: ['IT Services', 'Technology'],
  },
  {
    name: 'Accenture',
    logo: L.accenture,
    officialWebsite: 'https://www.accenture.com/',
    desc: 'Global professional services company with capabilities in digital, cloud and security across 40+ industries.',
    tags: ['Consulting', 'Technology'],
  },
  {
    name: 'Microsoft',
    logo: L.microsoft,
    officialWebsite: 'https://www.microsoft.com/',
    desc: 'Leading technology company creating platforms and tools powered by AI that empower every person and organization.',
    tags: ['Product', 'Technology'],
  },
  {
    name: 'Deloitte',
    logo: L.deloitte,
    officialWebsite: 'https://www.deloitte.com/',
    desc: 'World\'s largest professional services firm, providing audit, consulting, financial advisory and tax services.',
    tags: ['Consulting', 'Advisory'],
  },
  {
    name: 'Amazon',
    logo: L.amazon,
    officialWebsite: 'https://www.aboutamazon.com/',
    desc: 'Global technology company and cloud computing leader, offering opportunities across engineering and operations.',
    tags: ['Product', 'Cloud'],
  },
]

/* ============================================
   DATA: POPULAR ROLES (real industry titles)
   ============================================ */
const popularRoles = [
  { title: 'Software Engineer', category: 'Engineering', company: 'Tata Consultancy Services', companyLogo: L.tcs },
  { title: 'Associate Software Engineer', category: 'Engineering', company: 'Accenture', companyLogo: L.accenture },
  { title: 'Graduate Engineer Trainee', category: 'Engineering', company: 'Bosch', companyLogo: L.bosch },
  { title: 'Systems Engineer', category: 'Engineering', company: 'Infosys', companyLogo: L.infosys },
  { title: 'Data Analyst', category: 'Analytics', company: 'Deloitte', companyLogo: L.deloitte },
  { title: 'Data Scientist', category: 'Analytics', company: 'Amazon', companyLogo: L.amazon },
  { title: 'Business Analyst', category: 'Analytics', company: 'EY', companyLogo: L.ey },
  { title: 'Backend Developer', category: 'Engineering', company: 'Microsoft', companyLogo: L.microsoft },
  { title: 'Frontend Developer', category: 'Engineering', company: 'Wipro', companyLogo: L.wipro },
  { title: 'Full Stack Developer', category: 'Engineering', company: 'Cognizant', companyLogo: L.cognizant },
  { title: 'Cloud Engineer', category: 'Infrastructure', company: 'IBM', companyLogo: L.ibm },
  { title: 'DevOps Engineer', category: 'Infrastructure', company: 'Cisco', companyLogo: L.cisco },
  { title: 'QA Engineer', category: 'Quality', company: 'Siemens', companyLogo: L.siemens },
  { title: 'Cyber Security Analyst', category: 'Security', company: 'Honeywell', companyLogo: L.honeywell },
  { title: 'Technical Support Engineer', category: 'Support', company: 'HCLTech', companyLogo: L.hcl },
  { title: 'Product Analyst', category: 'Product', company: 'Oracle', companyLogo: L.oracle },
  { title: 'UX Designer', category: 'Design', company: 'SAP', companyLogo: L.sap },
  { title: 'UI/UX Designer', category: 'Design', company: 'Goldman Sachs', companyLogo: L.goldman },
]

/* ============================================
   DATA: TOP COLLEGES
   ============================================ */
const topColleges = [
  { name: 'IIT Bombay', logo: L.iitb, desc: 'Premier engineering and technology institution in India.', tags: ['Engineering', 'Technology'] },
  { name: 'IIT Delhi', logo: L.iitd, desc: 'Leading institution known for engineering, research and innovation.', tags: ['Engineering', 'Research'] },
  { name: 'IIT Madras', logo: L.iitm, desc: 'Top-ranked institute with strong industry connections and placement record.', tags: ['Engineering', 'Innovation'] },
  { name: 'BITS Pilani', logo: L.bits, desc: 'Premier private institution known for quality engineering education.', tags: ['Engineering', 'Technology'] },
  { name: 'IISc Bangalore', logo: L.iisc, desc: 'India\'s premier research institution for science and engineering.', tags: ['Research', 'Science'] },
  { name: 'NIT Trichy', logo: L.nitt, desc: 'Leading National Institute of Technology with strong placement records.', tags: ['Engineering', 'Technology'] },
  { name: 'IIIT Bangalore', logo: L.iiitb, desc: 'Leading information technology institution focused on IT and electronics.', tags: ['Technology', 'IT'] },
  { name: 'RV College of Engineering', logo: L.rvce, desc: 'One of Bangalore\'s top private engineering colleges with strong placements.', tags: ['Engineering', 'Technology'] },
  { name: 'BMS College of Engineering', logo: L.bmsce, desc: 'Bangalore\'s premier autonomous engineering institution established in 1946.', tags: ['Engineering', 'Technology'] },
  { name: 'PES University', logo: L.pes, desc: 'Leading Bangalore university known for engineering and technology programs.', tags: ['Technology', 'Innovation'] },
]

/* ============================================
   DATA: HOW IT WORKS
   ============================================ */
const howItWorks = [
  { title: 'Create your profile', desc: 'Add your branch, year, CGPA and academic details to get matched with relevant opportunities.' },
  { title: 'Discover eligible drives', desc: 'Browse placement drives filtered by your branch, year and CGPA eligibility.' },
  { title: 'Apply to drives', desc: 'Submit applications directly through the portal with one-click apply.' },
  { title: 'Track your progress', desc: 'Monitor application status, shortlisting and selection progress in real time.' },
]

/* ============================================
   DATA: WHY PLACEMENT PORTAL
   ============================================ */
const whyItems = [
  { title: 'Eligibility-based discovery', desc: 'Students discover drives based on branch, year and CGPA — no noise, only relevant opportunities.', icon: 'bi bi-funnel' },
  { title: 'Centralized recruitment', desc: 'Companies manage placement drives, review applicants and track hiring from a single platform.', icon: 'bi bi-grid' },
  { title: 'Application tracking', desc: 'Students monitor their application and selection status across all applied drives.', icon: 'bi bi-clipboard-check' },
  { title: 'Placement administration', desc: 'Admins manage companies, drives, and generate placement reports for the institution.', icon: 'bi bi-gear' },
]
</script>

<style scoped>
/* ============================================
   LAYOUT — Premium light-mode base
   ============================================ */
.landing {
  font-family: var(--font-family);
  color: #15152A;
  background: #FAFAF9;
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
}
.container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 0 32px;
}
a {
  text-decoration: none;
  color: inherit;
}

/* ============================================
   HEADER
   ============================================ */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #EDE9F6;
}
.header-inner {
  max-width: 1140px;
  margin: 0 auto;
  padding: 0 32px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}
.header-left { display: flex; align-items: center; }
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #15152A;
}
.brand-icon { font-size: 1.15rem; color: #7C3AED; }
.brand-name { font-size: var(--text-base); font-weight: var(--weight-bold); white-space: nowrap; }
.header-nav {
  display: flex;
  align-items: center;
  gap: 2px;
}
.nav-link {
  padding: 6px 14px;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: #52526A;
  border-radius: var(--radius-md);
  transition: color 120ms ease, background 120ms ease;
  white-space: nowrap;
}
.nav-link:hover { color: #15152A; background: #F5F3FA; }
.header-right { display: flex; align-items: center; gap: 8px; }
.btn-header-text {
  padding: 6px 14px;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: #52526A;
  border-radius: var(--radius-md);
  transition: color 120ms ease;
}
.btn-header-text:hover { color: #15152A; }
.btn-header-primary {
  padding: 7px 18px;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #fff;
  background: #7C3AED;
  border-radius: var(--radius-md);
  transition: background 120ms ease;
}
.btn-header-primary:hover { background: #6D28D9; }
.mobile-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #15152A;
  cursor: pointer;
  padding: 4px;
}

/* ============================================
   HERO — Editorial style
   ============================================ */
.hero {
  padding: 72px 32px 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #EDE9F6;
}
.hero-inner {
  max-width: 680px;
  margin: 0 auto;
  text-align: center;
}
.hero-eyebrow {
  font-size: 11px;
  font-weight: var(--weight-semibold);
  letter-spacing: 0.1em;
  color: #7C3AED;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.hero-title {
  font-size: 2.5rem;
  font-weight: var(--weight-bold);
  color: #15152A;
  margin: 0 0 16px;
  line-height: 1.15;
  letter-spacing: -0.025em;
}
.hero-sub {
  font-size: 16px;
  color: #6B6B82;
  margin: 0;
  line-height: 1.7;
  max-width: 520px;
  margin-left: auto;
  margin-right: auto;
}

/* ============================================
   SECTIONS — Generous whitespace
   ============================================ */
.section {
  padding: 72px 0;
}
.section--alt {
  background: #FFFFFF;
}
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 36px;
  gap: 16px;
}
.section-title {
  font-size: 22px;
  font-weight: var(--weight-bold);
  color: #15152A;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.section-sub {
  font-size: var(--text-sm);
  color: #6B6B82;
  margin: 6px 0 0;
  line-height: 1.5;
}
.view-all {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #7C3AED;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: gap 150ms ease;
}
.view-all:hover { gap: 8px; }

/* ============================================
   CATEGORIES
   ============================================ */
.cat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}
.cat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #FAFAF9;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  transition: all 150ms ease;
  cursor: pointer;
}
.cat-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 2px 12px rgba(124, 58, 237, 0.06);
}
.cat-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: #F0ECFE;
  color: #7C3AED;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}
.cat-info { flex: 1; min-width: 0; }
.cat-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #15152A;
  line-height: 1.25;
}
.cat-count {
  font-size: var(--text-xs);
  color: #8E8EA0;
  margin-top: 2px;
}
.cat-arrow {
  color: #D4D4E0;
  font-size: 12px;
  flex-shrink: 0;
  transition: color 120ms ease;
}
.cat-card:hover .cat-arrow { color: #7C3AED; }

/* ============================================
   DRIVES
   ============================================ */
.drive-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.drive-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
  background: #FFFFFF;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  transition: all 150ms ease;
}
.drive-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.06);
}
.drive-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: #7C3AED;
  line-height: 1.3;
  margin-bottom: 4px;
}
.drive-company {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: #15152A;
  margin-bottom: 14px;
}
.drive-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: var(--text-xs);
  color: #6B6B82;
  margin-bottom: 16px;
}
.drive-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.drive-meta i { color: #A0A0B8; font-size: 11px; }
.drive-bottom {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid #F0ECFE;
}
.drive-deadline {
  font-size: var(--text-xs);
  color: #6B6B82;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.drive-deadline i { font-size: 11px; }

/* ============================================
   COMPANY CATEGORIES RAIL
   ============================================ */
.company-rail {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}
.company-cat-card {
  padding: 20px 16px;
  background: #FAFAF9;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  text-align: center;
  transition: all 150ms ease;
}
.company-cat-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 2px 12px rgba(124, 58, 237, 0.06);
}
.company-cat-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin-bottom: 2px;
}
.company-cat-label {
  font-size: var(--text-xs);
  color: #8E8EA0;
  margin-bottom: 14px;
}
.company-logos {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.company-logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: var(--radius-md);
  background: #FFFFFF;
  border: 1px solid #F0ECFE;
  padding: 4px;
}

/* ============================================
   FEATURED COMPANIES
   ============================================ */
.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.featured-card {
  background: #FFFFFF;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  flex-direction: column;
  transition: all 150ms ease;
}
.featured-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.06);
}
.featured-logo {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  object-fit: contain;
  margin-bottom: 18px;
  flex-shrink: 0;
  background: #FAFAF9;
  border: 1px solid #F0ECFE;
  padding: 6px;
}
.featured-body { flex: 1; }
.featured-name {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin-bottom: 10px;
}
.featured-desc {
  font-size: var(--text-xs);
  color: #6B6B82;
  line-height: 1.65;
  margin: 0 0 16px;
}
.featured-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}
.pill {
  display: inline-block;
  font-size: 10px;
  font-weight: var(--weight-medium);
  color: #6B6B82;
  background: #FAFAF9;
  border: 1px solid #EDE9F6;
  padding: 3px 10px;
  border-radius: var(--radius-full);
}
.featured-link {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: #7C3AED;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: auto;
}
.featured-card:hover .featured-link { gap: 8px; }

/* ============================================
   ROLES CAROUSEL
   ============================================ */
.roles-carousel-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
}
.roles-rail {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 4px 0;
  flex: 1;
}
.roles-rail::-webkit-scrollbar { display: none; }

.role-card {
  flex: 0 0 240px;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  padding: 20px 18px;
  background: #FAFAF9;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  transition: all 150ms ease;
  cursor: pointer;
}
.role-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 2px 12px rgba(124, 58, 237, 0.06);
}
.role-card-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: var(--radius-md);
  background: #FFFFFF;
  border: 1px solid #F0ECFE;
  padding: 3px;
  margin-bottom: 12px;
}
.role-card-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin-bottom: 3px;
  line-height: 1.3;
}
.role-card-company {
  font-size: var(--text-xs);
  color: #6B6B82;
  margin-bottom: 2px;
}
.role-card-meta {
  font-size: var(--text-xs);
  color: #8E8EA0;
  margin-bottom: 14px;
}
.role-card-arrow {
  font-size: 13px;
  color: #D4D4E0;
  transition: all 150ms ease;
  margin-top: auto;
}
.role-card:hover .role-card-arrow { color: #7C3AED; transform: translateX(2px); }

.carousel-arrow {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1px solid #EDE9F6;
  background: #FFFFFF;
  color: #6B6B82;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 150ms ease;
  font-size: 14px;
}
.carousel-arrow:hover {
  border-color: #C4B5FD;
  color: #7C3AED;
}
.carousel-arrow--hidden {
  opacity: 0;
  pointer-events: none;
}

/* ============================================
   COLLEGES CAROUSEL
   ============================================ */
.college-carousel-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
}
.college-rail {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 4px 0;
  flex: 1;
}
.college-rail::-webkit-scrollbar { display: none; }
.college-card {
  flex: 0 0 190px;
  scroll-snap-align: start;
  background: #FFFFFF;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
  padding: 24px 18px;
  text-align: center;
  transition: all 150ms ease;
}
.college-card:hover {
  border-color: #C4B5FD;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.06);
}
.college-logo-img {
  height: 48px;
  width: auto;
  max-width: 100%;
  border-radius: var(--radius-lg);
  object-fit: contain;
  margin: 0 auto 14px;
  display: block;
}
.college-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin-bottom: 8px;
}
.college-desc {
  font-size: 11px;
  color: #8E8EA0;
  line-height: 1.5;
  margin: 0 0 12px;
}
.college-tags {
  display: flex;
  justify-content: center;
  gap: 4px;
  flex-wrap: wrap;
}

/* ============================================
   HOW IT WORKS — Connected steps
   ============================================ */
.steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  position: relative;
}
.step-card {
  text-align: center;
  padding: 28px 18px;
  position: relative;
}
.step-card:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 44px;
  right: -12px;
  width: 24px;
  height: 1px;
  background: #EDE9F6;
}
.step-num {
  font-size: 32px;
  font-weight: var(--weight-bold);
  color: #7C3AED;
  opacity: 0.2;
  margin-bottom: 14px;
  line-height: 1;
}
.step-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin: 0 0 10px;
}
.step-desc {
  font-size: var(--text-xs);
  color: #6B6B82;
  line-height: 1.65;
  margin: 0;
}

/* ============================================
   WHY
   ============================================ */
.why-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.why-card {
  padding: 28px;
  background: #FAFAF9;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-lg);
}
.why-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background: #F0ECFE;
  color: #7C3AED;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-bottom: 16px;
}
.why-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: #15152A;
  margin: 0 0 8px;
}
.why-desc {
  font-size: var(--text-xs);
  color: #6B6B82;
  line-height: 1.65;
  margin: 0;
}

/* ============================================
   CTA COMPACT
   ============================================ */
.cta-compact {
  padding: 48px 0;
  background: #FFFFFF;
  border-top: 1px solid #EDE9F6;
  border-bottom: 1px solid #EDE9F6;
}
.cta-compact-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.cta-heading {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: #15152A;
  margin: 0 0 4px;
}
.cta-sub {
  font-size: var(--text-sm);
  color: #6B6B82;
  margin: 0;
}
.cta-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}
.btn-cta-primary {
  padding: 10px 24px;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: #fff;
  background: #7C3AED;
  border-radius: var(--radius-md);
  transition: background 120ms ease;
  white-space: nowrap;
}
.btn-cta-primary:hover { background: #6D28D9; }
.btn-cta-outline {
  padding: 10px 24px;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: #6B6B82;
  background: #FFFFFF;
  border: 1px solid #EDE9F6;
  border-radius: var(--radius-md);
  transition: all 120ms ease;
  white-space: nowrap;
}
.btn-cta-outline:hover {
  border-color: #C4B5FD;
  color: #15152A;
}

/* ============================================
   FOOTER
   ============================================ */
.footer {
  background: #15152A;
  color: #A0A0B8;
  padding: 60px 0 0;
}
.footer-top {
  display: grid;
  grid-template-columns: 1.2fr 3fr;
  gap: 48px;
  padding-bottom: 44px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  color: #fff;
  margin-bottom: 14px;
}
.footer-brand .brand-icon { color: #A78BFA; }
.footer-about {
  font-size: var(--text-xs);
  color: #A0A0B8;
  line-height: 1.65;
  margin: 0;
  max-width: 300px;
}
.footer-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}
.footer-col { display: flex; flex-direction: column; gap: 8px; }
.footer-col-title {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: #fff;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin: 0 0 4px;
}
.footer-col a {
  font-size: var(--text-xs);
  color: #A0A0B8;
  transition: color 120ms ease;
}
.footer-col a:hover { color: #fff; }
.footer-bottom {
  display: flex;
  justify-content: space-between;
  padding: 20px 0;
  font-size: 11px;
  color: #6B6B82;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .cat-grid { grid-template-columns: repeat(3, 1fr); }
  .drive-list { grid-template-columns: repeat(2, 1fr); }
  .company-rail { grid-template-columns: repeat(3, 1fr); }
  .featured-grid { grid-template-columns: repeat(2, 1fr); }
  .college-rail { grid-template-columns: repeat(5, 1fr); }
}

@media (max-width: 768px) {
  .header-nav { display: none; }
  .header-nav.open {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 56px;
    left: 0;
    right: 0;
    background: #FFFFFF;
    border-bottom: 1px solid #EDE9F6;
    padding: 12px 32px;
    gap: 4px;
    z-index: 99;
  }
  .mobile-toggle { display: block; }
  .header-right .btn-header-text { display: none; }

  .hero { padding: 56px 24px 48px; }
  .hero-title { font-size: 1.6rem; }

  .section { padding: 48px 0; }
  .section-title { font-size: var(--text-lg); }
  .section-head { flex-direction: column; align-items: flex-start; gap: 8px; }

  .cat-grid { grid-template-columns: repeat(2, 1fr); }
  .drive-list { grid-template-columns: 1fr; }
  .company-rail { grid-template-columns: repeat(2, 1fr); }
  .featured-grid { grid-template-columns: 1fr; }
  .college-rail { grid-template-columns: repeat(2, 1fr); }
  .steps { grid-template-columns: repeat(2, 1fr); }
  .step-card:not(:last-child)::after { display: none; }
  .why-grid { grid-template-columns: repeat(2, 1fr); }

  .roles-carousel-wrap { gap: 8px; }
  .carousel-arrow { width: 32px; height: 32px; }
  .role-card { flex: 0 0 200px; }

  .cta-compact-inner {
    flex-direction: column;
    text-align: center;
  }
  .cta-actions { width: 100%; justify-content: center; }

  .footer-top { grid-template-columns: 1fr; gap: 32px; }
  .footer-links { grid-template-columns: repeat(2, 1fr); }
  .footer-bottom { flex-direction: column; gap: 4px; text-align: center; }
}

@media (max-width: 480px) {
  .container { padding: 0 20px; }
  .hero-title { font-size: 1.35rem; }
  .cat-grid { grid-template-columns: 1fr; }
  .company-rail { grid-template-columns: 1fr; }
  .college-rail { grid-template-columns: 1fr; }
  .steps { grid-template-columns: 1fr; }
  .why-grid { grid-template-columns: 1fr; }
  .footer-links { grid-template-columns: 1fr; }
  .cta-actions { flex-direction: column; }
  .btn-cta-primary, .btn-cta-outline { width: 100%; text-align: center; }
  .role-card { flex: 0 0 160px; }
}
</style>
