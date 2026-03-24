// leads.js — Lead Management JavaScript
// Handles: fetching leads, adding leads, changing stages, viewing history

// ── STAGE COLOURS ─────────────────────────────────────────────────────────────
// Each stage group gets a colour for the badge in the table

const STAGE_COLORS = {
    "stage_1_1": { bg: "#E8F5E9", text: "#2E7D32", label: "Qualified" },
    "stage_1_2": { bg: "#FFEBEE", text: "#C62828", label: "Not Qualified" },
    "stage_2":   { bg: "#E3F2FD", text: "#1565C0", label: "Request Sent" },
    "stage_2_1": { bg: "#E8EAF6", text: "#283593", label: "Connected" },
    "stage_2_2": { bg: "#FFF3E0", text: "#E65100", label: "Not Accepted" },
    "stage_3":   { bg: "#F3E5F5", text: "#6A1B9A", label: "Msg Sent" },
    "stage_3_1": { bg: "#FAFAFA", text: "#616161", label: "No Response" },
    "stage_4":   { bg: "#E0F7FA", text: "#00695C", label: "Reply Received" },
    "stage_6_1": { bg: "#F9FBE7", text: "#558B2F", label: "Interested" },
    "stage_6_2": { bg: "#FFEBEE", text: "#B71C1C", label: "Archived" },
    "stage_6_3": { bg: "#FFF8E1", text: "#F57F17", label: "Warm Lead" },
    "stage_7":   { bg: "#E8F5E9", text: "#1B5E20", label: "Mtg Scheduled" },
    "stage_8":   { bg: "#E0F2F1", text: "#004D40", label: "Mtg Completed" },
};

// ── GLOBAL STATE ──────────────────────────────────────────────────────────────
let allLeads   = [];
let allStages  = [];
let currentFilter = 'all';


// ── FETCH ALL STAGES ──────────────────────────────────────────────────────────
async function fetchStages() {
    try {
        const response = await fetch('/api/stages');
        const data     = await response.json();
        if (response.ok) {
            allStages = data.stages;
            populateStageDropdowns();
        }
    } catch (error) {
        console.error('Error fetching stages:', error);
    }
}


// ── POPULATE STAGE DROPDOWNS ──────────────────────────────────────────────────
function populateStageDropdowns() {
    // Populate the Add Lead form stage dropdown (if exists)
    const addStageSelect = document.getElementById('addLeadStage');
    if (addStageSelect) {
        addStageSelect.innerHTML = '';
        allStages.forEach(stage => {
            const option    = document.createElement('option');
            option.value    = stage.stageId;
            option.textContent = `${stage.stageNumber} — ${stage.stageName}`;
            if (stage.stageId === 'stage_1_1') option.selected = true;
            addStageSelect.appendChild(option);
        });
    }
}


// ── FETCH ALL LEADS ───────────────────────────────────────────────────────────
async function fetchLeads() {
    try {
        showTableLoading(true);
        const response = await fetch('/api/leads');
        const data     = await response.json();

        if (response.ok) {
            allLeads = data.leads;
            updateStatsBar(data.total, data.activeCount);
            renderLeadsTable(allLeads);
        } else {
            showTableError(data.error || 'Failed to load leads');
        }
    } catch (error) {
        showTableError('Network error. Please refresh the page.');
        console.error('Error fetching leads:', error);
    } finally {
        showTableLoading(false);
    }
}


// ── RENDER LEADS TABLE ────────────────────────────────────────────────────────
function renderLeadsTable(leads) {
    const tbody = document.getElementById('leadsTableBody');
    if (!tbody) return;

    if (leads.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-5 text-muted">
                    <i class="bi bi-funnel" style="font-size:2rem; opacity:0.3;"></i>
                    <p class="mt-2 mb-0">No leads yet. Click "Add Lead" to get started.</p>
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = leads.map(lead => {
        const color     = STAGE_COLORS[lead.currentStage] || { bg: "#F5F5F5", text: "#616161" };
        const stageBadge = `
            <span style="
                background-color: ${color.bg};
                color: ${color.text};
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                white-space: nowrap;
            ">${lead.stageName}</span>`;

        const linkedinBtn = lead.linkedinUrl
            ? `<a href="${lead.linkedinUrl}" target="_blank"
                  class="btn btn-sm btn-outline-primary py-0 px-2">
                   <i class="bi bi-linkedin"></i>
               </a>`
            : '';

        return `
            <tr style="cursor:pointer;">
                <td class="fw-semibold">${escapeHtml(lead.name)}</td>
                <td class="text-muted">${escapeHtml(lead.company || '—')}</td>
                <td class="text-muted small">${escapeHtml(lead.email || '—')}</td>
                <td>${stageBadge}</td>
                <td class="text-muted small">${lead.createdAt}</td>
                <td>
                    <div class="d-flex gap-1">
                        ${linkedinBtn}
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2"
                                onclick="openChangeStage('${lead.leadId}', '${lead.currentStage}', '${escapeHtml(lead.name)}')"
                                title="Change Stage">
                            <i class="bi bi-arrow-left-right"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info py-0 px-2"
                                onclick="openHistory('${lead.leadId}', '${escapeHtml(lead.name)}')"
                                title="View History">
                            <i class="bi bi-clock-history"></i>
                        </button>
                    </div>
                </td>
            </tr>`;
    }).join('');
}


// ── UPDATE STATS BAR ──────────────────────────────────────────────────────────
function updateStatsBar(total, activeCount) {
    const el = document.getElementById('statsBar');
    if (!el) return;
    el.innerHTML = `
        <div class="d-flex gap-3 flex-wrap">
            <span class="badge bg-primary fs-6 px-3 py-2">
                <i class="bi bi-people me-1"></i> Total Leads: ${total}
            </span>
            <span class="badge bg-success fs-6 px-3 py-2">
                <i class="bi bi-funnel me-1"></i> Active: ${activeCount}
            </span>
            <span class="badge bg-secondary fs-6 px-3 py-2">
                <i class="bi bi-archive me-1"></i> Archived: ${total - activeCount}
            </span>
        </div>`;
}


// ── ADD LEAD FORM SUBMIT ───────────────────────────────────────────────────────
async function submitAddLead() {
    const name        = document.getElementById('leadName').value.trim();
    const company     = document.getElementById('leadCompany').value.trim();
    const email       = document.getElementById('leadEmail').value.trim();
    const phone       = document.getElementById('leadPhone').value.trim();
    const linkedinUrl = document.getElementById('leadLinkedin').value.trim();
    const errorEl     = document.getElementById('addLeadError');

    // Validate
    if (!name) {
        errorEl.textContent = 'Lead name is required.';
        errorEl.classList.remove('d-none');
        return;
    }

    errorEl.classList.add('d-none');

    const submitBtn = document.getElementById('submitAddLead');
    submitBtn.disabled     = true;
    submitBtn.textContent  = 'Adding...';

    try {
        const response = await fetch('/api/leads', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ name, company, email, phone, linkedinUrl })
        });

        const data = await response.json();

        if (response.ok) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(
                document.getElementById('addLeadModal')
            );
            modal.hide();

            // Reset form
            document.getElementById('addLeadForm').reset();

            // Refresh leads table
            await fetchLeads();

            // Show success toast
            showToast('Lead added successfully!', 'success');
        } else {
            errorEl.textContent = data.error || 'Failed to add lead.';
            errorEl.classList.remove('d-none');
        }
    } catch (error) {
        errorEl.textContent = 'Network error. Please try again.';
        errorEl.classList.remove('d-none');
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Add Lead';
    }
}


// ── CHANGE STAGE MODAL ────────────────────────────────────────────────────────
function openChangeStage(leadId, currentStageId, leadName) {
    document.getElementById('changeStageLeadId').value   = leadId;
    document.getElementById('changeStageLeadName').textContent = leadName;

    // Populate stage select
    const select = document.getElementById('newStageSelect');
    select.innerHTML = '';
    allStages.forEach(stage => {
        const option       = document.createElement('option');
        option.value       = stage.stageId;
        option.textContent = `${stage.stageNumber} — ${stage.stageName}`;
        if (stage.stageId === currentStageId) option.selected = true;
        select.appendChild(option);
    });

    const modal = new bootstrap.Modal(document.getElementById('changeStageModal'));
    modal.show();
}


async function submitChangeStage() {
    const leadId   = document.getElementById('changeStageLeadId').value;
    const newStage = document.getElementById('newStageSelect').value;
    const notes    = document.getElementById('stageNotes').value.trim();
    const errorEl  = document.getElementById('changeStageError');

    errorEl.classList.add('d-none');

    const submitBtn = document.getElementById('submitChangeStage');
    submitBtn.disabled    = true;
    submitBtn.textContent = 'Updating...';

    try {
        const response = await fetch(`/api/leads/${leadId}/stage`, {
            method:  'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ newStage, notes })
        });

        const data = await response.json();

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(
                document.getElementById('changeStageModal')
            );
            modal.hide();
            document.getElementById('stageNotes').value = '';
            await fetchLeads();
            showToast(`Stage updated to: ${data.stageName}`, 'success');
        } else {
            errorEl.textContent = data.error || 'Failed to update stage.';
            errorEl.classList.remove('d-none');
        }
    } catch (error) {
        errorEl.textContent = 'Network error. Please try again.';
        errorEl.classList.remove('d-none');
    } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'Update Stage';
    }
}


// ── HISTORY MODAL ─────────────────────────────────────────────────────────────
async function openHistory(leadId, leadName) {
    document.getElementById('historyLeadName').textContent = leadName;
    document.getElementById('historyBody').innerHTML =
        '<p class="text-muted text-center py-3">Loading history...</p>';

    const modal = new bootstrap.Modal(document.getElementById('historyModal'));
    modal.show();

    try {
        const response = await fetch(`/api/leads/${leadId}/history`);
        const data     = await response.json();

        if (response.ok && data.history.length > 0) {
            document.getElementById('historyBody').innerHTML =
                data.history.map(entry => `
                    <div class="d-flex align-items-start mb-3">
                        <div class="me-3 text-primary">
                            <i class="bi bi-arrow-right-circle-fill fs-5"></i>
                        </div>
                        <div>
                            <div class="fw-semibold">
                                ${entry.fromStageName || 'Start'}
                                → ${entry.toStageName}
                            </div>
                            ${entry.notes
                                ? `<div class="text-muted small">${escapeHtml(entry.notes)}</div>`
                                : ''}
                            <div class="text-muted small">${entry.changedAt}</div>
                        </div>
                    </div>`).join('');
        } else {
            document.getElementById('historyBody').innerHTML =
                '<p class="text-muted text-center py-3">No history yet.</p>';
        }
    } catch (error) {
        document.getElementById('historyBody').innerHTML =
            '<p class="text-danger text-center py-3">Failed to load history.</p>';
    }
}


// ── SEARCH / FILTER ───────────────────────────────────────────────────────────
function filterLeads() {
    const searchTerm = document.getElementById('searchInput')
        .value.toLowerCase().trim();
    const stageFilter = document.getElementById('stageFilter').value;

    let filtered = allLeads;

    if (searchTerm) {
        filtered = filtered.filter(lead =>
            lead.name.toLowerCase().includes(searchTerm) ||
            (lead.company || '').toLowerCase().includes(searchTerm) ||
            (lead.email || '').toLowerCase().includes(searchTerm)
        );
    }

    if (stageFilter) {
        filtered = filtered.filter(lead => lead.currentStage === stageFilter);
    }

    renderLeadsTable(filtered);
}


// ── UTILITY FUNCTIONS ─────────────────────────────────────────────────────────
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;')
              .replace(/</g,'&lt;')
              .replace(/>/g,'&gt;')
              .replace(/"/g,'&quot;');
}

function showTableLoading(show) {
    const loading = document.getElementById('tableLoading');
    const table   = document.getElementById('leadsTable');
    if (loading) loading.classList.toggle('d-none', !show);
    if (table)   table.classList.toggle('d-none', show);
}

function showTableError(message) {
    const tbody = document.getElementById('leadsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4 text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>${message}
                </td>
            </tr>`;
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('successToast');
    if (!toast) return;
    toast.querySelector('.toast-body').textContent = message;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
}


// ── INITIALISE ON PAGE LOAD ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await fetchStages();
    await fetchLeads();

    // Search input listener
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterLeads);
    }

    // Stage filter listener
    const stageFilter = document.getElementById('stageFilter');
    if (stageFilter) {
        stageFilter.addEventListener('change', filterLeads);
    }
});