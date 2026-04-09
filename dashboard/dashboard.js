/**
 * Admin Dashboard — JavaScript
 * =============================
 * Handles navigation, data fetching, and rendering for all dashboard views.
 */

const API_BASE = '/api/admin';
let authToken = localStorage.getItem('admin_token') || '';

// ── API Helpers ────────────────────────────────────────────────

async function api(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    });

    if (response.status === 401 || response.status === 403) {
        showLoginPrompt();
        throw new Error('Unauthorized');
    }

    return response.json();
}

function showLoginPrompt() {
    document.querySelector('.main-content').innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:80vh;flex-direction:column;gap:16px;">
            <h2>🔐 Admin Login Required</h2>
            <p style="color:var(--text-secondary)">Enter your JWT token to access the dashboard.</p>
            <input type="text" id="token-input" class="input" placeholder="Paste JWT token..." style="width:400px;max-width:90vw;">
            <button class="btn" onclick="loginWithToken()">Login</button>
        </div>
    `;
}

function loginWithToken() {
    const token = document.getElementById('token-input').value.trim();
    if (token) {
        localStorage.setItem('admin_token', token);
        authToken = token;
        location.reload();
    }
}

// ── Navigation ─────────────────────────────────────────────────

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const view = link.dataset.view;

        // Update active link
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Update active view
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(`view-${view}`).classList.add('active');

        // Update title
        document.getElementById('page-title').textContent =
            link.textContent.replace(/^..\s/, '');

        // Load data for the view
        loadView(view);
    });
});

document.getElementById('refresh-btn').addEventListener('click', () => {
    const activeLink = document.querySelector('.nav-link.active');
    if (activeLink) loadView(activeLink.dataset.view);
});

// ── View Loaders ───────────────────────────────────────────────

async function loadView(view) {
    try {
        switch (view) {
            case 'overview': await loadOverview(); break;
            case 'users': await loadUsers(); break;
            case 'revenue': await loadRevenue(); break;
            case 'analytics': await loadAnalytics(); break;
        }
        document.getElementById('last-updated').textContent =
            `Updated ${new Date().toLocaleTimeString()}`;
    } catch (err) {
        console.error(`Error loading ${view}:`, err);
    }
}

// ── Overview ───────────────────────────────────────────────────

async function loadOverview() {
    const data = await api('/dashboard');
    const stats = data.stats;

    // Update stat cards
    setStatValue('stat-total-users', stats.users.total.toLocaleString());
    setStatValue('stat-active-today', stats.users.active_today.toLocaleString());
    setStatValue('stat-revenue', stats.revenue.total_formatted);
    setStatValue('stat-pro-users', (stats.users.by_tier.pro + stats.users.by_tier.lifetime).toLocaleString());

    // Tier breakdown bars
    const total = stats.users.total || 1;
    const tierContainer = document.getElementById('tier-breakdown');
    tierContainer.innerHTML = ['free', 'pro', 'lifetime'].map(tier => {
        const count = stats.users.by_tier[tier];
        const pct = (count / total * 100).toFixed(1);
        return `
            <div class="tier-bar">
                <span class="tier-bar-label">${tier.charAt(0).toUpperCase() + tier.slice(1)}</span>
                <div class="tier-bar-track">
                    <div class="tier-bar-fill ${tier}" style="width: ${pct}%"></div>
                </div>
                <span class="tier-bar-count">${count}</span>
            </div>
        `;
    }).join('');

    // Activity summary
    const activityContainer = document.getElementById('activity-summary');
    activityContainer.innerHTML = `
        <div class="activity-item">
            <span>📄 Total Saved Pages</span>
            <strong>${stats.activity.total_saved_pages.toLocaleString()}</strong>
        </div>
        <div class="activity-item">
            <span>⚡ Events Today</span>
            <strong>${stats.activity.events_today.toLocaleString()}</strong>
        </div>
        <div class="activity-item">
            <span>✨ Active Subscriptions</span>
            <strong>${stats.activity.active_subscriptions.toLocaleString()}</strong>
        </div>
        <div class="activity-item">
            <span>🆕 New Users This Week</span>
            <strong>${stats.users.new_this_week.toLocaleString()}</strong>
        </div>
    `;
}

// ── Users ──────────────────────────────────────────────────────

let usersPage = 1;

async function loadUsers(page = 1) {
    usersPage = page;
    const search = document.getElementById('user-search')?.value || '';
    const tier = document.getElementById('user-tier-filter')?.value || '';

    let url = `/users?page=${page}&per_page=20`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (tier) url += `&tier=${tier}`;

    const data = await api(url);

    const tbody = document.getElementById('users-tbody');
    if (data.users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No users found</td></tr>';
    } else {
        tbody.innerHTML = data.users.map(user => `
            <tr>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        ${user.avatar_url ? `<img src="${user.avatar_url}" style="width:28px;height:28px;border-radius:50%;">` : ''}
                        <span>${user.name || '—'}</span>
                    </div>
                </td>
                <td>${user.email}</td>
                <td><span class="badge badge-${user.tier}">${user.tier}</span></td>
                <td>${formatDate(user.created_at)}</td>
                <td>${formatDate(user.last_active)}</td>
            </tr>
        `).join('');
    }

    // Pagination
    renderPagination('users-pagination', data.total, data.per_page, page, (p) => loadUsers(p));
}

// Search & filter listeners
document.getElementById('user-search')?.addEventListener('input', debounce(() => loadUsers(1), 300));
document.getElementById('user-tier-filter')?.addEventListener('change', () => loadUsers(1));

// ── Revenue ────────────────────────────────────────────────────

async function loadRevenue() {
    const [dashData, revData] = await Promise.all([
        api('/dashboard'),
        api('/revenue'),
    ]);

    const stats = dashData.stats;
    setStatValue('stat-revenue-total', stats.revenue.total_formatted);
    setStatValue('stat-revenue-month', stats.revenue.this_month_formatted);

    // Bar chart
    const chartContainer = document.getElementById('revenue-chart');
    const months = revData.monthly_revenue;
    const maxRevenue = Math.max(...months.map(m => m.revenue_cents), 1);

    chartContainer.innerHTML = months.map(m => {
        const height = Math.max((m.revenue_cents / maxRevenue) * 160, 4);
        const label = m.month.split('-')[1]; // Just month number
        return `
            <div class="chart-bar">
                <span class="chart-bar-value">${m.revenue_formatted}</span>
                <div class="chart-bar-fill" style="height: ${height}px;"></div>
                <span class="chart-bar-label">${label}</span>
            </div>
        `;
    }).join('');
}

// ── Analytics ──────────────────────────────────────────────────

async function loadAnalytics() {
    const data = await api('/analytics');

    // Events breakdown
    const eventsContainer = document.getElementById('events-breakdown');
    const events = data.events_by_type;
    const eventIcons = {
        login: '🔑', save_page: '📄', highlight: '🖍️',
        export: '📦', sync: '🔄',
    };

    if (Object.keys(events).length === 0) {
        eventsContainer.innerHTML = '<p class="text-muted">No events this week</p>';
    } else {
        eventsContainer.innerHTML = Object.entries(events).map(([type, count]) => `
            <div class="stat-card">
                <div class="stat-icon">${eventIcons[type] || '📊'}</div>
                <div class="stat-value">${count.toLocaleString()}</div>
                <div class="stat-label">${type.replace(/_/g, ' ')}</div>
            </div>
        `).join('');
    }

    // DAU chart
    const dauContainer = document.getElementById('dau-chart');
    const dau = data.daily_active_users;
    const maxDau = Math.max(...dau.map(d => d.active_users), 1);

    dauContainer.innerHTML = dau.map(d => {
        const height = Math.max((d.active_users / maxDau) * 160, 4);
        const dayName = new Date(d.date).toLocaleDateString('en', { weekday: 'short' });
        return `
            <div class="chart-bar">
                <span class="chart-bar-value">${d.active_users}</span>
                <div class="chart-bar-fill" style="height: ${height}px;"></div>
                <span class="chart-bar-label">${dayName}</span>
            </div>
        `;
    }).join('');
}

// ── Helpers ────────────────────────────────────────────────────

function setStatValue(id, value) {
    const card = document.getElementById(id);
    if (card) {
        card.querySelector('.stat-value').textContent = value;
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en', { month: 'short', day: 'numeric', year: 'numeric' });
}

function debounce(fn, ms) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

function renderPagination(containerId, total, perPage, currentPage, onClick) {
    const container = document.getElementById(containerId);
    const totalPages = Math.ceil(total / perPage);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';
    for (let i = 1; i <= Math.min(totalPages, 10); i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="(${onClick.toString()})(${i})">${i}</button>`;
    }
    container.innerHTML = html;
}

// ── Init ───────────────────────────────────────────────────────

loadView('overview');
