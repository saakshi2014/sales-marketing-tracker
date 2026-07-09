// leads.js — Lead Management (Clean Single Version)

// ── STAGE COLOURS ─────────────────────────────────────────────────────────────
const LEADS_STAGE_COLORS = {
    "stage_1_1": { bg: "#E8F5E9", text: "#2E7D32" },
    "stage_1_2": { bg: "#FFEBEE", text: "#C62828" },
    "stage_2":   { bg: "#E3F2FD", text: "#1565C0" },
    "stage_2_1": { bg: "#E8EAF6", text: "#283593" },
    "stage_2_2": { bg: "#FFF3E0", text: "#E65100" },
    "stage_3":   { bg: "#F3E5F5", text: "#6A1B9A" },
    "stage_3_1": { bg: "#FAFAFA", text: "#616161" },
    "stage_4":   { bg: "#E0F7FA", text: "#00695C" },
    "stage_6_1": { bg: "#F9FBE7", text: "#558B2F" },
    "stage_6_2": { bg: "#FFEBEE", text: "#B71C1C" },
    "stage_6_3": { bg: "#FFF8E1", text: "#F57F17" },
    "stage_7":   { bg: "#E8F5E9", text: "#1B5E20" },
    "stage_8":   { bg: "#E0F2F1", text: "#004D40" },
};

// ── GLOBAL STATE ──────────────────────────────────────────────────────────────
let allLeads              = [];
let allStages             = [];
let currentPage           = 1;
const PER_PAGE            = 50;
let showArchived          = false;
let originalContactValues = {};


// ══════════════════════════════════════════════════════════════════════════════
// STAGES
// ══════════════════════════════════════════════════════════════════════════════
async function fetchStages() {
    try {
        const r = await fetch('/api/stages');
        const d = await r.json();
        if (r.ok) { allStages = d.stages; populateStageDropdowns(); }
    } catch (e) { console.error('fetchStages:', e); }
}

function populateStageDropdowns() {
    const sel = document.getElementById('addLeadStage');
    if (!sel) return;
    sel.innerHTML = '';
    allStages.forEach(s => {
        const o = document.createElement('option');
        o.value = s.stageId;
        o.textContent = `${s.stageNumber} — ${s.stageName}`;
        if (s.stageId === 'stage_1_1') o.selected = true;
        sel.appendChild(o);
    });
}


// ══════════════════════════════════════════════════════════════════════════════
// FETCH LEADS
// ══════════════════════════════════════════════════════════════════════════════
async function fetchLeads() {
    try {
        showTableLoading(true);
        const r = await fetch(`/api/leads?page=${currentPage}&per_page=${PER_PAGE}`);
        const d = await r.json();
        if (r.ok) {
            allLeads = d.leads;
            updateStatsBar(d.total, d.activeCount);
            const visible = showArchived ? d.leads : d.leads.filter(l => !l.isArchived);
            renderLeadsTable(visible);
            updatePaginationControls(d.page||1, d.totalPages||1, d.total||0, visible.length);
        } else {
            showTableError(d.error || 'Failed to load leads');
        }
    } catch (e) {
        showTableError('Network error. Please refresh.');
    } finally {
        showTableLoading(false);
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// RENDER TABLE
// ══════════════════════════════════════════════════════════════════════════════
function renderLeadsTable(leads) {
    const tbody = document.getElementById('leadsTableBody');
    if (!tbody) return;

    if (!leads.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-5 text-muted">
            <i class="bi bi-funnel" style="font-size:2rem;opacity:0.3;"></i>
            <p class="mt-2 mb-0">No leads yet. Click "Add Lead" to get started.</p>
        </td></tr>`;
        return;
    }

    tbody.innerHTML = leads.map(lead => {
        const c = LEADS_STAGE_COLORS[lead.currentStage] || { bg:"#F5F5F5", text:"#616161" };
        const stageBadge = `<span style="background:${c.bg};color:${c.text};
            padding:4px 10px;border-radius:12px;font-size:0.75rem;
            font-weight:600;white-space:nowrap;">${lead.stageName}</span>`;
        const linkedinBtn = lead.linkedinUrl
            ? `<a href="${lead.linkedinUrl}" target="_blank"
                  class="btn btn-sm btn-outline-primary py-0 px-2">
                  <i class="bi bi-linkedin"></i></a>` : '';
        return `
        <tr style="cursor:pointer;" onclick="openLeadDetail('${lead.leadId}')">
            <td class="fw-semibold">${escapeHtml(lead.name)}</td>
            <td class="text-muted">${escapeHtml(lead.company||'—')}</td>
            <td class="text-muted small">${escapeHtml(lead.email||'—')}</td>
            <td>${stageBadge}</td>
            <td class="text-muted small">${lead.createdAt}</td>
            <td onclick="event.stopPropagation()">
                <div class="d-flex gap-1">
                    ${linkedinBtn}
                    <button class="btn btn-sm btn-outline-primary py-0 px-2"
                            onclick="openEditLead('${lead.leadId}')" title="Edit">
                        <i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2"
                            onclick="openChangeStage('${lead.leadId}',
                                '${lead.currentStage}','${escapeHtml(lead.name)}')"
                            title="Change Stage">
                        <i class="bi bi-arrow-left-right"></i></button>
                    <button class="btn btn-sm btn-outline-info py-0 px-2"
                            onclick="openHistory('${lead.leadId}',
                                '${escapeHtml(lead.name)}')"
                            title="History">
                        <i class="bi bi-clock-history"></i></button>
                    <button class="btn btn-sm btn-outline-warning py-0 px-2"
                            onclick="toggleArchive('${lead.leadId}',${!lead.isArchived})"
                            title="${lead.isArchived?'Unarchive':'Archive'}">
                        <i class="bi bi-archive"></i></button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-2"
                            onclick="deleteLead('${lead.leadId}',
                                '${escapeHtml(lead.name)}')"
                            title="Delete">
                        <i class="bi bi-trash"></i></button>
                </div>
            </td>
        </tr>`;
    }).join('');
}


// ══════════════════════════════════════════════════════════════════════════════
// STATS BAR
// ══════════════════════════════════════════════════════════════════════════════
function updateStatsBar(total, activeCount) {
    const el = document.getElementById('statsBar');
    if (!el) return;
    el.innerHTML = `
        <div class="d-flex gap-3 flex-wrap">
            <span class="badge bg-primary fs-6 px-3 py-2">
                <i class="bi bi-people me-1"></i>Total Leads: ${total}</span>
            <span class="badge bg-success fs-6 px-3 py-2">
                <i class="bi bi-funnel me-1"></i>Active: ${activeCount}</span>
            <span class="badge bg-secondary fs-6 px-3 py-2">
                <i class="bi bi-archive me-1"></i>Archived: ${total - activeCount}</span>
        </div>`;
}


// ══════════════════════════════════════════════════════════════════════════════
// ADD LEAD
// ══════════════════════════════════════════════════════════════════════════════
async function submitAddLead() {
    const name        = document.getElementById('leadName').value.trim();
    const company     = document.getElementById('leadCompany').value.trim();
    const email       = document.getElementById('leadEmail').value.trim();
    const phone       = document.getElementById('leadPhone').value.trim();
    const linkedinUrl = document.getElementById('leadLinkedin').value.trim();
    const errorEl     = document.getElementById('addLeadError');

    errorEl.classList.add('d-none');

    if (!name) {
        errorEl.textContent = 'Lead name is required.';
        errorEl.classList.remove('d-none');
        return;
    }

    if (email) {
        const emailRx = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
        if (!emailRx.test(email)) {
            errorEl.textContent = 'Please enter a valid email address.';
            errorEl.classList.remove('d-none');
            return;
        }
    }

    if (phone) {
        const digits = phone.replace(/\D/g,'');
        if (digits.length !== 10) {
            errorEl.textContent = `Phone must be exactly 10 digits. You entered ${digits.length}.`;
            errorEl.classList.remove('d-none');
            return;
        }
    }

    const btn = document.getElementById('submitAddLead');
    btn.disabled = true;
    btn.textContent = 'Adding...';

    try {
        const r = await fetch('/api/leads', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({name, company, email, phone, linkedinUrl})
        });
        const d = await r.json();
        if (r.ok) {
            bootstrap.Modal.getInstance(
                document.getElementById('addLeadModal')).hide();
            document.getElementById('addLeadForm').reset();
            await fetchLeads();
            showToast('Lead added successfully!', 'success');
        } else {
            errorEl.textContent = d.error || 'Failed to add lead.';
            errorEl.classList.remove('d-none');
        }
    } catch (e) {
        errorEl.textContent = 'Network error. Please try again.';
        errorEl.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Add Lead';
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// EDIT LEAD — contact change approval workflow
// ══════════════════════════════════════════════════════════════════════════════
function openEditLead(leadId) {
    const lead = allLeads.find(l => l.leadId === leadId);
    if (!lead) return;

    document.getElementById('editLeadId').value      = leadId;
    document.getElementById('editLeadName').value    = lead.name || '';
    document.getElementById('editLeadCompany').value = lead.company || '';
    document.getElementById('editLeadEmail').value   = lead.email || '';
    document.getElementById('editLeadPhone').value   = lead.phone || '';
    document.getElementById('editLeadLinkedin').value = lead.linkedinUrl || '';

    originalContactValues = {
        email:       lead.email       || '',
        phone:       lead.phone       || '',
        linkedinUrl: lead.linkedinUrl || '',
    };

    const reqSection = document.getElementById('changeRequestSection');
    if (reqSection) reqSection.classList.add('d-none');

    const reasonSel = document.getElementById('changeRequestReason');
    if (reasonSel) reasonSel.value = '';

    const errorEl = document.getElementById('editLeadError');
    if (errorEl) errorEl.classList.add('d-none');

    new bootstrap.Modal(document.getElementById('editLeadModal')).show();
}

function detectContactChange() {
    const email    = document.getElementById('editLeadEmail')?.value    || '';
    const phone    = document.getElementById('editLeadPhone')?.value    || '';
    const linkedin = document.getElementById('editLeadLinkedin')?.value || '';

    const anyChanged =
        email    !== originalContactValues.email    ||
        phone    !== originalContactValues.phone    ||
        linkedin !== originalContactValues.linkedinUrl;

    const reqSection = document.getElementById('changeRequestSection');
    if (reqSection) reqSection.classList.toggle('d-none', !anyChanged);
}

function cleanPhoneDigits(phone) {
    let d = (phone || '').replace(/\D/g, '');
    if (d.length === 12 && d.startsWith('91')) d = d.slice(2);
    else if (d.length === 11 && d.startsWith('0')) d = d.slice(1);
    return d;
}

async function submitEditLead() {
    const leadId   = document.getElementById('editLeadId').value;
    const email    = document.getElementById('editLeadEmail').value.trim();
    const phone    = document.getElementById('editLeadPhone').value.trim();
    const linkedin = document.getElementById('editLeadLinkedin').value.trim();
    const errorEl  = document.getElementById('editLeadError');

    errorEl.classList.add('d-none');

    // Build changed fields list
    const changes = [];
    if (email    !== originalContactValues.email)
        changes.push({ field:'email',       current: originalContactValues.email,       next: email });
    if (phone    !== originalContactValues.phone)
        changes.push({ field:'phone',       current: originalContactValues.phone,       next: phone });
    if (linkedin !== originalContactValues.linkedinUrl)
        changes.push({ field:'linkedinUrl', current: originalContactValues.linkedinUrl, next: linkedin });

    if (changes.length === 0) {
        errorEl.textContent =
            'No changes detected. Name and Company cannot be edited. ' +
            'Modify Email, Phone, or LinkedIn to send an approval request.';
        errorEl.classList.remove('d-none');
        return;
    }

    // Validate
    for (const c of changes) {
        if (c.field === 'email' && c.next) {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c.next)) {
                errorEl.textContent = 'Please enter a valid email address.';
                errorEl.classList.remove('d-none');
                return;
            }
        }
        if (c.field === 'phone' && c.next) {
            const digits = cleanPhoneDigits(c.next);
            if (!/^\d{10}$/.test(digits)) {
                errorEl.textContent = 'Phone must be exactly 10 digits.';
                errorEl.classList.remove('d-none');
                return;
            }
        }
    }

    // Check reason selected
    const reason = document.getElementById('changeRequestReason')?.value || '';
    if (!reason) {
        errorEl.textContent = 'Please select a reason for the contact change.';
        errorEl.classList.remove('d-none');
        return;
    }

const submitBtn = document.getElementById('submitEditLead')
    || document.getElementById('editLeadBtn');
if (submitBtn) submitBtn.disabled = true;

    try {
        // Build requestedChanges object for the new change_requests route
        const requestedChanges = {};
        changes.forEach(c => { requestedChanges[c.field] = c.next; });

        const r = await fetch(`/api/leads/${leadId}/change-request`, {
            method:  'POST',
            headers: {'Content-Type':'application/json'},
            body:    JSON.stringify({ requestedChanges, reason })
        });
        const d = await r.json();

        if (r.ok) {
            bootstrap.Modal.getInstance(
                document.getElementById('editLeadModal')).hide();
            showToast('📤 Change request sent to M1 Manager for approval!', 'warning');
            fetchMyChangeRequests();
        } else {
            errorEl.textContent = d.error || 'Failed to submit request.';
            errorEl.classList.remove('d-none');
        }
    } catch (e) {
        errorEl.textContent = 'Network error. Please try again.';
        errorEl.classList.remove('d-none');
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// CHANGE STAGE
// ══════════════════════════════════════════════════════════════════════════════
function openChangeStage(leadId, currentStageId, leadName) {
    document.getElementById('changeStageLeadId').value        = leadId;
    document.getElementById('changeStageLeadName').textContent = leadName;

    const sel = document.getElementById('newStageSelect');
    sel.innerHTML = '';
    allStages.forEach(s => {
        const o = document.createElement('option');
        o.value = s.stageId;
        o.textContent = `${s.stageNumber} — ${s.stageName}`;
        if (s.stageId === currentStageId) o.selected = true;
        sel.appendChild(o);
    });
    new bootstrap.Modal(document.getElementById('changeStageModal')).show();
}

async function submitChangeStage() {
    const leadId   = document.getElementById('changeStageLeadId').value;
    const newStage = document.getElementById('newStageSelect').value;
    const notes    = document.getElementById('stageNotes').value.trim();
    const errorEl  = document.getElementById('changeStageError');
    errorEl.classList.add('d-none');

    const btn = document.getElementById('submitChangeStage');
    btn.disabled = true;
    btn.textContent = 'Updating...';

    try {
        const r = await fetch(`/api/leads/${leadId}/stage`, {
            method: 'PATCH',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({newStage, notes})
        });
        const d = await r.json();
        if (r.ok) {
            bootstrap.Modal.getInstance(
                document.getElementById('changeStageModal')).hide();
            document.getElementById('stageNotes').value = '';
            await fetchLeads();
            showToast(`Stage updated to: ${d.stageName}`, 'success');
        } else {
            errorEl.textContent = d.error || 'Failed to update stage.';
            errorEl.classList.remove('d-none');
        }
    } catch (e) {
        errorEl.textContent = 'Network error.';
        errorEl.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Update Stage';
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// HISTORY
// ══════════════════════════════════════════════════════════════════════════════
async function openHistory(leadId, leadName) {
    document.getElementById('historyLeadName').textContent = leadName;
    document.getElementById('historyBody').innerHTML =
        '<p class="text-muted text-center py-3">Loading...</p>';
    new bootstrap.Modal(document.getElementById('historyModal')).show();

    try {
        const r = await fetch(`/api/leads/${leadId}/history`);
        const d = await r.json();
        if (r.ok && d.history.length > 0) {
            document.getElementById('historyBody').innerHTML =
                d.history.map(e => `
                <div class="d-flex align-items-start mb-3">
                    <div class="me-3 text-primary">
                        <i class="bi bi-arrow-right-circle-fill fs-5"></i>
                    </div>
                    <div>
                        <div class="fw-semibold">
                            ${e.fromStageName || 'Start'} → ${e.toStageName}
                        </div>
                        ${e.notes
                            ? `<div class="text-muted small">${escapeHtml(e.notes)}</div>`
                            : ''}
                        <div class="text-muted small">${e.changedAt}</div>
                    </div>
                </div>`).join('');
        } else {
            document.getElementById('historyBody').innerHTML =
                '<p class="text-muted text-center py-3">No history yet.</p>';
        }
    } catch (e) {
        document.getElementById('historyBody').innerHTML =
            '<p class="text-danger text-center py-3">Failed to load.</p>';
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// LEAD DETAIL PANEL
// ══════════════════════════════════════════════════════════════════════════════
async function openLeadDetail(leadId) {
    const panel = document.getElementById('leadDetailPanel');
    if (!panel) return;
    panel.classList.remove('d-none');
    document.getElementById('detailContent').innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary spinner-border-sm"></div>
            <p class="mt-2 text-muted small">Loading...</p>
        </div>`;

    try {
        const r    = await fetch(`/api/leads/${leadId}`);
        const lead = await r.json();
        if (!r.ok) return;

        const c = LEADS_STAGE_COLORS[lead.currentStage]
               || { bg:"#F5F5F5", text:"#616161" };

        document.getElementById('detailContent').innerHTML = `
            <div class="mb-3">
                <h6 class="fw-bold text-dark mb-1">${escapeHtml(lead.name)}</h6>
                <span style="background:${c.bg};color:${c.text};
                    padding:3px 10px;border-radius:10px;
                    font-size:0.75rem;font-weight:600;">
                    ${escapeHtml(lead.stageName||'')}
                </span>
            </div>
            <table class="table table-sm table-borderless mb-3">
                <tr>
                    <td class="text-muted small fw-semibold ps-0" style="width:35%">Company</td>
                    <td class="small">${escapeHtml(lead.company||'—')}</td>
                </tr>
                <tr>
                    <td class="text-muted small fw-semibold ps-0">Email</td>
                    <td class="small">${lead.email
                        ? `<a href="mailto:${escapeHtml(lead.email)}"
                               class="text-decoration-none">
                               ${escapeHtml(lead.email)}</a>` : '—'}</td>
                </tr>
                <tr>
                    <td class="text-muted small fw-semibold ps-0">Phone</td>
                    <td class="small">${escapeHtml(lead.phone||'—')}</td>
                </tr>
                <tr>
                    <td class="text-muted small fw-semibold ps-0">LinkedIn</td>
                    <td class="small">${lead.linkedinUrl
                        ? `<a href="${escapeHtml(lead.linkedinUrl)}"
                               target="_blank" class="text-decoration-none">
                               View Profile
                               <i class="bi bi-box-arrow-up-right ms-1"></i>
                           </a>` : '—'}</td>
                </tr>
                <tr>
                    <td class="text-muted small fw-semibold ps-0">Status</td>
                    <td class="small">${lead.isArchived
                        ? '<span class="badge bg-secondary">Archived</span>'
                        : '<span class="badge bg-success">Active</span>'}</td>
                </tr>
            </table>
            <div class="d-flex gap-2 flex-wrap">
                <button class="btn btn-sm btn-outline-primary"
                        onclick="openEditLead('${lead.leadId}')">
                    <i class="bi bi-pencil me-1"></i>Edit</button>
                <button class="btn btn-sm btn-outline-secondary"
                        onclick="openChangeStage('${lead.leadId}',
                            '${lead.currentStage}','${escapeHtml(lead.name)}')">
                    <i class="bi bi-arrow-left-right me-1"></i>Stage</button>
                <button class="btn btn-sm btn-outline-warning"
                        onclick="toggleArchive('${lead.leadId}',${!lead.isArchived})">
                    <i class="bi bi-archive me-1"></i>
                    ${lead.isArchived ? 'Unarchive' : 'Archive'}</button>
            </div>`;
    } catch (e) {
        document.getElementById('detailContent').innerHTML =
            '<p class="text-danger small">Network error.</p>';
    }
}

function closeLeadDetail() {
    const panel = document.getElementById('leadDetailPanel');
    if (panel) panel.classList.add('d-none');
}


// ══════════════════════════════════════════════════════════════════════════════
// ARCHIVE / DELETE
// ══════════════════════════════════════════════════════════════════════════════
async function toggleArchive(leadId, archive) {
    if (!confirm(`Are you sure you want to ${archive?'archive':'unarchive'} this lead?`)) return;
    try {
        const r = await fetch(`/api/leads/${leadId}/archive`, {
            method: 'PATCH',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({archive})
        });
        const d = await r.json();
        if (r.ok) {
            await fetchLeads();
            showToast(archive ? 'Lead archived.' : 'Lead unarchived.',
                      archive ? 'warning' : 'success');
        } else { alert(d.error || 'Failed.'); }
    } catch (e) { alert('Network error.'); }
}

async function deleteLead(leadId, leadName) {
    if (!confirm(`⚠️ Permanently delete "${leadName}"?\nThis CANNOT be undone.`)) return;
    try {
        const r = await fetch(`/api/leads/${leadId}`, { method: 'DELETE' });
        const d = await r.json();
        if (r.ok) {
            closeLeadDetail();
            await fetchLeads();
            showToast(`Lead "${leadName}" deleted.`, 'danger');
        } else {
            alert(r.status === 403
                ? 'You can only delete your own leads.'
                : d.error || 'Failed.');
        }
    } catch (e) { alert('Network error.'); }
}


// ══════════════════════════════════════════════════════════════════════════════
// SEARCH / FILTER
// ══════════════════════════════════════════════════════════════════════════════
function filterLeads() {
    const search = document.getElementById('searchInput')?.value.toLowerCase().trim()||'';
    const stage  = document.getElementById('stageFilter')?.value||'';
    let filtered = showArchived ? allLeads : allLeads.filter(l=>!l.isArchived);
    if (search) filtered = filtered.filter(l =>
        l.name.toLowerCase().includes(search) ||
        (l.company||'').toLowerCase().includes(search) ||
        (l.email||'').toLowerCase().includes(search));
    if (stage) filtered = filtered.filter(l => l.currentStage === stage);
    renderLeadsTable(filtered);
}

function toggleShowArchived() {
    showArchived = !showArchived;
    const btn = document.getElementById('archiveToggleBtn');
    if (btn) {
        btn.classList.toggle('btn-outline-warning', !showArchived);
        btn.classList.toggle('btn-warning', showArchived);
    }
    filterLeads();
}


// ══════════════════════════════════════════════════════════════════════════════
// PAGINATION
// ══════════════════════════════════════════════════════════════════════════════
function changePage(direction) {
    currentPage = Math.max(1, currentPage + direction);
    fetchLeads();
}

function updatePaginationControls(page, totalPages, total, showing) {
    const controls  = document.getElementById('paginationControls');
    const info      = document.getElementById('paginationInfo');
    const indicator = document.getElementById('pageIndicator');
    const prevBtn   = document.getElementById('prevPageBtn');
    const nextBtn   = document.getElementById('nextPageBtn');
    if (!controls) return;
    controls.classList.toggle('d-none', total <= PER_PAGE);
    if (info) {
        const start = ((page-1)*PER_PAGE)+1;
        info.textContent = `Showing ${start}–${Math.min(page*PER_PAGE,total)} of ${total} leads`;
    }
    if (indicator) indicator.textContent = `Page ${page} of ${totalPages}`;
    if (prevBtn) prevBtn.disabled = page <= 1;
    if (nextBtn) nextBtn.disabled = page >= totalPages;
    currentPage = page;
}


// ══════════════════════════════════════════════════════════════════════════════
// BULK IMPORT
// ══════════════════════════════════════════════════════════════════════════════
async function submitBulkImport() {
    const fileInput = document.getElementById('bulkImportFile');
    const errorEl   = document.getElementById('importError');
    const resultsEl = document.getElementById('importResults');
    const successEl = document.getElementById('importSuccess');
    const errorsEl  = document.getElementById('importErrors');

    errorEl.classList.add('d-none');
    resultsEl.classList.add('d-none');

    if (!fileInput.files?.length) {
        errorEl.textContent = 'Please select a CSV file first.';
        errorEl.classList.remove('d-none');
        return;
    }

    const btn = document.getElementById('submitBulkImport');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Importing...';

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        const r = await fetch('/api/leads/bulk-import', { method:'POST', body:formData });
        const d = await r.json();
        if (r.ok) {
            resultsEl.classList.remove('d-none');
            successEl.classList.remove('d-none');
            document.getElementById('importSuccessMsg').textContent = d.message;
            if (d.errors?.length) {
                errorsEl.classList.remove('d-none');
                document.getElementById('importErrorList').innerHTML =
                    d.errors.map(e=>`<li>${e}</li>`).join('');
            }
            fileInput.value = '';
            await fetchLeads();
            showToast(`Imported ${d.imported} leads!`, 'success');
        } else {
            errorEl.textContent = d.error || 'Import failed.';
            errorEl.classList.remove('d-none');
        }
    } catch (e) {
        errorEl.textContent = 'Network error.';
        errorEl.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-upload me-1"></i>Import Leads';
    }
}


// ══════════════════════════════════════════════════════════════════════════════
// MY CHANGE REQUESTS (Employee — Requests Tab)
// ══════════════════════════════════════════════════════════════════════════════
async function fetchMyChangeRequests() {
    try {
        const r = await fetch('/api/change-requests');
        const d = await r.json();
        if (r.ok) {
            updateRequestsBadge(d.pendingCount || 0);
            renderRequestsTable(d.requests || []);
            const loading = document.getElementById('requestsLoading');
            const wrapper = document.getElementById('requestsWrapper');
            if (loading) loading.classList.add('d-none');
            if (wrapper) wrapper.classList.remove('d-none');
        }
    } catch (e) {
        console.error('fetchMyChangeRequests:', e);
    }
}

function updateRequestsBadge(count) {
    const badge = document.getElementById('pendingRequestsBadge');
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count;
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

function renderRequestsTable(requests) {
    const container = document.getElementById('requestsTableContainer');
    if (!container) return;

    if (!requests.length) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-arrow-left-right"
                   style="font-size:2.5rem;opacity:0.25;"></i>
                <p class="mt-2 mb-0">No change requests yet.</p>
                <p class="small">Edit a lead's Email, Phone, or LinkedIn
                to trigger an approval request.</p>
            </div>`;
        return;
    }

    const statusColors = {
        pending:  { bg:'#FEF9E7', text:'#9A7D0A', label:'⏳ Pending'  },
        approved: { bg:'#EAFAF1', text:'#1E8449', label:'✅ Approved' },
        rejected: { bg:'#FDEDEC', text:'#922B21', label:'❌ Rejected' },
    };

    const rows = requests.map(req => {
        const sc  = statusColors[req.status] || statusColors.pending;
        const statBadge = `<span style="background:${sc.bg};color:${sc.text};
            padding:3px 10px;border-radius:10px;
            font-size:0.75rem;font-weight:600;">${sc.label}</span>`;

        const changesHtml = Object.entries(req.requestedChanges||{})
            .map(([field, val]) => `
                <div class="small">
                    <span class="text-muted">${field}:</span>
                    <span class="text-decoration-line-through text-danger ms-1">
                        ${escapeHtml(req.currentValues?.[field]||'—')}
                    </span>
                    <span class="text-success ms-1 fw-semibold">
                        → ${escapeHtml(val)}
                    </span>
                </div>`).join('');

        return `
        <tr>
            <td class="fw-semibold small">${escapeHtml(req.leadName||'—')}</td>
            <td>${changesHtml}</td>
            <td class="small text-muted">${escapeHtml(req.reason||'—')}</td>
            <td>${statBadge}</td>
            <td class="small text-muted">${req.createdAt||'—'}</td>
            <td class="small">${req.reviewNote
                ? `<span class="text-muted">${escapeHtml(req.reviewNote)}</span>`
                : '—'}</td>
        </tr>`;
    }).join('');

    container.innerHTML = `
        <div class="card shadow-sm">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Lead</th>
                                <th>Requested Changes</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Submitted</th>
                                <th>Manager Note</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            </div>
        </div>`;
}


// ══════════════════════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════════════════════
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;')
              .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showTableLoading(show) {
    const loading = document.getElementById('tableLoading');
    const table   = document.getElementById('leadsTable');
    if (loading) loading.classList.toggle('d-none', !show);
    if (table)   table.classList.toggle('d-none', show);
}

function showTableError(message) {
    const tbody = document.getElementById('leadsTableBody');
    if (tbody) tbody.innerHTML = `
        <tr><td colspan="6" class="text-center py-4 text-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>${message}
        </td></tr>`;
}

function showToast(message, type='success') {
    const toast = document.getElementById('taskToast')
               || document.getElementById('successToast');
    if (!toast) return;
    toast.querySelector('.toast-body').textContent = message;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    new bootstrap.Toast(toast, { delay: 3000 }).show();
}


// ══════════════════════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', async () => {
    await fetchStages();
    await fetchLeads();

    setTimeout(() => {
        const stageFilter = document.getElementById('stageFilter');
        if (stageFilter && allStages.length > 0) {
            allStages.forEach(s => {
                const o = document.createElement('option');
                o.value = s.stageId;
                o.textContent = `${s.stageNumber} — ${s.stageName}`;
                stageFilter.appendChild(o);
            });
        }
    }, 800);

    document.getElementById('searchInput')
        ?.addEventListener('input', filterLeads);
    document.getElementById('stageFilter')
        ?.addEventListener('change', filterLeads);
});