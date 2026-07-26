// Jahan bhi ye app khula hai (localhost ho ya production URL), wahi ka
// origin use karta hai — isse deploy karte waqt is line ko badalna nahi padta.
const API = window.location.origin + '/api';

let currentFile = null;
let bulkFiles = [];
let allRecords = [];
let chartTypes = null;
let chartStatus = null;
let progTimer = null;

/* ==========================================================
   AUTHENTICATION
========================================================== */

const authContainer = document.getElementById("authContainer");
const mainApp = document.getElementById("mainApp");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");
const showForgotPassword = document.getElementById("showForgotPassword");
const backToLoginFromForgot = document.getElementById("backToLoginFromForgot");

const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");
const forgotSendBtn = document.getElementById("forgotSendBtn");
const forgotVerifyBtn = document.getElementById("forgotVerifyBtn");
const forgotResetBtn = document.getElementById("forgotResetBtn");

const togglePassword = document.getElementById("togglePassword");
let currentUser = null;
let forgotEmailValue = "";
let forgotOtpValue = "";

function goToForgotStep(stepNum) {
    document.getElementById('forgotStep1').classList.toggle('active', stepNum === 1);
    document.getElementById('forgotStep2').classList.toggle('active', stepNum === 2);
    document.getElementById('forgotStep3').classList.toggle('active', stepNum === 3);
}

forgotSendBtn.onclick = async function () {
    const email = document.getElementById("forgotEmail").value.trim();
    if (!email) {
        showForgotMessage("Enter your email address.", "err");
        return;
    }

    forgotSendBtn.disabled = true;
    try {
        const res = await fetch(`${API}/auth/forgot-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });
        const data = await safeJson(res);

        if (!res.ok || !data.success) {
            showForgotMessage(data.detail || data.message || "Could not send OTP.", "err");
            return;
        }

        forgotEmailValue = email;
        showForgotMessage(data.message || "OTP sent.", "ok");
        goToForgotStep(2);
    } catch (e) {
        showForgotMessage("Request failed: " + e.message, "err");
    } finally {
        forgotSendBtn.disabled = false;
    }
};

forgotVerifyBtn.onclick = async function () {
    const otp = document.getElementById("forgotOtp").value.trim();
    if (!otp) {
        showForgotMessage("Enter the OTP.", "err");
        return;
    }

    forgotVerifyBtn.disabled = true;
    try {
        const res = await fetch(`${API}/auth/verify-otp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: forgotEmailValue, otp })
        });
        const data = await safeJson(res);

        if (!res.ok || !data.success) {
            showForgotMessage(data.detail || data.message || "Invalid or expired OTP.", "err");
            return;
        }

        forgotOtpValue = otp;
        showForgotMessage(data.message || "OTP verified.", "ok");
        goToForgotStep(3);
    } catch (e) {
        showForgotMessage("Request failed: " + e.message, "err");
    } finally {
        forgotVerifyBtn.disabled = false;
    }
};

forgotResetBtn.onclick = async function () {
    const newPassword = document.getElementById("forgotNewPassword").value;
    const confirmPassword = document.getElementById("forgotConfirmPassword").value;

    if (!newPassword || !confirmPassword) {
        showForgotMessage("Fill both password fields.", "err");
        return;
    }
    if (newPassword !== confirmPassword) {
        showForgotMessage("Passwords do not match.", "err");
        return;
    }

    forgotResetBtn.disabled = true;
    try {
        const res = await fetch(`${API}/auth/reset-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: forgotEmailValue,
                otp: forgotOtpValue,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });
        const data = await safeJson(res);

        if (!res.ok || !data.success) {
            showForgotMessage(data.detail || data.message || "Reset failed.", "err");
            return;
        }

        showForgotMessage("Password reset. You can log in now.", "ok");
        setTimeout(() => {
            document.getElementById("forgotPasswordForm").style.display = "none";
            loginForm.style.display = "block";
            resetForgotFlow();
        }, 1200);
    } catch (e) {
        showForgotMessage("Request failed: " + e.message, "err");
    } finally {
        forgotResetBtn.disabled = false;
    }
};
let activeUploadStatusTimer = null;
let activeUploadPdfId = null;

/* ---------- Switch Forms ---------- */

showRegister.onclick = function(e){
    e.preventDefault();
    loginForm.style.display="none";
    registerForm.style.display="block";
    document.getElementById("forgotPasswordForm").style.display="none";
}

showLogin.onclick = function(e){
    e.preventDefault();
    registerForm.style.display="none";
    loginForm.style.display="block";
    document.getElementById("forgotPasswordForm").style.display="none";
}

showForgotPassword.onclick = function(e){
    e.preventDefault();
    loginForm.style.display="none";
    registerForm.style.display="none";
    document.getElementById("forgotPasswordForm").style.display="block";
    resetForgotFlow();
}

backToLoginFromForgot.onclick = function(e){
    e.preventDefault();
    document.getElementById("forgotPasswordForm").style.display="none";
    loginForm.style.display="block";
    registerForm.style.display="none";
}

/* ---------- Show Password ---------- */

togglePassword.onclick=function(){

    const input=document.getElementById("loginPassword");

    if(input.type==="password"){

        input.type="text";

    }else{

        input.type="password";

    }

}

function updateNavVisibility(){
    const adminNav = document.getElementById('adminNav');
    if (adminNav) {
        adminNav.style.display = currentUser?.role === 'admin' ? 'flex' : 'none';
    }
}

function showForgotMessage(msg, type){
    const el = document.getElementById('forgotMsg');
    el.className = 'alert show ' + type;
    el.textContent = msg;
}

function resetForgotFlow(){
    document.getElementById('forgotStep1').classList.add('active');
    document.getElementById('forgotStep2').classList.remove('active');
    document.getElementById('forgotStep3').classList.remove('active');
    document.getElementById('forgotEmail').value = '';
    document.getElementById('forgotOtp').value = '';
    document.getElementById('forgotNewPassword').value = '';
    document.getElementById('forgotConfirmPassword').value = '';
    document.getElementById('forgotMsg').className = 'alert';
    forgotEmailValue = '';
}

async function checkLogin(){
    const token = localStorage.getItem("token");
    if(token){
        try {
            const res = await fetch(`${API}/auth/me`, { headers: authHeader() });
            if(!res.ok) throw new Error("Token invalid");
            currentUser = JSON.parse(localStorage.getItem("user") || "{}");
            if(currentUser.name){
                document.getElementById("welcomeUser").innerHTML = "👋 " + currentUser.name;
            }
            updateNavVisibility();
            authContainer.style.display = "none";
            mainApp.style.display = "block";
            nav(currentUser.role === 'admin' ? "admin" : "dashboard");
            loadDashboard();
            loadAllRecords();
        } catch {
            logout();
        }
    } else {
        authContainer.style.display = "flex";
        mainApp.style.display = "none";
    }
}

function logout(){
    if(!confirm("Do you want to log out?")){
        return;
    }
    currentUser = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    authContainer.style.display = "flex";
    mainApp.style.display = "none";
    loginForm.style.display = "block";
    registerForm.style.display = "none";
    document.getElementById("loginEmail").value = "";
    document.getElementById("loginPassword").value = "";
    document.getElementById("captchaAnswer").value = "";
    generateCaptcha();
    document.getElementById("welcomeUser").innerHTML = "Welcome";
}

function authHeader(){
    const token = localStorage.getItem("token");
    return {
        "Authorization": "Bearer " + token
    };
}

async function safeJson(res) {
    const text = await res.text();
    try {
        return JSON.parse(text);
    } catch {
        throw new Error("Server ne invalid response diya: " + text.slice(0, 100));
    }
}

/* ==========================================================
   CAPTCHA
========================================================== */

let captchaA = 0;
let captchaB = 0;

function generateCaptcha(){
    captchaA = Math.floor(Math.random()*10)+1;
    captchaB = Math.floor(Math.random()*10)+1;
    document.getElementById("captchaQuestion").innerHTML = `${captchaA} + ${captchaB} = ?`;
    document.getElementById("registerCaptcha").innerHTML = `${captchaA} + ${captchaB} = ?`;
}

document.getElementById("refreshCaptcha").onclick = generateCaptcha;

checkLogin();



registerBtn.onclick = async function () {

    const full_name = document.getElementById("regName").value.trim();
     // Full Name Validation
    const nameRegex = /^[A-Za-z.' -]+$/;

    if (!nameRegex.test(full_name)) {

        alert("Enter a valid Full Name.");

        return;

    }
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value.trim();
    const confirm = document.getElementById("regConfirm").value.trim();

    if (!full_name || !email || !password || !confirm) {

        alert("Please fill all fields.");
        return;

    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(!emailRegex.test(email)){
        alert("Please enter a valid email address.");
        return;
    }

    // if (password.length < 8) {

    //     alert("Password must be at least 8 characters.");
    //     return;

    // }

    // if (password.length > 72) {

    //     alert("Password 72 characters se lamba nahi ho sakta.");
    //     return;

    // }



    // ==========================================
// Strong Password Validation
// ==========================================

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&^#])[A-Za-z\d@$!%*?&^#]{8,64}$/;
    if (!passwordRegex.test(password)) {

        alert(
            "Password must contain:\n\n" +
            "• At least 8 characters\n" +
            "• One uppercase letter\n" +
            "• One lowercase letter\n" +
            "• One number\n" +
            "• One special character"
        );

        return;

    }


    if (password !== confirm) {

        alert("Passwords do not match.");
        return;

    }

    const regCaptcha = Number(document.getElementById("registerCaptchaAnswer").value);
    if(regCaptcha !== (captchaA + captchaB)){
        alert("Captcha Wrong");
        generateCaptcha();
        return;
    }

    try {

        const res = await fetch(`${API}/auth/register`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                full_name,
                email,
                password

            })

        });

        const data = await safeJson(res);

        if (!res.ok) {
            alert(data.detail || "Registration failed. Please check your details.");
            return;
        }

        if (data.success) {

            alert(data.message);

            document.getElementById("regName").value = "";
            document.getElementById("regEmail").value = "";
            document.getElementById("regPassword").value = "";
            document.getElementById("regConfirm").value = "";
            document.getElementById("registerCaptchaAnswer").value = "";
            generateCaptcha();

            registerForm.style.display = "none";
            loginForm.style.display = "block";

        } else {

            alert(data.message);

        }

    } catch (err) {

        alert("Registration Failed");

        console.error(err);

    }

};



/* ==========================================================
   LOGIN USER
========================================================== */

loginBtn.onclick = async function () {

    const email =
        document.getElementById("loginEmail").value.trim();

    const password =
        document.getElementById("loginPassword").value.trim();

    if (!email || !password) {

        alert("Enter Email and Password");

        return;

    }

    const loginCaptcha = Number(document.getElementById("captchaAnswer").value);
    if(loginCaptcha !== (captchaA + captchaB)){
        alert("Captcha Wrong");
        generateCaptcha();
        document.getElementById("captchaAnswer").value = "";
        return;
    }

    try {

        const res = await fetch(`${API}/auth/login`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                email,
                password

            })

        });

        const data = await safeJson(res);

        if (!data.success) {

            alert(data.message);

            return;

        }

        // Save JWT
        localStorage.setItem(
            "token",
            data.access_token
        );

        currentUser = {
            name: data.user.name,
            role: data.user.role,
            user_id: data.user.id
        };

        localStorage.setItem(
            "user",
            JSON.stringify(currentUser)
        );

        document.getElementById("welcomeUser").innerHTML =
            "👋 " + data.user.name;
        updateNavVisibility();

        generateCaptcha();
        document.getElementById("captchaAnswer").value = "";

        // Hide Login
        authContainer.style.display = "none";

        // Show Dashboard
        mainApp.style.display = "block";

        // Load Dashboard — Admin ko seedha Admin panel dikhao, normal user ko Dashboard
        if (currentUser.role === 'admin') {
            nav("admin");
        } else {
            nav("dashboard");
        }

        loadDashboard();

        loadAllRecords();

        alert("Welcome " + data.user.name);

    }

    catch (err) {

        console.error(err);

        alert("Login Failed");

    }

};



generateCaptcha();

// ── NAV ──
function nav(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('v-' + name).classList.add('active');
  const names = ['dashboard','upload','bulk','results','records','pdfs','search','profile','admin','rejected','settings'];
  if(name==="rejected")
    loadRejectedPDFs();
  if (name === 'profile') loadProfile();
  if (name === 'admin') loadAdminOverview();
  if (name === 'settings') loadSettings();
  document.querySelectorAll('.nav-btn')[names.indexOf(name)].classList.add('active');
  if (name === 'pdfs') loadPDFList();
  if (name === 'records')
    loadAllRecords();
  if (name === 'dashboard') loadDashboard();
}

// ── DASHBOARD ──
async function loadDashboard() {
  try {
    const res = await fetch(`${API}/stats`,{

    headers:authHeader()

});
    const data = await safeJson(res);

    document.getElementById('d-pdfs').textContent = data.total_pdfs || 0;
    document.getElementById('d-pages').textContent = data.total_pages || 0;
    document.getElementById('d-records').textContent = data.total_records || 0;
    document.getElementById('d-completed').textContent = data.completed || 0;

    // Content type chart
    const types = data.content_types || {};
    const typeLabels = Object.keys(types);
    const typeData = Object.values(types);
    const typeColors = ['#1a56db','#0d7a55','#c0392b','#e65100','#7b1fa2'];

    if (chartTypes) chartTypes.destroy();
    const ctx1 = document.getElementById('chartTypes').getContext('2d');
    chartTypes = new Chart(ctx1, {
      type: 'doughnut',
      data: {
        labels: typeLabels.length ? typeLabels : ['No data'],
        datasets: [{ data: typeData.length ? typeData : [1], backgroundColor: typeColors, borderWidth: 0 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { family: 'IBM Plex Mono', size: 11 }, padding: 12 } } } }
    });

    // Status chart
    if (chartStatus) chartStatus.destroy();
    const ctx2 = document.getElementById('chartStatus').getContext('2d');
    chartStatus = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: ['Completed', 'Failed', 'Processing'],
        datasets: [{
          data: [data.completed || 0, data.failed || 0, (data.total_pdfs - data.completed - data.failed) || 0],
          backgroundColor: ['#0d7a55', '#c0392b', '#1a56db'],
          borderRadius: 4, borderWidth: 0
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { font: { family: 'IBM Plex Mono', size: 10 } } }, x: { ticks: { font: { family: 'IBM Plex Mono', size: 10 } } } }
      }
    });

    // Recent uploads
    const recent = data.recent_uploads || [];
    if (recent.length === 0) {
      document.getElementById('recentList').innerHTML = '<div class="empty"><div class="empty-ico">⬛</div><div class="empty-ttl">No uploads yet</div></div>';
    } else {
      document.getElementById('recentList').innerHTML = recent.map((r, i) => `
        <div class="recent-row">
          <span class="recent-num">${i+1}</span>
          <span class="recent-name">${escHtml(r.file_name)}</span>
          <span class="recent-pages">${r.pages}p</span>
          <span class="status-badge sb-${r.status}">${r.status}</span>
          <button class="btn btn-outline btn-sm" onclick="openPDF(${r.id},'${escHtml(r.file_name)}')">View</button>
        </div>`).join('');
    }

    document.getElementById('nc-pdfs').textContent = data.total_pdfs || 0;

  } catch(e) {
    console.error('Dashboard load failed:', e);
  }
}

// ── SINGLE UPLOAD ──
document.getElementById('fileInput').addEventListener('change', e => {
  if (e.target.files[0]) pickFile(e.target.files[0]);
});

const dz = document.getElementById('dropZone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('over'); });
dz.addEventListener('dragleave', () => dz.classList.remove('over'));
dz.addEventListener('drop', e => {
  e.preventDefault(); dz.classList.remove('over');
  const f = e.dataTransfer.files[0];
  if (f && f.name.endsWith('.pdf')) pickFile(f);
  else showAlert('uploadAlert','err','Only PDF files are accepted.');
});

function pickFile(file) {
  currentFile = file;
  document.getElementById('chipName').textContent = file.name;
  document.getElementById('chipMeta').textContent = fmtSize(file.size) + ' · PDF';
  document.getElementById('fileChip').classList.add('show');
  document.getElementById('actionRow').style.display = 'flex';
  document.getElementById('uploadAlert').classList.remove('show');
  document.getElementById('inlineResults').classList.remove('show');
  document.getElementById('inlineResults').innerHTML = '';
}

function clearFile() {
  currentFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('fileChip').classList.remove('show');
  document.getElementById('actionRow').style.display = 'none';
  document.getElementById('progWrap').classList.remove('show');
  document.getElementById('uploadAlert').classList.remove('show');
}

async function doExtract() {
  if (!currentFile) return;
  const btn = document.getElementById('extractBtn');
  btn.disabled = true; btn.textContent = 'Extracting...';
  document.getElementById('progWrap').classList.add('show');
  document.getElementById('uploadAlert').classList.remove('show');
  updateStatusUI({ status: 'processing', progress: 5, processing_message: 'Uploading PDF' });

  const fd = new FormData();
  fd.append('file', currentFile);

  try {
   const res = await fetch(`${API}/upload`,{

    method:'POST',

    headers:authHeader(),

    body:fd

});
    const data = await safeJson(res);
    if (!res.ok) throw new Error(data.detail || 'Failed');

    if (data.pdf_id) {
      activeUploadPdfId = data.pdf_id;
      pollUploadStatus(data.pdf_id);
    }

    document.getElementById('nc-results').textContent = data.total_pages || 0;

    showAlert('uploadAlert','ok',`✓ ${data.file || currentFile.name} accepted for background processing.`);
    loadDashboard();

  } catch(err) {
    document.getElementById('progWrap').classList.remove('show');
    showAlert('uploadAlert','err','Error: ' + err.message);
  } finally {
    btn.disabled = false; btn.textContent = '⚡ Extract Content';
  }
}

// ── BULK UPLOAD ──
document.getElementById('bulkInput').addEventListener('change', e => {
  const files = Array.from(e.target.files).filter(f => f.name.endsWith('.pdf'));
  if (files.length) setBulkFiles(files);
});

const bdz = document.getElementById('bulkDropZone');
bdz.addEventListener('dragover', e => { e.preventDefault(); bdz.classList.add('over'); });
bdz.addEventListener('dragleave', () => bdz.classList.remove('over'));
bdz.addEventListener('drop', e => {
  e.preventDefault(); bdz.classList.remove('over');
  const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
  if (files.length) setBulkFiles(files);
});

function setBulkFiles(files) {
  bulkFiles = files;
  renderBulkQueue(files.map(f => ({ name: f.name, size: fmtSize(f.size), status: 'pending' })));
  document.getElementById('bulkActionRow').style.display = 'flex';
}

function renderBulkQueue(items) {
  document.getElementById('bulkQueue').innerHTML = items.map((f, i) => `
    <div class="queue-item" id="qi-${i}">
      <span style="font-size:14px;">📄</span>
      <span class="queue-item-name">${escHtml(f.name)}</span>
      <span style="font-family:var(--mono);font-size:11px;color:var(--ink-3);">${f.size}</span>
      <span class="queue-status qs-${f.status}">${f.status}</span>
    </div>`).join('');
}

function clearBulk() {
  bulkFiles = [];
  document.getElementById('bulkInput').value = '';
  document.getElementById('bulkQueue').innerHTML = '';
  document.getElementById('bulkActionRow').style.display = 'none';
  document.getElementById('bulkProgWrap').classList.remove('show');
  document.getElementById('bulkAlert').classList.remove('show');
}

async function doBulkExtract() {
  if (bulkFiles.length === 0) return;
  const btn = document.getElementById('bulkExtractBtn');
  btn.disabled = true; btn.textContent = 'Processing...';
  document.getElementById('bulkProgWrap').classList.add('show');

  let done = 0;
  const queueItems = bulkFiles.map(f => ({ name: f.name, size: fmtSize(f.size), status: 'pending' }));

  for (let i = 0; i < bulkFiles.length; i++) {
    queueItems[i].status = 'processing';
    renderBulkQueue(queueItems);

    const fd = new FormData();
    fd.append('file', bulkFiles[i]);

    try {
      const res = await fetch(`${API}/upload`,{

    method:'POST',

    headers:authHeader(),

    body:fd

});
      const data = await safeJson(res);
      if (!res.ok) throw new Error(data.detail);

      queueItems[i].status = 'done';
      done++;

      if (data.results) {
        data.results.forEach(page => {
          allRecords.push({
            file: bulkFiles[i].name, page: page.page_number,
            type: page.content_type, tables: page.tables || [],
            text: page.text || '', images: page.images || [],
            pdfId: data.pdf_id
          });
        });
      }

    } catch(e) {
      queueItems[i].status = 'failed';
    }

    renderBulkQueue(queueItems);
    const pct = Math.round(((i+1) / bulkFiles.length) * 100);
    document.getElementById('bulkProgFill').style.width = pct + '%';
    document.getElementById('bulkProgPct').textContent = pct + '%';
    document.getElementById('bulkProgLabel').textContent = `Processing ${i+1} of ${bulkFiles.length}...`;
  }

  document.getElementById('nc-records').textContent = allRecords.length;
  showAlert('bulkAlert','ok',`✓ ${done} of ${bulkFiles.length} PDFs processed successfully.`);
  btn.disabled = false; btn.textContent = '⚡ Extract All';
  loadDashboard();
}

// ── RESULTS HTML ──
function buildResultsHTML(data) {
  if (!data.results || data.results.length === 0) return '<div class="empty"><div class="empty-ico">◧</div><div class="empty-ttl">Nothing extracted</div></div>';

  return data.results.map(page => {
    const typeClass = 'type-' + (page.content_type || 'mixed');
    let body = '';

    if (page.tables && page.tables.length > 0) {
      page.tables.forEach((tbl, ti) => {
        body += `<div class="${ti>0?'sec-gap':''}"><div class="sec-label">Table${page.tables.length>1?' '+(ti+1):''}</div>
          <div class="data-tbl-wrap"><table class="data-tbl">`;
        if (tbl.headers?.length) body += `<thead><tr>${tbl.headers.map(h=>`<th>${h||'—'}</th>`).join('')}</tr></thead>`;
        if (tbl.rows?.length) body += `<tbody>${tbl.rows.map(row=>`<tr>${row.map(c=>`<td>${c||'—'}</td>`).join('')}</tr>`).join('')}</tbody>`;
        body += `</table></div></div>`;
      });
    }

    if (page.text?.trim()) {
      body += `<div class="sec-gap"><div class="sec-label">Text</div><div class="text-block">${escHtml(page.text.trim())}</div></div>`;
    }

    if (page.images?.length) {
      body += `<div class="sec-gap"><div class="sec-label">Images Detected</div><div class="img-list">
        ${page.images.map((img,i)=>`<div class="img-item"><span class="img-num">${i+1}</span><span>${escHtml(img)}</span></div>`).join('')}
      </div></div>`;
    }

    if (!body) body = '<div style="color:var(--ink-3);font-size:13px;">No extractable content on this page.</div>';

    return `<div class="page-block">
      <div class="page-block-head">
        <span class="page-num">Page ${page.page_number}</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <span class="type-tag ${typeClass}">${page.content_type||'mixed'}</span>
          <button class="btn btn-outline btn-sm" onclick="openPDF(${data.pdf_id},'${escHtml(data.file||'')}')">📄 View PDF</button>
        </div>
      </div>
      <div class="page-block-body">${body}</div>
    </div>`;
  }).join('');
}


// =====================================================
// LOAD ALL RECORDS FROM DATABASE
// =====================================================
// Ye function PostgreSQL se saare extracted
// records fetch karta hai.
//
// Backend API:
// GET /api/records
//
// Response Example:
// {
//   total: 7,
//   records: [...]
// }
//
// Frontend format me convert karke
// allRecords array me save karta hai.
// =====================================================

async function loadAllRecords() {

  try {

    // API call
    const res = await fetch(`${API}/records`,{

    headers:authHeader()

});

    // JSON response
    const data = await safeJson(res);

    // Backend response ko frontend format me convert karo
    allRecords = (data.records || []).map(r => ({

      // PDF file name
      file: r.file_name,

      // Page number
      page: r.page_number,

      // Content type
      type: r.content_type,

      // Extracted tables
      tables: r.data?.tables || [],

      // Extracted text
      text: r.data?.text || '',

      // Extracted images
      images: r.data?.images || [],

      // PDF id (View PDF ke liye)
      pdfId: r.pdf_id

    }));

    // Sidebar record count update karo
    document.getElementById('nc-records')
      .textContent = allRecords.length;

    // Table render karo
    renderRecordsTable();

    console.log(
      `Loaded ${allRecords.length} records from database`
    );

  } catch (e) {

    console.error(
      'Failed to load records:',
      e
    );

  }
}
// ── RECORDS TABLE ──
function renderRecordsTable() {
  const q = document.getElementById('recordSearch')?.value?.toLowerCase() || '';
  const filtered = q ? allRecords.filter(r =>
    r.file.toLowerCase().includes(q) || r.type.toLowerCase().includes(q) || r.text.toLowerCase().includes(q)
  ) : allRecords;

  if (filtered.length === 0) {
    document.getElementById('recordsTable').innerHTML = `<div class="empty"><div class="empty-ico">⊞</div><div class="empty-ttl">No records</div><div class="empty-txt">Upload a PDF to see records.</div></div>`;
    return;
  }

  document.getElementById('recordsTable').innerHTML = `<div class="data-tbl-wrap">
    <table class="data-tbl">
      <thead><tr><th>#</th><th>File</th><th>Page</th><th>Type</th><th>Tables</th><th>Text Preview</th><th>Images</th><th>View</th></tr></thead>
      <tbody>${filtered.map((r,i) => `<tr>
        <td style="color:var(--ink-3);font-family:var(--mono);font-size:11px;">${i+1}</td>
        <td style="font-weight:500;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escHtml(r.file)}">${escHtml(r.file)}</td>
        <td style="font-family:var(--mono);font-size:12px;">${r.page}</td>
        <td><span class="type-tag type-${r.type}">${r.type}</span></td>
        <td style="font-family:var(--mono);font-size:12px;">${r.tables.length}</td>
        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink-3);font-size:12px;">${escHtml(r.text.slice(0,80))}${r.text.length>80?'…':''}</td>
        <td style="font-family:var(--mono);font-size:12px;">${r.images.length}</td>
        <td><button class="btn btn-outline btn-sm" onclick="openPDF(${r.pdfId},'${escHtml(r.file)}')">📄</button></td>
      </tr>`).join('')}</tbody>
    </table>
  </div>`;
}

function filterRecords() { renderRecordsTable(); }

function clearRecords() {
  if (confirm('Clear all session records?')) {
    allRecords = [];
    renderRecordsTable();
    document.getElementById('nc-records').textContent = '0';
  }
}

// ── MANAGE PDFs ──
async function loadPDFList() {
  try {
    const res = await fetch(`${API}/masters`,{

    headers:authHeader()

});
    const data = await safeJson(res);
    const pdfs = data.pdfs || [];

    document.getElementById('nc-pdfs').textContent = pdfs.length;

    if (pdfs.length === 0) {
      document.getElementById('pdfList').innerHTML = '<div class="empty"><div class="empty-ico">📁</div><div class="empty-ttl">No PDFs yet</div></div>';
      return;
    }

    document.getElementById('pdfList').innerHTML = `<div style="padding:0 20px;">${pdfs.map(p => `
      <div class="pdf-row">
        <div class="pdf-icon">📄</div>
        <div class="pdf-info">
          <div class="pdf-name">${escHtml(p.file_name)}</div>
          <div class="pdf-meta">${fmtSize(p.file_size||0)} · ${p.total_pages} pages · ${new Date(p.uploaded_at).toLocaleString('en-IN')}</div>
        </div>
        <span class="status-badge sb-${p.status}">${p.status}</span>

        <div class="pdf-actions">

  <button class="btn btn-outline btn-sm"
    onclick="openPDF(${p.id},'${escHtml(p.file_name)}')">
    📄 View
  </button>

  <button class="btn btn-outline btn-sm"
    onclick="downloadPDF(${p.id},'${escHtml(p.file_name)}')">
    ⬇ Download
  </button>

  <button class="btn btn-danger btn-sm"
    onclick="deletePDF(${p.id},'${escHtml(p.file_name)}')">
    🗑 Delete
  </button>

</div>
      </div>`).join('')}
    </div>`;

  } catch(e) {
    document.getElementById('pdfList').innerHTML = '<div class="empty"><div class="empty-ico">⚠</div><div class="empty-ttl">Failed to load</div></div>';
  }
}

async function deletePDF(pdfId, fileName) {
  if (!confirm(`"${fileName}" and Do you want to delete all associated data?`)) return;

  try {
    const res = await fetch(

`${API}/pdf/${pdfId}`,

{

method:'DELETE',

headers:authHeader()

});
    if (!res.ok) throw new Error('Delete failed');
    loadPDFList();
    loadDashboard();
    // Session records se bhi hatao
    allRecords = allRecords.filter(r => r.pdfId !== pdfId);
    document.getElementById('nc-records').textContent = allRecords.length;
  } catch(e) {
    alert('Delete nahi hua: ' + e.message);
  }
}

// ── SEARCH ──
async function doSearch() {
  const q = document.getElementById('globalSearch').value.trim();
  if (!q) return;

  try {
    const res = await fetch(

`${API}/records?search=${encodeURIComponent(q)}`,

{

headers:authHeader()

}

);
    const data = await safeJson(res);
    const records = data.records || [];

    if (records.length === 0) {
      document.getElementById('searchResults').innerHTML = `<div class="empty"><div class="empty-ico">🔍</div><div class="empty-ttl">No results for "${escHtml(q)}"</div></div>`;
      return;
    }

    document.getElementById('searchResults').innerHTML = `
      <div style="font-family:var(--mono);font-size:11px;color:var(--ink-3);margin-bottom:12px;">${records.length} result(s) found for "${escHtml(q)}"</div>
      <div class="data-tbl-wrap"><table class="data-tbl">
        <thead><tr><th>File</th><th>Page</th><th>Type</th><th>Text Match</th><th>View</th></tr></thead>
        <tbody>${records.map(r => {
          const text = r.data?.text || '';
          const idx = text.toLowerCase().indexOf(q.toLowerCase());
          const preview = idx >= 0
            ? escHtml(text.slice(Math.max(0,idx-40), idx)) + `<span class="hl">${escHtml(text.slice(idx, idx+q.length))}</span>` + escHtml(text.slice(idx+q.length, idx+q.length+60))
            : escHtml(text.slice(0,100));
          return `<tr>
            <td style="font-weight:500;">${escHtml(r.file_name)}</td>
            <td style="font-family:var(--mono);font-size:12px;">${r.page_number}</td>
            <td><span class="type-tag type-${r.content_type}">${r.content_type}</span></td>
            <td style="font-size:12px;max-width:300px;">${preview}…</td>
            <td><button class="btn btn-outline btn-sm" onclick="openPDF(${r.pdf_id},'${escHtml(r.file_name)}')">📄</button></td>
          </tr>`;
        }).join('')}</tbody>
      </table></div>`;

  } catch(e) {
    document.getElementById('searchResults').innerHTML = `<div class="empty"><div class="empty-ico">⚠</div><div class="empty-ttl">Search failed</div><div class="empty-txt">${e.message}</div></div>`;
  }
}

document.getElementById('globalSearch').addEventListener('keydown', e => {
  if (e.key === 'Enter') doSearch();
});

// ── EXPORT ──
async function exportExcel() {
  try {
    const res = await fetch(`${API}/export/excel`, { headers: authHeader() });
    if (!res.ok) throw new Error("Export failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "docscan_export.xlsx";
    a.click();
    URL.revokeObjectURL(url);
  } catch(e) {
    alert("Excel export failed: " + e.message);
  }
}

function exportCSV() {
  if (allRecords.length === 0) return alert('No records to export.');
  const rows = [['File','Page','Type','Tables','Text Preview','Images']];
  allRecords.forEach(r => rows.push([r.file, r.page, r.type, r.tables.length, r.text.slice(0,200), r.images.length]));
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(',')).join('\n');
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(new Blob([csv],{type:'text/csv'})),
    download: 'docscan_' + Date.now() + '.csv'
  });
  a.click();
}

// ── PDF MODAL ──
async function downloadPDF(pdfId, fileName) {
  try {
    const res = await fetch(`${API}/pdf/${pdfId}`, { headers: authHeader() });
    if (!res.ok) throw new Error("Download failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
  } catch(e) {
    alert("Download failed: " + e.message);
  }
}

async function openPDF(pdfId, fileName) {
  if (!pdfId) return alert('PDF ID nahi mila.');
  document.getElementById('modalName').textContent = '📄 ' + fileName;
  try {
    const res = await fetch(`${API}/pdf/${pdfId}`, { headers: authHeader() });
    if (!res.ok) throw new Error("PDF load failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    document.getElementById('pdfFrame').src = url;
    document.getElementById('pdfModal').classList.add('show');
  } catch(e) {
    alert("PDF open nahi hua: " + e.message);
  }
}

function closeModal() {
  document.getElementById('pdfModal').classList.remove('show');
  document.getElementById('pdfFrame').src = '';
}

document.getElementById('pdfModal').addEventListener('click', e => {
  if (e.target === document.getElementById('pdfModal')) closeModal();
});

function updateStatusUI(data) {
  const status = (data.status || 'processing').toLowerCase();
  const progress = data.progress || 0;
  const message = data.processing_message || 'Processing';
  const stepEls = document.querySelectorAll('.status-step');
  if (stepEls.length) {
    stepEls.forEach((el) => el.classList.remove('active','done','failed'));
    if (status === 'failed') {
      stepEls.forEach((el) => el.classList.add('failed'));
    } else if (status === 'completed') {
      stepEls.forEach((el) => el.classList.add('done'));
    } else {
      const activeIndex = progress < 10 ? 0 : progress < 40 ? 1 : progress < 80 ? 2 : 2;
      stepEls.forEach((el, index) => {
        if (index < activeIndex) el.classList.add('done');
        if (index === activeIndex) el.classList.add('active');
      });
    }
  }
  const label = document.getElementById('progLabel');
  const pct = document.getElementById('progPct');
  const fill = document.getElementById('progFill');
  const text = document.getElementById('uploadStatusText');
  if (label) label.textContent = message;
  if (pct) pct.textContent = `${progress}%`;
  if (fill) fill.style.width = `${progress}%`;
  if (text) text.textContent = message;
}

async function pollUploadStatus(pdfId) {
  if (!pdfId) return;
  try {
    const res = await fetch(`${API}/upload/status/${pdfId}`, { headers: authHeader() });
    const data = await safeJson(res);
    if (!res.ok) throw new Error(data.detail || 'Status unavailable');
    updateStatusUI(data);

    if (data.status === 'completed') {

      clearTimeout(activeUploadStatusTimer);

      await loadAllRecords();

      const pageResults = allRecords
        .filter(r => r.pdfId === pdfId)
        .map(r => ({
          page_number: r.page,
          content_type: r.type,
          tables: r.tables,
          text: r.text,
          images: r.images
        }));

      const html = buildResultsHTML({
        results: pageResults,
        pdf_id: pdfId,
        file: currentFile ? currentFile.name : ''
      });

      document.getElementById('inlineResults').innerHTML = html;
      document.getElementById('inlineResults').classList.add('show');
      document.getElementById('resultsContent').innerHTML = html;

      loadDashboard();
      return;
    }

    if (data.status !== 'completed' && data.status !== 'failed') {
      clearTimeout(activeUploadStatusTimer);
      activeUploadStatusTimer = setTimeout(() => pollUploadStatus(pdfId), 2000);
    }
  } catch (e) {
    console.error(e);
  }
}

function startProgress(fillId, labelId, pctId) {
  let p = 0;
  const labels = ['Reading PDF...','Converting pages...','Calling Gemini AI...','Saving to database...'];
  clearInterval(progTimer);
  progTimer = setInterval(() => {
    p = Math.min(p + Math.random() * 6, 88);
    document.getElementById(fillId).style.width = p + '%';
    document.getElementById(pctId).textContent = Math.round(p) + '%';
    document.getElementById(labelId).textContent = labels[Math.min(Math.floor(p/25),3)];
  }, 350);
}

function finishProgress(fillId, pctId, labelId) {
  clearInterval(progTimer);
  document.getElementById(fillId).style.width = '100%';
  document.getElementById(pctId).textContent = '100%';
  document.getElementById(labelId).textContent = 'Complete';
}


async function loadRejectedPDFs(){

    try{

        const res = await fetch(

             `${API}/rejected`,

{

headers:authHeader()

});

        const data = await safeJson(res);

        const rejected =
            data.rejected || [];

        document.getElementById(
            "nc-rejected"
        ).textContent = rejected.length;

        if(rejected.length===0){

            document.getElementById(
                "rejectedTable"
            ).innerHTML=

            `<div class="empty">

                <div class="empty-ico">

                    🚫

                </div>

                <div class="empty-ttl">

                    No rejected PDFs

                </div>

            </div>`;

            return;

        }

        document.getElementById(
            "rejectedTable"
        ).innerHTML=

        `<div class="data-tbl-wrap">

        <table class="data-tbl">

        <thead>

        <tr>

        <th>ID</th>

        <th>File</th>

        <th>Reason</th>

        <th>Owner</th>

        <th>Size</th>

        <th>Date</th>

        <th>Preview</th>

        </tr>

        </thead>

        <tbody>

        ${rejected.map(r=>`

        <tr>

        <td>${r.id}</td>

        <td>${r.file_name}</td>

        <td>

        <span class="type-tag type-image">

        ${r.reason}

        </span>

        </td>

        <td>${r.owner_email || '—'}</td>

        <td>${fmtSize(r.file_size)}</td>

        <td>${r.uploaded_at}</td>

        <td><button class="btn btn-outline btn-sm" onclick="openRejectedPDF(${r.id}, '${escHtml(r.file_name)}')">Preview</button></td>

        </tr>

        `).join("")}

        </tbody>

        </table>

        </div>`;

    }

    catch(e){

        console.log(e);

    }
}

async function openRejectedPDF(rejectedId, fileName) {
  document.getElementById('modalName').textContent = '📄 ' + fileName;
  try {
    const res = await fetch(`${API}/rejected/${rejectedId}/file`, { headers: authHeader() });
    if (!res.ok) throw new Error('PDF load failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    document.getElementById('pdfFrame').src = url;
    document.getElementById('pdfModal').classList.add('show');
  } catch (e) {
    alert('PDF open nahi hua: ' + e.message);
  }
}

async function loadProfile() {
  try {
    const res = await fetch(`${API}/auth/profile`, { headers: authHeader() });
    const data = await safeJson(res);
    const avatarEl = document.getElementById('profileAvatar');
    if (data.profile_image) {
      avatarEl.innerHTML = `<img src="${data.profile_image}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
    } else {
      avatarEl.textContent = (data.full_name || data.name || data.email || 'U').charAt(0).toUpperCase();
    }
    document.getElementById('profileName').textContent = data.full_name || data.name || '—';
    document.getElementById('profileEmail').textContent = data.email || '—';
    document.getElementById('profileRole').textContent = `Role: ${data.role || 'user'}`;
    document.getElementById('profileLastLogin').textContent = `Last login: ${data.last_login || 'never'}`;
    document.getElementById('editFullName').value = data.full_name || data.name || '';
  } catch (e) {
    console.error(e);
  }
}

document.getElementById('profilePhotoInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 1024 * 1024) {
    alert('The photo should be less than 1MB.');
    return;
  }

  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const res = await fetch(`${API}/auth/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ profile_image: reader.result })
      });
      const data = await safeJson(res);
      if (!res.ok || !data.success) {
        alert(data.detail || 'Photo update failed.');
        return;
      }
      loadProfile();
    } catch (err) {
      alert('Request failed: ' + err.message);
    }
  };
  reader.readAsDataURL(file);
});

async function saveProfileName() {
  const fullName = document.getElementById('editFullName').value.trim();
  const msgEl = document.getElementById('profileEditMsg');

  if (!fullName) {
    msgEl.className = 'alert show err';
    msgEl.textContent = 'Name cannot be empty.';
    return;
  }

  try {
    const res = await fetch(`${API}/auth/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ full_name: fullName })
    });
    const data = await safeJson(res);

    if (!res.ok || !data.success) {
      msgEl.className = 'alert show err';
      msgEl.textContent = data.detail || 'Update failed.';
      return;
    }

    msgEl.className = 'alert show ok';
    msgEl.textContent = 'Name updated.';
    document.getElementById('profileName').textContent = fullName;

    currentUser = { ...currentUser, name: fullName };
    localStorage.setItem('user', JSON.stringify(currentUser));
    document.getElementById('welcomeUser').innerHTML = '👋 ' + fullName;
  } catch (e) {
    msgEl.className = 'alert show err';
    msgEl.textContent = 'Request failed: ' + e.message;
  }
}

async function changePassword() {
  const current = document.getElementById('currentPassword').value;
  const next = document.getElementById('newPassword').value;
  const confirm = document.getElementById('confirmPassword').value;
  const el = document.getElementById('profileMsg');
  if (!current || !next || !confirm) {
    el.className = 'alert show err';
    el.textContent = 'Please fill all password fields.';
    return;
  }
  if (next !== confirm) {
    el.className = 'alert show err';
    el.textContent = 'New password and confirm password do not match.';
    return;
  }
  try {
    const res = await fetch(`${API}/auth/change-password`, {
      method: 'POST',
      headers: { ...authHeader(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: current, new_password: next, confirm_password: confirm })
    });
    const data = await safeJson(res);
    el.className = 'alert show ' + (data.success ? 'ok' : 'err');
    el.textContent = data.message || 'Password updated.';
  } catch (e) {
    el.className = 'alert show err';
    el.textContent = 'Password change failed.';
  }
}

async function toggleUserRole(userId, currentRole) {
  const newRole = currentRole === 'admin' ? 'user' : 'admin';
  if (!confirm(`Change this user's role to "${newRole}"?`)) return;

  try {
    const res = await fetch(`${API}/admin/users/${userId}/role`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ role: newRole })
    });
    const data = await safeJson(res);

    if (!res.ok || !data.success) {
      alert(data.detail || 'Role change failed.');
      return;
    }

    loadAdminOverview();
  } catch (e) {
    alert('Request failed: ' + e.message);
  }
}

async function toggleUserStatus(userId, isCurrentlyActive) {
  const action = isCurrentlyActive ? 'deactivate' : 'activate';
  if (!confirm(`Are you sure you want to ${action} this user?`)) return;

  try {
    const res = await fetch(`${API}/admin/users/${userId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ is_active: !isCurrentlyActive })
    });
    const data = await safeJson(res);

    if (!res.ok || !data.success) {
      alert(data.detail || 'Status change failed.');
      return;
    }

    loadAdminOverview();
  } catch (e) {
    alert('Request failed: ' + e.message);
  }
}

async function deleteUser(userId, email) {
  if (!confirm(`Delete user "${email}" permanently? Their uploaded PDFs will be kept but unowned. This cannot be undone.`)) return;

  try {
    const res = await fetch(`${API}/admin/users/${userId}`, {
      method: 'DELETE',
      headers: authHeader()
    });
    const data = await safeJson(res);

    if (!res.ok || !data.success) {
      alert(data.detail || 'Delete failed.');
      return;
    }

    loadAdminOverview();
  } catch (e) {
    alert('Request failed: ' + e.message);
  }
}

async function loadAdminOverview() {
  try {
    const res = await fetch(`${API}/admin/overview`, { headers: authHeader() });
    const data = await safeJson(res);
    document.getElementById('adminUsers').textContent = data.total_users || 0;
    document.getElementById('adminPdfs').textContent = data.total_pdfs || 0;
    document.getElementById('adminCompleted').textContent = data.completed || 0;
    document.getElementById('adminFailed').textContent = data.failed || 0;
  } catch (e) {
    console.error(e);
  }
  try {
    const res = await fetch(`${API}/admin/users`, { headers: authHeader() });
    const data = await safeJson(res);
    const users = data.users || [];
    const myId = currentUser?.user_id;
    document.getElementById('adminUsersList').innerHTML = users.length ? `<div class="data-tbl-wrap"><table class="data-tbl"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Login</th><th>Actions</th></tr></thead><tbody>${users.map(u => `
      <tr>
        <td>${escHtml(u.full_name)}</td>
        <td>${escHtml(u.email)}</td>
        <td>${u.role}</td>
        <td>${u.account_locked ? 'Locked' : (u.is_active ? 'Active' : 'Inactive')}</td>
        <td>${u.last_login || '—'}</td>
        <td>${u.id === myId ? '<span style="color:var(--muted,#888);font-size:12px;">You</span>' : `
          <button class="btn btn-outline btn-sm" onclick="toggleUserRole(${u.id}, '${u.role}')">${u.role === 'admin' ? 'Make User' : 'Make Admin'}</button>
          <button class="btn btn-outline btn-sm" onclick="toggleUserStatus(${u.id}, ${u.is_active})">${u.is_active ? 'Deactivate' : 'Activate'}</button>
          <button class="btn btn-outline btn-sm" style="color:var(--red);" onclick="deleteUser(${u.id}, '${escHtml(u.email)}')">Delete</button>
        `}</td>
      </tr>
    `).join('')}</tbody></table></div>` : '<div class="empty"><div class="empty-ttl">No users found</div></div>';
  } catch (e) {
    console.error(e);
  }
  try {
    const res = await fetch(`${API}/admin/audit-logs`, { headers: authHeader() });
    const data = await safeJson(res);
    const logs = data.logs || [];
    document.getElementById('adminAuditLogs').innerHTML = logs.length ? `<div class="data-tbl-wrap"><table class="data-tbl"><thead><tr><th>Date</th><th>User ID</th><th>Action</th><th>Details</th></tr></thead><tbody>${logs.slice(-50).reverse().map(log => `
      <tr>
        <td>${escHtml(log.timestamp || '—')}</td>
        <td>${escHtml(String(log.user_id || 'system'))}</td>
        <td>${escHtml(log.event || '—')}</td>
        <td>${escHtml(log.details || '—')}</td>
      </tr>
    `).join('')}</tbody></table></div>` : '<div class="empty"><div class="empty-ttl">No audit logs yet</div></div>';
  } catch (e) {
    console.error(e);
  }
  try {
    const res = await fetch(`${API}/rejected`, { headers: authHeader() });
    const data = await safeJson(res);
    const rejected = data.rejected || [];
    document.getElementById('adminRejectedList').innerHTML = rejected.length ? `<div class="data-tbl-wrap"><table class="data-tbl"><thead><tr><th>File</th><th>Reason</th><th>Size</th></tr></thead><tbody>${rejected.slice(0, 8).map(r => `<tr><td>${escHtml(r.file_name)}</td><td>${escHtml(r.reason)}</td><td>${fmtSize(r.file_size || 0)}</td></tr>`).join('')}</tbody></table></div>` : '<div class="empty"><div class="empty-ttl">No rejected PDFs</div></div>';
  } catch (e) {
    console.error(e);
  }
}

// ── HELPERS ──
function showAlert(id, type, msg) {
  const el = document.getElementById(id);
  el.className = 'alert show ' + type;
  el.textContent = msg;
}

function fmtSize(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  return (b/1048576).toFixed(1) + ' MB';
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── SETTINGS ──
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
  localStorage.setItem('theme', theme);
}

(function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

async function checkApiStatus() {
  const el = document.getElementById('apiStatusText');
  el.textContent = 'Checking...';
  try {
    const start = Date.now();
    const res = await fetch(`${API.replace('/api', '')}/health`);
    const ms = Date.now() - start;
    if (res.ok) {
      el.innerHTML = `<span style="color:var(--green);">● Online</span> — responded in ${ms}ms`;
    } else {
      el.innerHTML = `<span style="color:var(--red);">● Error</span> — status ${res.status}`;
    }
  } catch (e) {
    el.innerHTML = `<span style="color:var(--red);">● Offline</span> — ${e.message}`;
  }
}

async function logoutAllDevices() {
  if (!confirm('This will log you out of every device, including this one. Continue?')) return;
  try {
    const res = await fetch(`${API}/auth/logout-all`, { method: 'POST', headers: authHeader() });
    const data = await safeJson(res);
    if (!res.ok) {
      alert(data.detail || 'Logout failed.');
      return;
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    location.reload();
  } catch (e) {
    alert('Request failed: ' + e.message);
  }
}

function loadSettings() {
  checkApiStatus();
  const chunkCard = document.getElementById('adminChunkSizeCard');
  if (chunkCard) chunkCard.style.display = currentUser?.role === 'admin' ? 'block' : 'none';
}