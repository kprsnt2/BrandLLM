/**
 * Blankphone Community - Forum JavaScript
 * Click on any thread to expand and read full content
 */

let discussions = [];
let currentFilter = 'all';
let expandedThread = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadDiscussions();
    setupFilters();
    renderDiscussions();
});

async function loadDiscussions() {
    try {
        const response = await fetch('community/discussions.json');
        discussions = await response.json();
        discussions.sort((a, b) => b.upvotes - a.upvotes);
    } catch (error) {
        console.error('Failed to load discussions:', error);
        discussions = [];
    }
}

function setupFilters() {
    const buttons = document.querySelectorAll('#filterButtons button');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.replace('btn-primary', 'btn-secondary'));
            btn.classList.replace('btn-secondary', 'btn-primary');
            currentFilter = btn.dataset.filter;
            expandedThread = null;
            renderDiscussions();
        });
    });
}

function toggleThread(threadId) {
    expandedThread = expandedThread === threadId ? null : threadId;
    renderDiscussions();

    // Scroll expanded thread into view
    if (expandedThread) {
        setTimeout(() => {
            const el = document.querySelector(`[data-thread-id="${threadId}"]`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

function renderDiscussions() {
    const container = document.getElementById('discussionsContainer');
    const filtered = currentFilter === 'all'
        ? discussions
        : discussions.filter(d => d.model === currentFilter);

    container.innerHTML = filtered.map(d => {
        const isExpanded = expandedThread === d.id;
        return `
        <div class="thread-card sentiment-${d.sentiment}" 
             data-thread-id="${d.id}"
             onclick="toggleThread('${d.id}')" 
             style="cursor:pointer;${isExpanded ? 'border-color:var(--color-accent);' : ''}">
            <div class="thread-header">
                <div class="thread-avatar" style="background: ${getAvatarColor(d.author)}">${d.avatar}</div>
                <div class="thread-meta">
                    <div class="thread-author">${d.author}</div>
                    <div class="thread-time">${formatDate(d.timestamp)} · ${getModelName(d.model)}</div>
                </div>
                <span class="badge badge-${d.model}">${getModelName(d.model)}</span>
            </div>
            <h3 class="thread-title" style="margin-bottom:var(--space-3);">${d.title}</h3>
            <div class="thread-content" style="color:var(--color-gray-300);font-size:var(--text-sm);line-height:1.7;${isExpanded ? 'white-space:pre-wrap;' : ''}">
                ${isExpanded ? d.content : truncate(d.content, 200)}
            </div>
            ${isExpanded ? `
                <div style="margin-top:var(--space-6);padding-top:var(--space-4);border-top:1px solid var(--glass-border);">
                    <p style="color:var(--color-gray-500);font-size:var(--text-sm);margin-bottom:var(--space-4);">
                        <i class="fa-solid fa-reply"></i> ${d.replies} replies in this thread
                    </p>
                    <div class="thread-tags" style="display:flex;flex-wrap:wrap;gap:var(--space-2);">
                        ${d.tags.map(t => `<span class="badge">${t}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            <div class="thread-footer" style="margin-top:var(--space-4);">
                <div class="thread-stat">
                    <button class="vote-btn" onclick="event.stopPropagation()"><i class="fa-solid fa-arrow-up"></i></button>
                    <span class="vote-count">${formatNumber(d.upvotes)}</span>
                    <button class="vote-btn" onclick="event.stopPropagation()"><i class="fa-solid fa-arrow-down"></i></button>
                </div>
                <div class="thread-stat"><i class="fa-solid fa-comment"></i> ${d.replies}</div>
                <div class="thread-stat" style="margin-left:auto;">
                    <i class="fa-solid fa-chevron-${isExpanded ? 'up' : 'down'}"></i>
                    ${isExpanded ? 'Collapse' : 'Read more'}
                </div>
            </div>
        </div>
    `}).join('');
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length).trim() + '...';
}

function getModelName(id) {
    const names = { pro: 'Pro', base: 'Blankphone', x: 'X', one: 'One', a: 'A' };
    return names[id] || id;
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Yesterday';
    if (diff < 7) return `${diff} days ago`;
    if (diff < 30) return `${Math.floor(diff / 7)} weeks ago`;
    return date.toLocaleDateString();
}

function formatNumber(num) {
    return num >= 1000 ? (num / 1000).toFixed(1) + 'K' : num.toString();
}

function getAvatarColor(name) {
    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'];
    return colors[name.charCodeAt(0) % colors.length];
}
