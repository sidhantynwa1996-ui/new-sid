let cfaData = [];
let currentView = 'dashboard';
let currentModule = null;
let practiceState = null;
let examState = null;
let flashcardState = null;
let isFullscreen = false;
let sidebarMode = 'schedule';

const STORAGE_KEY = 'cfa_tutor_progress';
const REVIEW_INTERVAL_DAYS = 2;

function getProgress() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
    return {
        readModules: {},
        questionHistory: [],
        flashcardHistory: {},
        reviewSchedule: {},
        watchedVideos: {},
        streak: { count: 0, lastDate: null },
        totalQuestionsAnswered: 0,
        totalCorrect: 0,
        totalFlashcardsReviewed: 0,
        firstUseDate: new Date().toISOString().split('T')[0]
    };
}

function saveProgress(progress) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function showActionToast(message, actionLabel, actionFn) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast toast-action';
    const msg = document.createElement('span');
    msg.textContent = message;
    const btn = document.createElement('button');
    btn.className = 'toast-btn';
    btn.textContent = actionLabel;
    btn.onclick = function() { toast.remove(); actionFn(); };
    toast.appendChild(msg);
    toast.appendChild(btn);
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
}

function showView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById('view-' + viewName).classList.add('active');
    document.querySelector(`.nav-btn[data-view="${viewName}"]`).classList.add('active');
    currentView = viewName;

    if (viewName === 'dashboard') renderDashboard();
    if (viewName === 'study') renderStudySidebar();
    if (viewName === 'practice') showPracticeSetup();
    if (viewName === 'flashcards') renderFlashcardSetup();
    if (viewName === 'exam') renderExamSetup();
    if (viewName === 'review') renderReviewQueue();
    if (viewName === 'plan') renderStudyPlan();
    if (viewName === 'syllabus') renderSyllabus();
}

// --- DASHBOARD ---
function renderDashboard() {
    const progress = getProgress();
    const readCount = Object.keys(progress.readModules).length;
    const totalMods = cfaData.reduce((s, v) => s + v.chapters.length, 0);
    const pct = totalMods > 0 ? Math.round((readCount / totalMods) * 100) : 0;

    document.getElementById('overallPercent').textContent = pct;
    document.getElementById('modulesCompleted').textContent = readCount;
    document.getElementById('totalModules').textContent = totalMods;
    document.getElementById('questionsAnswered').textContent = progress.totalQuestionsAnswered;
    document.getElementById('flashcardsReviewed').textContent = progress.totalFlashcardsReviewed;
    document.getElementById('videosWatched').textContent = Object.keys(progress.watchedVideos || {}).length;

    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (pct / 100) * circumference;
    document.getElementById('overallProgressCircle').style.strokeDashoffset = offset;

    updateStreak();
    document.getElementById('streakCount').textContent = progress.streak.count;

    const colors = ['#4285f4', '#ea4335', '#34a853', '#fbbc04', '#9c27b0',
                    '#ff6d00', '#00bcd4', '#795548', '#607d8b', '#e91e63'];
    let barsHtml = '';
    cfaData.forEach((vol, i) => {
        const volRead = vol.chapters.filter(ch => progress.readModules[`${vol.volume}-${ch.chapter}`]).length;
        const volPct = vol.chapters.length > 0 ? Math.round((volRead / vol.chapters.length) * 100) : 0;
        barsHtml += `
            <div class="subject-bar subject-bar-link" onclick="openFirstModuleOfVolume(${vol.volume})" title="Study ${vol.subject}">
                <div class="subject-bar-label">
                    <span>${vol.subject}</span>
                    <span>${volPct}%</span>
                </div>
                <div class="subject-bar-track">
                    <div class="subject-bar-fill" style="width:${volPct}%;background:${colors[i]}"></div>
                </div>
            </div>`;
    });
    document.getElementById('subjectBars').innerHTML = barsHtml;

    const dueItems = getReviewDueItems();
    const alertEl = document.getElementById('reviewAlert');
    if (dueItems.length > 0) {
        alertEl.style.display = 'block';
        document.getElementById('reviewDueCount').textContent = dueItems.length;
    } else {
        alertEl.style.display = 'none';
    }

    const cw = getCurrentWeek();
    const cwData = STUDY_SCHEDULE.find(w => w.week === cw) || STUDY_SCHEDULE[0];
    const cwKeys = getWeekModuleKeys(cwData);
    const cwDone = cwKeys.filter(k => progress.readModules[k]).length;
    const daysLeft = getDaysToExam();
    document.getElementById('quickNavRow').innerHTML = `
        <div class="qn-today" onclick="showView('plan')">
            <div class="qn-label">THIS WEEK</div>
            <div class="qn-value">Week ${cw}: ${cwData.subject}</div>
            <div class="qn-sub">${cwKeys.length > 0 ? cwDone + '/' + cwKeys.length + ' modules done' : cwData.phase.toUpperCase() + ' phase'} &middot; ${daysLeft} days to exam</div>
        </div>
        <div class="qn-links">
            <button class="qn-btn" onclick="event.stopPropagation();showView('plan')"><span class="qn-icon">&#9776;</span> Study Plan</button>
            <button class="qn-btn" onclick="event.stopPropagation();showView('syllabus')"><span class="qn-icon">&#128218;</span> Syllabus</button>
            <button class="qn-btn" onclick="event.stopPropagation();showView('study')"><span class="qn-icon">&#9733;</span> Study</button>
            <button class="qn-btn" onclick="event.stopPropagation();showView('practice')"><span class="qn-icon">&#9998;</span> Practice</button>
            <button class="qn-btn" onclick="event.stopPropagation();showView('flashcards')"><span class="qn-icon">&#9830;</span> Flashcards</button>
            <button class="qn-btn" onclick="event.stopPropagation();showView('exam')"><span class="qn-icon">&#9201;</span> Mock Exam</button>
        </div>
    `;

    let continueHtml = '';
    const recentModules = getRecentOrSuggestedModules(progress);
    recentModules.forEach(mod => {
        continueHtml += `
            <div class="continue-item" onclick="openModule(${mod.volume}, ${mod.chapter})">
                <div>
                    <div class="ci-subject">${mod.subject}</div>
                    <div class="ci-module">${mod.title}</div>
                </div>
                <span class="btn-sm">Study</span>
            </div>`;
    });
    if (!continueHtml) {
        continueHtml = '<p style="color:var(--text-secondary);padding:12px;">Start by selecting a topic from the Study tab!</p>';
    }
    document.getElementById('continueStudying').innerHTML = continueHtml;
}

function getRecentOrSuggestedModules(progress) {
    const modules = [];
    for (const vol of cfaData) {
        for (const ch of vol.chapters) {
            const key = `${vol.volume}-${ch.chapter}`;
            if (!progress.readModules[key]) {
                modules.push({
                    volume: vol.volume,
                    chapter: ch.chapter,
                    subject: vol.subject,
                    title: ch.title
                });
            }
        }
    }
    return modules.slice(0, 5);
}

function updateStreak() {
    const progress = getProgress();
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    if (progress.streak.lastDate === today) return;
    if (progress.streak.lastDate === yesterday) {
        progress.streak.count++;
    } else if (progress.streak.lastDate !== today) {
        progress.streak.count = 1;
    }
    progress.streak.lastDate = today;
    saveProgress(progress);
}

// --- STUDY VIEW ---
function toggleSidebarMode(mode) {
    sidebarMode = mode;
    renderStudySidebar();
}

function renderStudySidebar() {
    document.querySelectorAll('.sidebar-toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === sidebarMode);
    });

    if (sidebarMode === 'schedule') {
        renderScheduleSidebar();
    } else {
        renderSubjectsSidebar();
    }
}

function renderScheduleSidebar() {
    const progress = getProgress();
    const currentWeek = getCurrentWeek();
    let html = '';

    STUDY_SCHEDULE.forEach(week => {
        const modKeys = getWeekModuleKeys(week);
        const readCount = modKeys.filter(k => progress.readModules[k]).length;
        const totalCount = modKeys.length;
        const isCurrentWeek = week.week === currentWeek;
        const phaseClass = week.phase === 'learn' ? 'phase-learn' :
                          week.phase === 'practice' ? 'phase-practice' : 'phase-review';
        const phaseLabel = week.phase.charAt(0).toUpperCase() + week.phase.slice(1);

        const startDate = new Date(week.start + 'T00:00:00');
        const dateStr = startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

        html += `<div class="vol-group${isCurrentWeek ? ' current-week' : ''}">
            <div class="vol-header${isCurrentWeek ? ' expanded' : ''}" onclick="toggleVolume(this)">
                <span class="vol-arrow">&#9654;</span>
                <div class="week-header-info">
                    <span class="week-label">Week ${week.week} &middot; ${dateStr}</span>
                    <span class="week-date">${week.subject}</span>
                </div>
                <span class="sw-phase ${phaseClass}">${phaseLabel}</span>
                ${totalCount > 0 ? `<span style="font-size:10px;color:var(--text-secondary);margin-left:4px;">${readCount}/${totalCount}</span>` : ''}
            </div>
            <div class="vol-modules">`;

        if (modKeys.length > 0) {
            modKeys.forEach(key => {
                const [v, m] = key.split('-').map(Number);
                const isRead = progress.readModules[key];
                const isActive = currentModule && currentModule.volume === v && currentModule.chapter === m;
                const title = getModuleTitle(key);
                const vc = getVideoCount(key);
                html += `<div class="mod-item${isActive ? ' active' : ''}" onclick="openModule(${v}, ${m})">
                    <span class="mod-status ${isRead ? 'read' : 'unread'}">${isRead ? '&#10003;' : '&#9675;'}</span>
                    <span>${title}</span>
                    ${vc > 0 ? `<span class="mod-video-count">&#9654; ${vc}</span>` : ''}
                </div>`;
            });
        } else {
            html += `<div class="week-detail-text">${week.detail}</div>`;
        }

        html += `</div></div>`;
    });

    document.getElementById('moduleTree').innerHTML = html;
}

function renderSubjectsSidebar() {
    const progress = getProgress();
    let html = '';

    cfaData.forEach(vol => {
        const volRead = vol.chapters.filter(ch => progress.readModules[`${vol.volume}-${ch.chapter}`]).length;
        html += `<div class="vol-group">
            <div class="vol-header" onclick="toggleVolume(this)">
                <span class="vol-arrow">&#9654;</span>
                <span>Vol ${vol.volume}: ${vol.subject}</span>
                <span style="margin-left:auto;font-size:10px;color:var(--text-secondary)">${volRead}/${vol.chapters.length}</span>
            </div>
            <div class="vol-modules">`;

        vol.chapters.forEach(ch => {
            const key = `${vol.volume}-${ch.chapter}`;
            const isRead = progress.readModules[key];
            const isActive = currentModule && currentModule.volume === vol.volume && currentModule.chapter === ch.chapter;
            const vc = getVideoCount(key);
            html += `<div class="mod-item${isActive ? ' active' : ''}" onclick="openModule(${vol.volume}, ${ch.chapter})">
                <span class="mod-status ${isRead ? 'read' : 'unread'}">${isRead ? '&#10003;' : '&#9675;'}</span>
                <span>${ch.title}</span>
                ${vc > 0 ? `<span class="mod-video-count">&#9654; ${vc}</span>` : ''}
            </div>`;
        });

        html += `</div></div>`;
    });

    document.getElementById('moduleTree').innerHTML = html;
}

function toggleVolume(el) {
    el.classList.toggle('expanded');
}

function filterModules(query) {
    query = query.toLowerCase();
    document.querySelectorAll('.vol-group').forEach(group => {
        const items = group.querySelectorAll('.mod-item');
        let anyVisible = false;
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const match = !query || text.includes(query);
            item.style.display = match ? '' : 'none';
            if (match) anyVisible = true;
        });
        group.style.display = anyVisible ? '' : 'none';
        if (query && anyVisible) {
            group.querySelector('.vol-header').classList.add('expanded');
        }
    });
}

function openModule(volNum, chNum) {
    const vol = cfaData.find(v => v.volume === volNum);
    if (!vol) return;
    const ch = vol.chapters.find(c => c.chapter === chNum);
    if (!ch) return;

    currentModule = { volume: volNum, chapter: chNum, subject: vol.subject };

    if (currentView !== 'study') showView('study');

    document.getElementById('studyPlaceholder').style.display = 'none';
    document.getElementById('studyReader').style.display = 'block';

    document.getElementById('readerBreadcrumb').innerHTML =
        `<span style="color:var(--text-secondary)">Volume ${vol.volume}: ${vol.subject}</span> &rarr; <span>${ch.title}</span>`;

    if (ch.html) {
        document.getElementById('readerContent').innerHTML = ch.html;
    } else {
        const raw = ch.content || 'Content not available for this module.';
        document.getElementById('readerContent').innerHTML =
            '<div class="study-section"><p class="study-paragraph">' +
            raw.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>') +
            '</p></div>';
    }

    if (volNum === 10) {
        document.getElementById('readerContent').insertAdjacentHTML('afterbegin',
            '<div class="ethics-banner"><strong>&#9888; TIEBREAKER TOPIC</strong> &mdash; Ethics performance breaks ties near the pass/fail line. Study this thoroughly, not casually.</div>');
    }

    renderVideoPanel(volNum, chNum);

    buildSectionToc(ch);

    const readerContent = document.getElementById('readerContent');
    readerContent.scrollTop = 0;

    setupScrollSpy(readerContent);
    renderStudySidebar();
}

function buildSectionToc(ch) {
    const tocList = document.getElementById('tocList');
    let tocHtml = '';

    if (ch.sections && ch.sections.length > 0) {
        const sections = document.getElementById('readerContent').querySelectorAll('.study-section');

        sections.forEach((sec, idx) => {
            const heading = sec.querySelector('.section-heading, .study-module-title');
            if (!heading) return;

            const headingText = heading.textContent.replace(/^[\u{1F300}-\u{1F9FF}]/u, '').trim();
            if (!headingText) return;

            sec.id = 'section-' + idx;
            const typeClass = sec.classList.contains('study-outcomes') ? ' style="color:#3730a3"' :
                              sec.classList.contains('study-overview') ? ' style="color:#166534"' :
                              sec.classList.contains('study-summary') ? ' style="color:#92400e"' :
                              sec.classList.contains('study-practice') ? ' style="color:#991b1b"' :
                              sec.classList.contains('study-solutions') ? ' style="color:#166534"' : '';

            tocHtml += `<div class="toc-item" data-section="section-${idx}" onclick="scrollToSection('section-${idx}')"${typeClass}>${headingText}</div>`;

            const subsections = sec.querySelectorAll('.subsection-heading');
            subsections.forEach((sub, subIdx) => {
                const subText = sub.textContent.trim();
                if (subText.length > 2) {
                    const subId = `section-${idx}-sub-${subIdx}`;
                    sub.id = subId;
                    tocHtml += `<div class="toc-item toc-sub" data-section="${subId}" onclick="scrollToSection('${subId}')">${subText.substring(0, 45)}${subText.length > 45 ? '...' : ''}</div>`;
                }
            });
        });
    }

    if (!tocHtml) {
        tocHtml = '<p style="font-size:12px;color:var(--text-secondary);padding:8px;">No sections detected</p>';
    }

    tocList.innerHTML = tocHtml;
}

function scrollToSection(sectionId) {
    const el = document.getElementById(sectionId);
    if (!el) return;

    el.scrollIntoView({ behavior: 'smooth', block: 'start' });

    document.querySelectorAll('.toc-item').forEach(t => t.classList.remove('active'));
    const tocItem = document.querySelector(`.toc-item[data-section="${sectionId}"]`);
    if (tocItem) tocItem.classList.add('active');
}

function setupScrollSpy(container) {
    container.addEventListener('scroll', function() {
        const sections = container.querySelectorAll('.study-section[id], .subsection-heading[id]');
        let currentId = '';

        sections.forEach(sec => {
            const rect = sec.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            if (rect.top <= containerRect.top + 100) {
                currentId = sec.id;
            }
        });

        if (currentId) {
            document.querySelectorAll('.toc-item').forEach(t => t.classList.remove('active'));
            const active = document.querySelector(`.toc-item[data-section="${currentId}"]`);
            if (active) {
                active.classList.add('active');
                active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        }
    });
}

function toggleFullscreen() {
    const reader = document.getElementById('studyReader');
    const btn = document.getElementById('btnFullscreen');
    const sidebar = document.querySelector('.study-sidebar');
    const topBar = document.querySelector('.top-bar');
    const studyView = document.getElementById('view-study');

    isFullscreen = !isFullscreen;

    if (isFullscreen) {
        reader.classList.add('reader-fullscreen');
        sidebar.style.display = 'none';
        topBar.style.display = 'none';
        studyView.style.padding = '0';
        btn.innerHTML = '&#x2716; Exit';
        btn.classList.add('active');
    } else {
        reader.classList.remove('reader-fullscreen');
        sidebar.style.display = '';
        topBar.style.display = '';
        studyView.style.padding = '';
        btn.innerHTML = '&#x26F6; Expand';
        btn.classList.remove('active');
    }
}

function popOutReader() {
    if (!currentModule) return;
    const vol = cfaData.find(v => v.volume === currentModule.volume);
    if (!vol) return;
    const ch = vol.chapters.find(c => c.chapter === currentModule.chapter);
    if (!ch) return;

    const popWin = window.open('', '_blank', 'width=1000,height=800,scrollbars=yes');
    if (!popWin) {
        showToast('Pop-up blocked. Please allow pop-ups for this site.');
        return;
    }

    popWin.document.write(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>${ch.title} - CFA Level I</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #fff;
    color: #1a1a2e;
    line-height: 1.95;
    padding: 40px 60px 60px;
    max-width: 900px;
    margin: 0 auto;
}
.top-strip {
    background: #002b5c;
    color: white;
    padding: 14px 60px;
    position: fixed; top: 0; left: 0; right: 0; z-index: 10;
    font-size: 14px;
    display: flex; justify-content: space-between; align-items: center;
}
.top-strip span { opacity: 0.7; }
.top-strip strong { color: #c5a44e; }
body { padding-top: 70px; }
.study-section { margin-bottom: 36px; scroll-margin-top: 60px; }
.study-title-section { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 3px solid #c5a44e; }
.study-module-title { font-size: 30px; font-weight: 700; color: #002b5c; line-height: 1.3; }
.section-heading { font-size: 22px; font-weight: 700; color: #002b5c; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 2px solid #e5e7eb; }
.subsection-heading { font-size: 19px; font-weight: 600; color: #004b87; margin: 28px 0 14px; padding-left: 14px; border-left: 3px solid #c5a44e; }
.study-subsection { margin-bottom: 24px; }
.study-paragraph { margin-bottom: 14px; font-size: 16.5px; line-height: 1.95; }
.study-outcomes { background: linear-gradient(135deg, #eef2ff, #e8f0fe); border: 1px solid #c7d2fe; border-radius: 12px; padding: 28px; margin-bottom: 32px; }
.outcomes-heading { color: #3730a3; border-bottom-color: #c7d2fe; }
.study-overview { background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #bbf7d0; border-radius: 12px; padding: 28px; margin-bottom: 32px; }
.overview-heading { color: #166534; border-bottom-color: #bbf7d0; }
.study-summary { background: linear-gradient(135deg, #fffbeb, #fef3c7); border: 1px solid #fde68a; border-radius: 12px; padding: 28px; margin-bottom: 32px; }
.summary-heading { color: #92400e; border-bottom-color: #fde68a; }
.study-introduction { background: #f8fafc; border-radius: 12px; padding: 28px; margin-bottom: 32px; border: 1px solid #e5e7eb; }
.study-practice { background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 28px; margin-bottom: 32px; }
.practice-heading { color: #991b1b; border-bottom-color: #fecaca; }
.study-solutions { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 28px; margin-bottom: 32px; }
.solutions-heading { color: #166534; border-bottom-color: #bbf7d0; }
.definition-highlight { background: linear-gradient(to bottom, transparent 60%, #fde68a 60%); font-weight: 500; padding: 0 2px; }
.formula-block { background: #f0f4ff; font-family: Consolas, monospace; padding: 14px 20px; border-radius: 8px; border: 1px solid #c7d2fe; border-left: 4px solid #6366f1; font-size: 14.5px; margin: 16px 0; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }
.study-bullet-list { list-style: none; padding: 0; margin: 14px 0 18px; }
.study-bullet-list li { position: relative; padding: 10px 16px 10px 32px; margin-bottom: 6px; background: #f8f9fb; border-radius: 8px; border-left: 3px solid #004b87; line-height: 1.75; font-size: 16px; }
.study-bullet-list li::before { content: "\\2022"; position: absolute; left: 14px; color: #004b87; font-weight: 700; font-size: 18px; }
.key-term { color: #002b5c; font-weight: 600; }
.study-example { background: white; border: 1px solid #d1d5db; border-radius: 10px; margin: 24px 0; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,0.06); }
.example-header { background: #002b5c; color: white; padding: 12px 24px; font-weight: 600; font-size: 15px; }
.example-body { padding: 24px; font-size: 15.5px; line-height: 1.85; }
.example-para { margin-bottom: 10px; }
.study-question { background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 14px 20px; margin-bottom: 12px; font-weight: 500; font-size: 15.5px; line-height: 1.7; }
@media print { .top-strip { display: none; } body { padding-top: 0; } }
</style>
</head>
<body>
<div class="top-strip">
    <div><strong>CFA Level I</strong> <span>|</span> ${vol.subject}</div>
    <div><span>${ch.title}</span></div>
</div>
${ch.html || '<p>Content not available</p>'}
</body>
</html>`);
    popWin.document.close();
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isFullscreen) {
        toggleFullscreen();
    }
});

function navigateModule(direction) {
    if (!currentModule) return;
    const vol = cfaData.find(v => v.volume === currentModule.volume);
    if (!vol) return;

    const idx = vol.chapters.findIndex(c => c.chapter === currentModule.chapter);
    const newIdx = idx + direction;

    if (newIdx >= 0 && newIdx < vol.chapters.length) {
        openModule(vol.volume, vol.chapters[newIdx].chapter);
    } else if (direction > 0) {
        const nextVol = cfaData.find(v => v.volume === currentModule.volume + 1);
        if (nextVol && nextVol.chapters.length > 0) {
            openModule(nextVol.volume, nextVol.chapters[0].chapter);
        }
    } else if (direction < 0) {
        const prevVol = cfaData.find(v => v.volume === currentModule.volume - 1);
        if (prevVol && prevVol.chapters.length > 0) {
            openModule(prevVol.volume, prevVol.chapters[prevVol.chapters.length - 1].chapter);
        }
    }
}

function markModuleRead() {
    if (!currentModule) return;
    const progress = getProgress();
    const key = `${currentModule.volume}-${currentModule.chapter}`;
    progress.readModules[key] = new Date().toISOString();

    const reviewDate = new Date();
    reviewDate.setDate(reviewDate.getDate() + REVIEW_INTERVAL_DAYS);
    progress.reviewSchedule[key] = {
        nextReview: reviewDate.toISOString().split('T')[0],
        interval: REVIEW_INTERVAL_DAYS,
        volume: currentModule.volume,
        chapter: currentModule.chapter,
        subject: currentModule.subject
    };

    updateStreak();
    saveProgress(progress);
    renderStudySidebar();
    showActionToast('Module marked as read!', 'Start Questions', startPracticeForModule);
}

function startPracticeForModule() {
    if (!currentModule) return;
    showView('practice');
    document.getElementById('practiceSubject').value = currentModule.volume;
    updatePracticeModules();
    document.getElementById('practiceModule').value = currentModule.chapter;
}

function createFlashcardsForModule() {
    if (!currentModule) return;
    showView('flashcards');
    showToast('Flashcards are available for studied topics!');
}

// --- VIDEO PANEL ---
function renderVideoPanel(volNum, chNum) {
    const key = `${volNum}-${chNum}`;
    const videos = VIDEO_LIBRARY[key] || [];
    const panel = document.getElementById('videoPanel');
    const badge = document.getElementById('videoBadge');
    const list = document.getElementById('videoList');

    if (videos.length === 0) {
        panel.style.display = 'none';
        return;
    }

    panel.style.display = 'block';
    badge.textContent = videos.length + ' videos';

    const progress = getProgress();
    const watched = progress.watchedVideos || {};

    let html = '';
    videos.forEach((vid, idx) => {
        const vidKey = `${key}-${idx}`;
        const isWatched = watched[vidKey];
        html += `<div class="video-item${isWatched ? ' video-item-watched' : ''}" data-vidkey="${vidKey}">
            <a href="${vid.url}" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;flex:1;min-width:0;">
                <span class="video-item-icon">&#9654;</span>
                <span class="video-item-title">${vid.title}</span>
            </a>
            <span class="video-item-check ${isWatched ? 'watched' : 'unwatched'}" onclick="toggleVideoWatched('${vidKey}', event)" title="${isWatched ? 'Mark unwatched' : 'Mark watched'}">${isWatched ? '&#10003;' : '&#9675;'}</span>
        </div>`;
    });
    list.innerHTML = html;

    document.getElementById('videoPanelBody').style.display = 'none';
    document.getElementById('videoPanelArrow').classList.remove('open');
}

function toggleVideoPanel() {
    const body = document.getElementById('videoPanelBody');
    const arrow = document.getElementById('videoPanelArrow');
    const isOpen = body.style.display !== 'none';
    body.style.display = isOpen ? 'none' : 'block';
    arrow.classList.toggle('open', !isOpen);
}

function toggleVideoWatched(vidKey, event) {
    event.stopPropagation();
    const progress = getProgress();
    if (!progress.watchedVideos) progress.watchedVideos = {};

    if (progress.watchedVideos[vidKey]) {
        delete progress.watchedVideos[vidKey];
    } else {
        progress.watchedVideos[vidKey] = new Date().toISOString();
    }
    saveProgress(progress);

    const item = event.target.closest('.video-item');
    const isNowWatched = !!progress.watchedVideos[vidKey];
    item.classList.toggle('video-item-watched', isNowWatched);
    event.target.className = 'video-item-check ' + (isNowWatched ? 'watched' : 'unwatched');
    event.target.innerHTML = isNowWatched ? '&#10003;' : '&#9675;';
    event.target.title = isNowWatched ? 'Mark unwatched' : 'Mark watched';
}

function getModuleVideoProgress(volNum, chNum) {
    const key = `${volNum}-${chNum}`;
    const videos = VIDEO_LIBRARY[key] || [];
    if (videos.length === 0) return null;
    const progress = getProgress();
    const watched = progress.watchedVideos || {};
    const watchedCount = videos.filter((_, idx) => watched[`${key}-${idx}`]).length;
    return { total: videos.length, watched: watchedCount };
}

// --- PRACTICE ---
function showPracticeSetup() {
    document.getElementById('practiceSetup').style.display = 'block';
    document.getElementById('practiceSession').style.display = 'none';
    document.getElementById('practiceResults').style.display = 'none';

    const select = document.getElementById('practiceSubject');
    if (select.options.length <= 1) {
        cfaData.forEach(vol => {
            const opt = document.createElement('option');
            opt.value = vol.volume;
            opt.textContent = `Vol ${vol.volume}: ${vol.subject}`;
            select.appendChild(opt);
        });
    }
}

function updatePracticeModules() {
    const volNum = parseInt(document.getElementById('practiceSubject').value);
    const modSelect = document.getElementById('practiceModule');
    modSelect.innerHTML = '<option value="all">All Modules</option>';

    if (isNaN(volNum)) return;

    const vol = cfaData.find(v => v.volume === volNum);
    if (!vol) return;

    // Only list modules that actually have curated questions for this subject,
    // so the dropdown never offers an empty selection.
    const bank = (typeof CURATED_QUESTIONS !== 'undefined' && CURATED_QUESTIONS.length)
        ? CURATED_QUESTIONS : QUESTION_BANK.questions;
    const chaptersWithQs = new Set(bank.filter(q => q.volume === volNum).map(q => q.chapter));

    vol.chapters.forEach(ch => {
        if (chaptersWithQs.size && !chaptersWithQs.has(ch.chapter)) return;
        const opt = document.createElement('option');
        opt.value = ch.chapter;
        opt.textContent = ch.title;
        modSelect.appendChild(opt);
    });
}

function startPractice() {
    const subjectVal = document.getElementById('practiceSubject').value;
    const moduleVal = document.getElementById('practiceModule').value;
    const count = parseInt(document.getElementById('practiceCount').value);
    const difficulty = document.getElementById('practiceDifficulty').value;

    // Use the curated CFA-exam-style bank for Practice; fall back to the
    // auto-generated bank only if the curated set is unavailable.
    let pool = (typeof CURATED_QUESTIONS !== 'undefined' && CURATED_QUESTIONS.length)
        ? CURATED_QUESTIONS
        : QUESTION_BANK.questions;

    if (subjectVal !== 'all') {
        pool = pool.filter(q => q.volume === parseInt(subjectVal));
    }
    if (moduleVal !== 'all') {
        pool = pool.filter(q => q.chapter === parseInt(moduleVal));
    }
    if (difficulty !== 'mixed') {
        pool = pool.filter(q => q.difficulty === difficulty);
    }

    if (pool.length === 0) {
        showToast('No questions available for this selection. Try different filters.');
        return;
    }

    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    const selected = shuffled.slice(0, Math.min(count, shuffled.length));

    practiceState = {
        questions: selected,
        currentIndex: 0,
        answers: [],
        score: 0,
        answered: false
    };

    document.getElementById('practiceSetup').style.display = 'none';
    document.getElementById('practiceSession').style.display = 'block';
    document.getElementById('totalQ').textContent = selected.length;
    renderPracticeQuestion();
}

function renderPracticeQuestion() {
    if (!practiceState) return;
    const q = practiceState.questions[practiceState.currentIndex];
    practiceState.answered = false;

    document.getElementById('currentQ').textContent = practiceState.currentIndex + 1;
    document.getElementById('practiceScore').textContent = practiceState.score;
    document.getElementById('practiceAttempted').textContent = practiceState.answers.length;

    const pctDone = ((practiceState.currentIndex) / practiceState.questions.length) * 100;
    document.getElementById('practiceProgressBar').style.width = pctDone + '%';

    const letters = ['A', 'B', 'C', 'D'];
    let diffClass = 'diff-' + q.difficulty;

    let html = `
        <div class="question-topic">${q.subject} - ${q.chapterTitle}</div>
        <span class="question-difficulty ${diffClass}">${q.difficulty.toUpperCase()}</span>
        <div class="question-text">${q.question}</div>`;

    q.options.forEach((opt, i) => {
        html += `<button class="answer-option" onclick="selectAnswer(${i})" id="opt-${i}">
            <span class="option-letter">${letters[i]}.</span> ${opt}
        </button>`;
    });

    html += `<div id="explanationArea"></div>
        <div class="question-actions" id="questionActions" style="display:none;">
            <button class="btn-primary" onclick="nextPracticeQuestion()">Next Question &#8594;</button>
        </div>`;

    document.getElementById('questionCard').innerHTML = html;
}

function selectAnswer(idx) {
    if (practiceState.answered) return;
    practiceState.answered = true;

    const q = practiceState.questions[practiceState.currentIndex];
    const isCorrect = idx === q.correctIndex;

    if (isCorrect) practiceState.score++;
    practiceState.answers.push({ questionIndex: practiceState.currentIndex, selected: idx, correct: isCorrect });

    document.querySelectorAll('.answer-option').forEach(btn => btn.disabled = true);

    document.getElementById(`opt-${idx}`).classList.add(isCorrect ? 'correct' : 'incorrect');
    if (!isCorrect) {
        document.getElementById(`opt-${q.correctIndex}`).classList.add('was-correct');
    }

    document.getElementById('explanationArea').innerHTML = `
        <div class="explanation">
            <strong>${isCorrect ? '&#10003; Correct!' : '&#10007; Incorrect'}</strong><br>
            ${q.explanation}
        </div>`;

    document.getElementById('questionActions').style.display = 'flex';

    const progress = getProgress();
    progress.totalQuestionsAnswered++;
    if (isCorrect) progress.totalCorrect++;
    updateStreak();
    saveProgress(progress);
}

function nextPracticeQuestion() {
    practiceState.currentIndex++;
    if (practiceState.currentIndex >= practiceState.questions.length) {
        showPracticeResults();
    } else {
        renderPracticeQuestion();
    }
}

function showPracticeResults() {
    document.getElementById('practiceSession').style.display = 'none';
    document.getElementById('practiceResults').style.display = 'block';

    const total = practiceState.questions.length;
    const correct = practiceState.score;
    const pct = Math.round((correct / total) * 100);

    let grade = 'Needs Work';
    let gradeColor = 'var(--cfa-red)';
    if (pct >= 90) { grade = 'Excellent!'; gradeColor = 'var(--cfa-green)'; }
    else if (pct >= 70) { grade = 'Good'; gradeColor = 'var(--cfa-blue)'; }
    else if (pct >= 50) { grade = 'Fair'; gradeColor = 'var(--cfa-orange)'; }

    document.getElementById('resultsSummary').innerHTML = `
        <div class="result-stat">
            <div class="stat-num" style="color:${gradeColor}">${pct}%</div>
            <div class="stat-label">${grade}</div>
        </div>
        <div class="result-stat">
            <div class="stat-num">${correct}</div>
            <div class="stat-label">Correct</div>
        </div>
        <div class="result-stat">
            <div class="stat-num">${total - correct}</div>
            <div class="stat-label">Incorrect</div>
        </div>
        <div class="result-stat">
            <div class="stat-num">${total}</div>
            <div class="stat-label">Total</div>
        </div>`;

    let detailHtml = '';
    practiceState.answers.forEach((ans, i) => {
        const q = practiceState.questions[ans.questionIndex];
        detailHtml += `
            <div class="result-q ${ans.correct ? 'correct' : 'incorrect'}">
                <span class="rq-icon">${ans.correct ? '&#10003;' : '&#10007;'}</span>
                <span>Q${i + 1}: ${q.question.substring(0, 80)}...</span>
            </div>`;
    });
    document.getElementById('resultsDetail').innerHTML = detailHtml;
}

function endPractice() {
    if (practiceState && practiceState.answers.length > 0) {
        showPracticeResults();
    } else {
        showPracticeSetup();
    }
}

function reviewMissed() {
    if (!practiceState) return;
    const missed = practiceState.answers.filter(a => !a.correct);
    if (missed.length === 0) {
        showToast('You got everything right! No missed questions to review.');
        return;
    }

    const missedQuestions = missed.map(a => practiceState.questions[a.questionIndex]);
    practiceState = {
        questions: missedQuestions,
        currentIndex: 0,
        answers: [],
        score: 0,
        answered: false
    };

    document.getElementById('practiceResults').style.display = 'none';
    document.getElementById('practiceSession').style.display = 'block';
    document.getElementById('totalQ').textContent = missedQuestions.length;
    renderPracticeQuestion();
}

// --- FLASHCARDS ---
function renderFlashcardSetup() {
    const progress = getProgress();
    const allCards = QUESTION_BANK.flashcards || [];

    const fcHistory = progress.flashcardHistory || {};
    const today = new Date().toISOString().split('T')[0];

    let dueCount = 0;
    let newCount = 0;

    allCards.forEach((card, i) => {
        const history = fcHistory[i];
        if (!history) {
            newCount++;
        } else if (history.nextReview <= today) {
            dueCount++;
        }
    });

    document.getElementById('fcNew').textContent = newCount;
    document.getElementById('fcDue').textContent = dueCount;
    document.getElementById('fcTotal').textContent = allCards.length;

    const select = document.getElementById('flashcardSubject');
    if (select.options.length <= 1) {
        cfaData.forEach(vol => {
            const opt = document.createElement('option');
            opt.value = vol.volume;
            opt.textContent = `Vol ${vol.volume}: ${vol.subject}`;
            select.appendChild(opt);
        });
    }

    document.getElementById('flashcardSetup').style.display = 'block';
    document.getElementById('flashcardSession').style.display = 'none';
}

function startFlashcards() {
    const subjectVal = document.getElementById('flashcardSubject').value;
    const progress = getProgress();
    const allCards = QUESTION_BANK.flashcards || [];
    const today = new Date().toISOString().split('T')[0];

    let pool = allCards.map((card, i) => ({ ...card, originalIndex: i }));

    if (subjectVal !== 'all') {
        pool = pool.filter(c => c.volume === parseInt(subjectVal));
    }

    const due = pool.filter(c => {
        const h = progress.flashcardHistory[c.originalIndex];
        return !h || h.nextReview <= today;
    });

    if (due.length === 0) {
        showToast('No flashcards due for review! Come back later.');
        return;
    }

    const session = due.sort(() => Math.random() - 0.5).slice(0, 20);

    flashcardState = {
        cards: session,
        currentIndex: 0,
        flipped: false
    };

    document.getElementById('flashcardSetup').style.display = 'none';
    document.getElementById('flashcardSession').style.display = 'block';
    document.getElementById('fcSessionTotal').textContent = session.length;
    renderFlashcard();
}

function renderFlashcard() {
    if (!flashcardState) return;
    const card = flashcardState.cards[flashcardState.currentIndex];

    document.getElementById('fcCurrent').textContent = flashcardState.currentIndex + 1;
    document.getElementById('fcTopic').textContent = card.topic;
    document.getElementById('fcQuestion').textContent = card.front;
    document.getElementById('fcAnswer').textContent = card.back;

    document.getElementById('flashcardInner').classList.remove('flipped');
    document.getElementById('fcRating').style.display = 'none';
    flashcardState.flipped = false;
}

function flipFlashcard() {
    if (!flashcardState) return;
    flashcardState.flipped = !flashcardState.flipped;
    document.getElementById('flashcardInner').classList.toggle('flipped');

    if (flashcardState.flipped) {
        document.getElementById('fcRating').style.display = 'block';
    }
}

function rateFlashcard(rating) {
    if (!flashcardState) return;
    const card = flashcardState.cards[flashcardState.currentIndex];
    const progress = getProgress();

    if (!progress.flashcardHistory) progress.flashcardHistory = {};

    const intervals = [1, 2, 4, 7];
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + intervals[rating]);

    progress.flashcardHistory[card.originalIndex] = {
        lastReview: new Date().toISOString().split('T')[0],
        nextReview: nextDate.toISOString().split('T')[0],
        rating: rating
    };

    progress.totalFlashcardsReviewed++;
    updateStreak();
    saveProgress(progress);

    flashcardState.currentIndex++;
    if (flashcardState.currentIndex >= flashcardState.cards.length) {
        showToast('Flashcard session complete!');
        renderFlashcardSetup();
    } else {
        renderFlashcard();
    }
}

function generateAllFlashcards() {
    showToast(`${QUESTION_BANK.flashcards.length} flashcards are ready! Click "Start Review" to begin.`);
}

// --- MOCK EXAM ---
function renderExamSetup() {
    document.getElementById('examSetup').style.display = 'block';
    document.getElementById('examSession').style.display = 'none';
    document.getElementById('examResults').style.display = 'none';

    const select = document.getElementById('examSubject');
    if (select.options.length <= 1) {
        cfaData.forEach(vol => {
            const opt = document.createElement('option');
            opt.value = vol.volume;
            opt.textContent = `Vol ${vol.volume}: ${vol.subject}`;
            select.appendChild(opt);
        });
    }
}

function startExam(type) {
    const examBank = (typeof CURATED_QUESTIONS !== 'undefined' && CURATED_QUESTIONS.length)
        ? CURATED_QUESTIONS : QUESTION_BANK.questions;
    let pool = [...examBank];
    let questionCount, timeMinutes;

    if (type === 'full') {
        questionCount = 180;
        timeMinutes = 270;
    } else if (type === 'mini') {
        questionCount = 45;
        timeMinutes = 60;
    } else if (type === 'subject') {
        const subjectVal = document.getElementById('examSubject').value;
        if (!subjectVal) {
            showToast('Please select a subject first.');
            return;
        }
        pool = pool.filter(q => q.volume === parseInt(subjectVal));
        questionCount = 30;
        timeMinutes = 45;
    }

    if (pool.length < questionCount) {
        questionCount = pool.length;
    }

    const shuffled = pool.sort(() => Math.random() - 0.5).slice(0, questionCount);

    examState = {
        questions: shuffled,
        currentIndex: 0,
        answers: new Array(shuffled.length).fill(null),
        flagged: new Set(),
        timeRemaining: timeMinutes * 60,
        timer: null,
        submitted: false
    };

    document.getElementById('examSetup').style.display = 'none';
    document.getElementById('examSession').style.display = 'block';
    document.getElementById('examTotalQ').textContent = shuffled.length;

    renderExamNav();
    renderExamQuestion();
    startExamTimer();
}

function startExamTimer() {
    examState.timer = setInterval(() => {
        examState.timeRemaining--;
        if (examState.timeRemaining <= 0) {
            clearInterval(examState.timer);
            submitExam();
            return;
        }

        const hrs = Math.floor(examState.timeRemaining / 3600);
        const mins = Math.floor((examState.timeRemaining % 3600) / 60);
        const secs = examState.timeRemaining % 60;
        document.getElementById('examTimer').textContent =
            `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

        if (examState.timeRemaining <= 300) {
            document.getElementById('examTimer').style.color = '#ff4444';
        }
    }, 1000);
}

function renderExamQuestion() {
    if (!examState) return;
    const q = examState.questions[examState.currentIndex];
    const letters = ['A', 'B', 'C', 'D'];

    document.getElementById('examCurrentQ').textContent = examState.currentIndex + 1;

    let html = `
        <div class="question-topic">${q.subject}</div>
        <div class="question-text">${q.question}</div>`;

    q.options.forEach((opt, i) => {
        const selected = examState.answers[examState.currentIndex] === i;
        html += `<button class="answer-option${selected ? ' selected' : ''}" onclick="selectExamAnswer(${i})">
            <span class="option-letter">${letters[i]}.</span> ${opt}
        </button>`;
    });

    document.getElementById('examQuestionArea').innerHTML = html;
    renderExamNav();
}

function selectExamAnswer(idx) {
    examState.answers[examState.currentIndex] = idx;
    renderExamQuestion();
}

function examNavigate(direction) {
    const newIdx = examState.currentIndex + direction;
    if (newIdx >= 0 && newIdx < examState.questions.length) {
        examState.currentIndex = newIdx;
        renderExamQuestion();
    }
}

function goToExamQuestion(idx) {
    examState.currentIndex = idx;
    renderExamQuestion();
}

function flagQuestion() {
    if (examState.flagged.has(examState.currentIndex)) {
        examState.flagged.delete(examState.currentIndex);
    } else {
        examState.flagged.add(examState.currentIndex);
    }
    renderExamNav();
}

function renderExamNav() {
    if (!examState) return;
    let html = '';
    for (let i = 0; i < examState.questions.length; i++) {
        let cls = 'exam-nav-btn';
        if (i === examState.currentIndex) cls += ' current';
        if (examState.answers[i] !== null) cls += ' answered';
        if (examState.flagged.has(i)) cls += ' flagged';
        html += `<button class="${cls}" onclick="goToExamQuestion(${i})">${i + 1}</button>`;
    }
    document.getElementById('examNav').innerHTML = html;
}

function submitExam() {
    if (examState.submitted) return;
    examState.submitted = true;

    if (examState.timer) clearInterval(examState.timer);

    const total = examState.questions.length;
    const answered = examState.answers.filter(a => a !== null).length;
    let correct = 0;

    examState.questions.forEach((q, i) => {
        if (examState.answers[i] === q.correctIndex) correct++;
    });

    const pct = Math.round((correct / total) * 100);
    const passed = pct >= 70;

    const subjectBreakdown = {};
    examState.questions.forEach((q, i) => {
        if (!subjectBreakdown[q.subject]) {
            subjectBreakdown[q.subject] = { correct: 0, total: 0 };
        }
        subjectBreakdown[q.subject].total++;
        if (examState.answers[i] === q.correctIndex) {
            subjectBreakdown[q.subject].correct++;
        }
    });

    let breakdownHtml = '';
    for (const [subject, stats] of Object.entries(subjectBreakdown)) {
        const sPct = Math.round((stats.correct / stats.total) * 100);
        const barColor = sPct >= 70 ? 'var(--cfa-green)' : sPct >= 50 ? 'var(--cfa-orange)' : 'var(--cfa-red)';
        breakdownHtml += `
            <div class="subject-bar" style="margin-bottom:16px;">
                <div class="subject-bar-label">
                    <span>${subject}</span>
                    <span>${stats.correct}/${stats.total} (${sPct}%)</span>
                </div>
                <div class="subject-bar-track" style="height:12px;">
                    <div class="subject-bar-fill" style="width:${sPct}%;background:${barColor};height:12px;"></div>
                </div>
            </div>`;
    }

    document.getElementById('examSession').style.display = 'none';
    document.getElementById('examResults').style.display = 'block';
    document.getElementById('examResults').innerHTML = `
        <h2 style="color:var(--cfa-navy);margin-bottom:24px;">Exam Results</h2>
        <div class="results-summary">
            <div class="result-stat">
                <div class="stat-num" style="color:${passed ? 'var(--cfa-green)' : 'var(--cfa-red)'}">${pct}%</div>
                <div class="stat-label">${passed ? 'PASSED' : 'NOT PASSED'}</div>
            </div>
            <div class="result-stat">
                <div class="stat-num">${correct}</div>
                <div class="stat-label">Correct</div>
            </div>
            <div class="result-stat">
                <div class="stat-num">${answered}</div>
                <div class="stat-label">Answered</div>
            </div>
            <div class="result-stat">
                <div class="stat-num">${total}</div>
                <div class="stat-label">Total</div>
            </div>
        </div>
        <h3 style="color:var(--cfa-navy);margin:24px 0 16px;">Subject Breakdown</h3>
        ${breakdownHtml}
        <div style="margin-top:24px;display:flex;gap:12px;">
            <button class="btn-primary" onclick="renderExamSetup()">New Exam</button>
            <button class="btn-secondary" onclick="reviewExamAnswers()">Review Answers</button>
        </div>
        <div class="view-nav-strip" style="margin-top:20px;">
            <span class="view-nav-label">Next steps:</span>
            <button class="btn-sm" onclick="showView('study')">&#9733; Study Weak Areas</button>
            <button class="btn-sm" onclick="showView('practice')">&#9998; Practice</button>
            <button class="btn-sm" onclick="showView('flashcards')">&#9830; Flashcards</button>
            <button class="btn-sm" onclick="showView('review')">&#8634; Review Queue</button>
            <button class="btn-sm" onclick="showView('syllabus')">&#128218; Syllabus</button>
        </div>`;

    const progress = getProgress();
    progress.totalQuestionsAnswered += total;
    progress.totalCorrect += correct;
    updateStreak();
    saveProgress(progress);
}

function reviewExamAnswers() {
    if (!examState) return;
    const letters = ['A', 'B', 'C', 'D'];

    let html = '<h2 style="color:var(--cfa-navy);margin-bottom:24px;">Exam Review</h2>';

    examState.questions.forEach((q, i) => {
        const userAns = examState.answers[i];
        const isCorrect = userAns === q.correctIndex;

        html += `
            <div style="background:${isCorrect ? '#d4edda' : '#f8d7da'};padding:16px;border-radius:8px;margin-bottom:12px;">
                <div style="font-size:12px;color:var(--cfa-blue);margin-bottom:4px;">${q.subject} - ${q.chapterTitle}</div>
                <div style="font-weight:500;margin-bottom:8px;">Q${i+1}: ${q.question}</div>
                <div style="font-size:14px;">
                    Your answer: ${userAns !== null ? letters[userAns] + '. ' + q.options[userAns] : 'Not answered'}
                </div>
                ${!isCorrect ? `<div style="font-size:14px;color:var(--cfa-green);margin-top:4px;">
                    Correct: ${letters[q.correctIndex]}. ${q.options[q.correctIndex]}
                </div>` : ''}
                <div style="font-size:13px;color:var(--text-secondary);margin-top:8px;">${q.explanation}</div>
            </div>`;
    });

    html += '<button class="btn-primary" onclick="renderExamSetup()" style="margin-top:16px;">Back to Exam Setup</button>';

    document.getElementById('examResults').innerHTML = html;
}

// --- REVIEW QUEUE ---
function getReviewDueItems() {
    const progress = getProgress();
    const today = new Date().toISOString().split('T')[0];
    const dueItems = [];

    for (const [key, schedule] of Object.entries(progress.reviewSchedule || {})) {
        if (schedule.nextReview <= today) {
            const vol = cfaData.find(v => v.volume === schedule.volume);
            const ch = vol ? vol.chapters.find(c => c.chapter === schedule.chapter) : null;
            dueItems.push({
                key,
                ...schedule,
                title: ch ? ch.title : `Module ${schedule.chapter}`,
                subjectName: vol ? vol.subject : schedule.subject
            });
        }
    }

    return dueItems;
}

function renderReviewQueue() {
    const progress = getProgress();
    const today = new Date().toISOString().split('T')[0];
    const items = [];

    for (const [key, schedule] of Object.entries(progress.reviewSchedule || {})) {
        const vol = cfaData.find(v => v.volume === schedule.volume);
        const ch = vol ? vol.chapters.find(c => c.chapter === schedule.chapter) : null;
        items.push({
            key,
            ...schedule,
            title: ch ? ch.title : `Module ${schedule.chapter}`,
            subjectName: vol ? vol.subject : schedule.subject,
            isDue: schedule.nextReview <= today
        });
    }

    items.sort((a, b) => a.nextReview.localeCompare(b.nextReview));

    let html = '';
    if (items.length === 0) {
        html = '<p style="color:var(--text-secondary);text-align:center;padding:40px;">No modules studied yet. Start studying to build your review queue!</p>';
    } else {
        items.forEach(item => {
            const dueText = item.isDue ? 'Due now!' : `Due: ${item.nextReview}`;
            html += `
                <div class="review-item ${item.isDue ? 'due' : 'upcoming'}">
                    <div class="ri-info">
                        <div class="ri-subject">${item.subjectName}</div>
                        <div class="ri-module">${item.title}</div>
                        <div class="ri-due">${dueText} (Review interval: ${item.interval} days)</div>
                    </div>
                    <div class="ri-actions">
                        <button class="btn-sm" onclick="openModule(${item.volume}, ${item.chapter})">Study</button>
                        <button class="btn-sm" onclick="startReviewPractice('${item.key}')">Practice</button>
                        ${item.isDue ? `<button class="btn-primary" style="padding:6px 14px;font-size:13px;" onclick="completeReview('${item.key}')">Done</button>` : ''}
                    </div>
                </div>`;
        });
    }

    document.getElementById('reviewList').innerHTML = html;
}

function completeReview(key) {
    const progress = getProgress();
    const schedule = progress.reviewSchedule[key];
    if (!schedule) return;

    schedule.interval = Math.min(schedule.interval * 2, 16);
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + schedule.interval);
    schedule.nextReview = nextDate.toISOString().split('T')[0];

    saveProgress(progress);
    renderReviewQueue();
    renderDashboard();
    showToast(`Review complete! Next review in ${schedule.interval} days.`);
}

function startReviewPractice(key) {
    const parts = key.split('-');
    const volNum = parseInt(parts[0]);
    const chNum = parseInt(parts[1]);

    showView('practice');
    document.getElementById('practiceSubject').value = volNum;
    updatePracticeModules();
    document.getElementById('practiceModule').value = chNum;
}

// --- STUDY PLAN ---
const EXAM_DATE = new Date('2026-10-12');
const PLAN_START = new Date('2026-06-22');

const STUDY_SCHEDULE = [
    { week: 1,  start: '2026-06-22', subject: 'Ethical & Professional Standards', vol: 10, modules: [1,2,3,4,5], phase: 'learn', detail: 'Ethics first - highest exam weight (15-20%)' },
    { week: 2,  start: '2026-06-29', subject: 'Quantitative Methods (Part 1)', vol: 1, modules: [1,2,3,4,5,6], phase: 'learn', detail: 'Rates, TVM, Statistics, Probability, Simulation' },
    { week: 3,  start: '2026-07-06', subject: 'Quantitative Methods (Part 2)', vol: 1, modules: [7,8,9,10,11,12], phase: 'learn', detail: 'Inference, Hypothesis Testing, Regression' },
    { week: 4,  start: '2026-07-13', subject: 'Economics', vol: 2, modules: [1,2,3,4,5,6,7,8], phase: 'learn', detail: 'Market Structures, Business Cycles, Trade, FX' },
    { week: 5,  start: '2026-07-20', subject: 'Financial Statement Analysis (Part 1)', vol: 4, modules: [1,2,3,4,5,6], phase: 'learn', detail: 'Income Statements, Balance Sheets, Cash Flows' },
    { week: 6,  start: '2026-07-27', subject: 'Financial Statement Analysis (Part 2)', vol: 4, modules: [7,8,9,10,11,12], phase: 'learn', detail: 'Long-Term Assets, Reporting Quality, Modeling' },
    { week: 7,  start: '2026-08-03', subject: 'Corporate Issuers', vol: 3, modules: [1,2,3,4,5,6,7], phase: 'learn', detail: 'All 7 modules - Governance, Capital Structure' },
    { week: 8,  start: '2026-08-10', subject: 'Equity Investments', vol: 5, modules: [1,2,3,4,5,6,7,8], phase: 'learn', detail: 'Market Structure through Valuation' },
    { week: 9,  start: '2026-08-17', subject: 'Fixed Income (Part 1)', vol: 6, modules: [1,2,3,4,5,6,7,8,9,10], phase: 'learn', detail: 'Instrument Features, Valuation, Yields' },
    { week: 10, start: '2026-08-24', subject: 'Fixed Income (Part 2)', vol: 6, modules: [11,12,13,14,15,16,17,18,19], phase: 'learn', detail: 'Duration, Convexity, Credit, Securitization' },
    { week: 11, start: '2026-08-31', subject: 'Derivatives + Alts + Portfolio Mgmt', vol: null, modules: [], phase: 'learn', detail: 'Vol 7 (10 mods) + Vol 8 (7 mods) + Vol 9 (6 mods)', multiVol: [{vol:7,modules:[1,2,3,4,5,6,7,8,9,10]},{vol:8,modules:[1,2,3,4,5,6,7]},{vol:9,modules:[1,2,3,4,5,6]}] },
    { week: 12, start: '2026-09-07', subject: 'Heavy Practice', vol: null, modules: [], phase: 'practice', detail: '50+ questions/day, flashcards, revisit weak areas' },
    { week: 13, start: '2026-09-14', subject: 'Mini Mocks + Weak Topics', vol: null, modules: [], phase: 'practice', detail: '2-3 mini mock exams, deep-dive lowest scores' },
    { week: 14, start: '2026-09-21', subject: 'Full Mock Exams', vol: null, modules: [], phase: 'practice', detail: '2 full 180-question timed mock exams' },
    { week: 15, start: '2026-09-28', subject: 'Ethics Re-read + Formula Review', vol: 10, modules: [1,2,3,4,5], phase: 'review', detail: 'Re-read all Ethics + memorize key formulas' },
    { week: 16, start: '2026-10-05', subject: 'Final Polish', vol: null, modules: [], phase: 'review', detail: 'Light review, flashcards, 1 mini mock, REST' },
];

const EXAM_WEIGHTS = [
    { subject: 'Ethical & Professional Standards', weight: 17.5, color: '#e91e63', vol: 10 },
    { subject: 'Financial Statement Analysis', weight: 12.5, color: '#fbbc04', vol: 4 },
    { subject: 'Equity Investments', weight: 12.5, color: '#9c27b0', vol: 5 },
    { subject: 'Fixed Income', weight: 12.5, color: '#ff6d00', vol: 6 },
    { subject: 'Portfolio Management', weight: 10, color: '#607d8b', vol: 9 },
    { subject: 'Alternative Investments', weight: 8.5, color: '#795548', vol: 8 },
    { subject: 'Quantitative Methods', weight: 7.5, color: '#4285f4', vol: 1 },
    { subject: 'Economics', weight: 7.5, color: '#ea4335', vol: 2 },
    { subject: 'Corporate Issuers', weight: 7.5, color: '#34a853', vol: 3 },
    { subject: 'Derivatives', weight: 6.5, color: '#00bcd4', vol: 7 },
];

function getCurrentWeek() {
    const now = new Date();
    const diffMs = now - PLAN_START;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    return Math.max(1, Math.min(16, Math.floor(diffDays / 7) + 1));
}

function getDaysToExam() {
    const now = new Date();
    const diffMs = EXAM_DATE - now;
    return Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)));
}

function getWeekModuleKeys(weekData) {
    const keys = [];
    if (weekData.multiVol) {
        weekData.multiVol.forEach(mv => {
            mv.modules.forEach(m => keys.push(`${mv.vol}-${m}`));
        });
    } else if (weekData.vol) {
        weekData.modules.forEach(m => keys.push(`${weekData.vol}-${m}`));
    }
    return keys;
}

function renderStudyPlan() {
    const progress = getProgress();
    const currentWeek = getCurrentWeek();
    const daysLeft = getDaysToExam();
    const dayOfWeek = new Date().getDay();
    const isMonThu = dayOfWeek >= 1 && dayOfWeek <= 4;
    const isFriday = dayOfWeek === 5;
    const isSaturday = dayOfWeek === 6;
    const isSunday = dayOfWeek === 0;
    const isWeekday = isMonThu;

    document.getElementById('planDaysLeft').textContent = daysLeft;

    const weekData = STUDY_SCHEDULE.find(w => w.week === currentWeek) || STUDY_SCHEDULE[0];
    const phaseName = weekData.phase === 'learn' ? 'PHASE 1: LEARN' :
                      weekData.phase === 'practice' ? 'PHASE 2: PRACTICE' : 'PHASE 3: FINAL REVIEW';
    const phaseClass = weekData.phase === 'learn' ? 'phase-learn' :
                       weekData.phase === 'practice' ? 'phase-practice' : 'phase-review';
    const badge = document.getElementById('planPhaseBadge');
    badge.textContent = phaseName;
    badge.className = 'plan-phase-badge ' + phaseClass;

    let todayHtml = '';
    if (weekData.phase === 'learn') {
        const modKeys = getWeekModuleKeys(weekData);
        const unread = modKeys.filter(k => !progress.readModules[k]);
        const nextMod = unread[0];
        const nextModTitle = nextMod ? getModuleTitle(nextMod) : 'Review today\'s topic';

        if (isFriday) {
            todayHtml += buildTaskBlock('Friday — Rest Day', 'break', [
                { time: 'All evening', desc: 'No study today. Rest, recharge, socialize. Sustainable effort beats burnout.' },
            ]);
        } else if (isMonThu) {
            todayHtml += buildTaskBlock('Evening Study (8:15 - 9:45 PM)', 'read', [
                { time: '8:15 - 8:30 PM', desc: 'Watch tutor video for ' + nextModTitle + ' (letmeexplain.eu)' },
                { time: '8:30 - 9:15 PM', desc: nextModTitle + ' - read actively, underline key terms & formulas' },
                { time: '9:15 - 9:45 PM', desc: '10 practice questions on today\'s reading - no notes' },
            ], nextMod);
        } else if (isSaturday) {
            todayHtml += buildTaskBlock('Deep Study (9:00 - 11:30 AM)', 'read', [
                { time: '9:00 - 9:30 AM', desc: 'Watch all tutor videos for ' + nextModTitle + ' (letmeexplain.eu)' },
                { time: '9:30 - 10:15 AM', desc: nextModTitle + ' - read fully, take handwritten notes on key concepts' },
                { time: '10:15 - 10:30 AM', desc: 'Break - walk around, hydrate, rest your eyes' },
                { time: '10:30 - 11:00 AM', desc: unread[1] ? 'Watch tutor videos + read ' + getModuleTitle(unread[1]) : 'Re-watch difficult video sections, create mental models' },
                { time: '11:00 - 11:30 AM', desc: unread[1] ? getModuleTitle(unread[1]) + ' - note formulas & definitions' : 'Re-read difficult sections from the reading' },
            ], nextMod);
            todayHtml += buildTaskBlock('Practice (1:00 - 3:00 PM)', 'practice', [
                { time: '1:00 - 1:45 PM', desc: '25 questions on this week\'s topics - simulate exam conditions' },
                { time: '1:45 - 2:15 PM', desc: 'Review every wrong answer: re-read explanations, note mistake patterns' },
                { time: '2:15 - 2:30 PM', desc: 'Break' },
                { time: '2:30 - 3:00 PM', desc: '15 mixed questions from all studied topics' },
            ]);
        } else {
            todayHtml += buildTaskBlock('Review + Flashcards (9:00 - 10:30 AM)', 'flashcard', [
                { time: '9:00 - 9:30 AM', desc: 'Flashcard session: clear entire due queue' },
                { time: '9:30 - 10:15 AM', desc: 'Review queue: re-watch tutor videos + re-read flagged topics' },
                { time: '10:15 - 10:30 AM', desc: 'Write key formulas from memory, check against notes' },
            ]);
            todayHtml += buildTaskBlock('Practice + Planning (1:00 - 3:00 PM)', 'practice', [
                { time: '1:00 - 1:45 PM', desc: '25 mixed questions across all studied topics' },
                { time: '1:45 - 2:15 PM', desc: 'Deep review of wrong answers, re-watch relevant tutor videos' },
                { time: '2:15 - 2:30 PM', desc: 'Break' },
                { time: '2:30 - 3:00 PM', desc: 'Review week\'s progress, plan next week\'s modules and targets' },
            ]);
        }
    } else if (weekData.phase === 'practice') {
        if (isFriday) {
            todayHtml += buildTaskBlock('Friday — Rest Day', 'break', [
                { time: 'All evening', desc: 'No study today. Rest and recharge for the weekend practice blocks.' },
            ]);
        } else if (currentWeek === 14 && isSaturday) {
            todayHtml += buildTaskBlock('Full Mock Exam Day', 'mock', [
                { time: '8:00 - 10:15 AM', desc: 'Session 1: 90 questions in 2h15m - full exam conditions, no breaks' },
                { time: '10:15 - 10:30 AM', desc: 'Break - exactly 30 min like the real exam' },
                { time: '10:30 - 12:45 PM', desc: 'Session 2: 90 questions in 2h15m - push through fatigue' },
                { time: '2:00 - 3:30 PM', desc: 'Review every wrong answer - categorize mistakes by topic' },
                { time: '3:30 - 4:30 PM', desc: 'Deep-dive the 2-3 weakest subjects from the mock results' },
            ]);
        } else if (isMonThu) {
            todayHtml += buildTaskBlock('Intensive Practice (8:30 - 9:45 PM)', 'practice', [
                { time: '8:30 - 9:10 PM', desc: '20 questions on weakest subject - timed, 1.5 min per question' },
                { time: '9:10 - 9:30 PM', desc: 'Review wrong answers - trace each mistake to a specific concept gap' },
                { time: '9:30 - 9:45 PM', desc: 'Re-read source material for any concept you couldn\'t explain clearly' },
            ]);
        } else if (isSaturday) {
            todayHtml += buildTaskBlock('Heavy Practice (9:00 AM - 1:00 PM)', 'practice', [
                { time: '9:00 - 9:45 AM', desc: '25 questions on weakest subject - identify recurring mistake patterns' },
                { time: '9:45 - 10:15 AM', desc: 'Review wrong answers, re-read relevant sections' },
                { time: '10:15 - 10:30 AM', desc: 'Break' },
                { time: '10:30 - 11:15 AM', desc: '25 mixed-subject questions under timed conditions (1.5 min each)' },
                { time: '11:15 - 11:45 AM', desc: 'Deep review: for each wrong answer, write why the correct answer is right' },
                { time: '11:45 AM - 1:00 PM', desc: 'Re-study the 2 topics you scored lowest on - go back to theory' },
            ]);
        } else {
            todayHtml += buildTaskBlock('Sunday Practice + Review (9:00 AM - 12:30 PM)', 'practice', [
                { time: '9:00 - 9:45 AM', desc: 'Mini mock: 45 questions, 60 min - full exam discipline' },
                { time: '9:45 - 10:30 AM', desc: 'Score and review every wrong answer thoroughly' },
                { time: '10:30 - 10:45 AM', desc: 'Break' },
                { time: '10:45 - 11:30 AM', desc: 'Targeted practice: 20 questions only from weak areas' },
                { time: '11:30 AM - 12:00 PM', desc: 'Flashcards: all due cards + cards from today\'s mistakes' },
                { time: '12:00 - 12:30 PM', desc: 'Plan next week, update weak topic tracker' },
            ]);
        }
    } else {
        if (isFriday) {
            todayHtml += buildTaskBlock('Friday — Rest Day', 'break', [
                { time: 'All evening', desc: 'Light rest. You\'re in the final stretch — trust your preparation.' },
            ]);
        } else if (isMonThu) {
            todayHtml += buildTaskBlock(currentWeek === 15 ? 'Ethics Re-read + Review (8:30 - 9:45 PM)' : 'Final Polish (8:30 - 9:45 PM)', currentWeek === 15 ? 'read' : 'practice', [
                { time: '8:30 - 9:15 PM', desc: currentWeek === 15 ? 'Re-read one Ethics module slowly - focus on Standards of Practice' : 'Light 15-question mixed quiz - stay sharp without burning out' },
                { time: '9:15 - 9:45 PM', desc: currentWeek === 15 ? 'Practice 15 Ethics questions - these are the most reliable marks' : 'Relax, review summary notes - trust your preparation' },
            ]);
        } else if (isSaturday) {
            todayHtml += buildTaskBlock(currentWeek === 15 ? 'Ethics + Formulas Deep Review (9:00 AM - 1:00 PM)' : 'Final Saturday (9:00 AM - 12:00 PM)', currentWeek === 15 ? 'read' : 'flashcard', [
                { time: '9:00 - 10:00 AM', desc: currentWeek === 15 ? 'Re-read Ethics modules - take fresh notes on Standards' : 'Complete flashcard review - clear entire due queue' },
                { time: '10:00 - 10:15 AM', desc: 'Break' },
                { time: '10:15 - 11:15 AM', desc: currentWeek === 15 ? 'Write all formulas from memory, check, repeat the ones you missed' : 'One final mini mock (45 questions) - assess overall readiness' },
                { time: '11:15 AM - 12:00 PM', desc: currentWeek === 15 ? '25 Ethics practice questions - aim for 90%+' : 'Review results - note any last-minute gaps but don\'t panic' },
            ]);
        } else {
            todayHtml += buildTaskBlock(currentWeek === 15 ? 'Sunday: Ethics Practice (9:00 - 12:00 PM)' : 'Rest & Confidence (Sunday)', currentWeek === 15 ? 'practice' : 'flashcard', [
                { time: '9:00 - 9:45 AM', desc: currentWeek === 15 ? 'Mixed practice: 25 questions across all subjects' : 'Light review of summary notes only - no new material' },
                { time: '9:45 - 10:30 AM', desc: currentWeek === 15 ? 'Review wrong answers, final formula check' : 'Rest, exercise, or do something enjoyable - you\'ve earned it' },
                { time: '10:30 - 11:00 AM', desc: currentWeek === 15 ? 'Update weak areas list, plan final week priorities' : 'Early night - good sleep is the best exam prep now' },
            ]);
        }
    }
    document.getElementById('planTodayTasks').innerHTML = todayHtml;

    document.getElementById('planWeekNum').textContent = `Week ${currentWeek}`;
    document.getElementById('planWeekSubject').textContent = weekData.subject;

    const weekModKeys = getWeekModuleKeys(weekData);
    const weekRead = weekModKeys.filter(k => progress.readModules[k]).length;
    const weekTotal = weekModKeys.length;
    const weekPct = weekTotal > 0 ? Math.round((weekRead / weekTotal) * 100) : (weekData.phase !== 'learn' ? 0 : 0);
    document.getElementById('planWeekBar').style.width = weekPct + '%';
    document.getElementById('planWeekPct').textContent = weekTotal > 0 ? weekPct + '%' : weekData.phase !== 'learn' ? 'N/A' : '0%';

    let modsHtml = '';
    if (weekModKeys.length > 0) {
        weekModKeys.forEach(key => {
            const isDone = progress.readModules[key];
            const title = getModuleTitle(key);
            const [v, m] = key.split('-').map(Number);
            const vc = getVideoCount(key);
            modsHtml += `<div class="plan-mod" onclick="openModule(${v},${m})">
                <span class="mod-check ${isDone ? 'done' : 'pending'}">${isDone ? '&#10003;' : '&#9675;'}</span>
                <span>${title}</span>
                ${vc > 0 ? `<span class="mod-video-count">&#9654; ${vc}</span>` : ''}
            </div>`;
        });
        const weekVol = weekData.multiVol ? weekData.multiVol[0].vol : weekData.vol;
        if (weekVol) {
            modsHtml += `<div class="plan-week-actions">
                <button class="btn-sm" onclick="openFirstModuleOfVolume(${weekVol})">Study Material</button>
                <button class="btn-sm" onclick="startPracticeForSubject(${weekVol})">Practice Questions</button>
                <button class="btn-sm" onclick="showView('flashcards')">Flashcards</button>
            </div>`;
        }
    } else {
        const actionView = weekData.phase === 'practice' ? 'practice' : weekData.phase === 'review' ? 'review' : 'study';
        modsHtml = `<p style="font-size:13px;color:var(--text-secondary);padding:8px;">${weekData.detail}</p>
            <div class="plan-week-actions">
                <button class="btn-sm" onclick="showView('${actionView}')">${weekData.phase === 'practice' ? 'Start Practice' : weekData.phase === 'review' ? 'Open Review Queue' : 'Open Study'}</button>
                <button class="btn-sm" onclick="showView('exam')">Mock Exam</button>
                <button class="btn-sm" onclick="showView('flashcards')">Flashcards</button>
            </div>`;
    }
    document.getElementById('planWeekModules').innerHTML = modsHtml;

    let routineHtml = `
        <div class="routine-block weekday">
            <div class="routine-header-bar">
                <h4>Monday &ndash; Thursday</h4>
                <div class="routine-stats">
                    <span class="routine-stat"><span class="routine-stat-num">1.5</span> hrs study</span>
                    <span class="routine-stat-sep">&middot;</span>
                    <span class="routine-stat"><span class="routine-stat-num">3</span> sessions</span>
                </div>
            </div>
            <div class="routine-timeline">
                <div class="routine-block-group routine-block-muted">
                    <div class="routine-item routine-disabled"><span class="ri-time">7:30AM - 7:30PM</span><span>Work</span></div>
                    <div class="routine-item routine-disabled"><span class="ri-time">7:30 - 8:30 PM</span><span>Dinner, decompress, rest</span></div>
                </div>
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-read">PM</span> Evening Study (~1.5 hrs)</div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">8:15 - 8:30 PM</span><span>Watch tutor video for today's module (letmeexplain.eu)</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">8:30 - 9:15 PM</span><span>Read module section, take notes on key terms</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">9:15 - 9:45 PM</span><span>10 practice questions on today's reading</span><span class="ri-go">&#8594;</span></div>
                </div>
            </div>
        </div>
        <div class="routine-block" style="background:#f8f8f8;border-left:3px solid #d1d5db;">
            <div class="routine-header-bar">
                <h4>Friday &mdash; REST DAY</h4>
                <div class="routine-stats">
                    <span class="routine-stat" style="color:var(--cfa-green);">No study</span>
                </div>
            </div>
            <div class="routine-timeline">
                <div class="routine-block-group routine-block-muted">
                    <div class="routine-item routine-disabled"><span class="ri-time">All day</span><span>Rest, recharge, socialize. Sustainable effort beats burnout.</span></div>
                </div>
            </div>
        </div>
        <div class="routine-block weekend">
            <div class="routine-header-bar">
                <h4>Saturday &mdash; Deep Study</h4>
                <div class="routine-stats">
                    <span class="routine-stat"><span class="routine-stat-num">4.5</span> hrs study</span>
                    <span class="routine-stat-sep">&middot;</span>
                    <span class="routine-stat"><span class="routine-stat-num">3</span> sessions</span>
                </div>
            </div>
            <div class="routine-timeline">
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-read">AM</span> Watch + Deep Read (2.5 hrs)</div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">9:00 - 9:30 AM</span><span>Watch all tutor videos for Module 1 (letmeexplain.eu)</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">9:30 - 10:15 AM</span><span>Read Module 1: concepts, notes, formulas</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-disabled"><span class="ri-time">10:15 - 10:30 AM</span><span>Break</span></div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">10:30 - 11:00 AM</span><span>Watch videos + read Module 2</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('study')"><span class="ri-time">11:00 - 11:30 AM</span><span>Finish reading, note formulas & definitions</span><span class="ri-go">&#8594;</span></div>
                </div>
                <div class="routine-sub">Lunch break: 11:00 AM - 1:00 PM</div>
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-practice">PM</span> Practice (2 hrs)</div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">1:00 - 1:45 PM</span><span>25 questions on this week's topics (timed)</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">1:45 - 2:15 PM</span><span>Review wrong answers, note mistake patterns</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-disabled"><span class="ri-time">2:15 - 2:30 PM</span><span>Break</span></div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">2:30 - 3:00 PM</span><span>15 mixed questions from all studied topics</span><span class="ri-go">&#8594;</span></div>
                </div>
            </div>
        </div>
        <div class="routine-block weekend">
            <div class="routine-header-bar">
                <h4>Sunday &mdash; Review + Planning</h4>
                <div class="routine-stats">
                    <span class="routine-stat"><span class="routine-stat-num">3.5</span> hrs study</span>
                    <span class="routine-stat-sep">&middot;</span>
                    <span class="routine-stat"><span class="routine-stat-num">3</span> sessions</span>
                </div>
            </div>
            <div class="routine-timeline">
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-flashcard">AM</span> Flashcards + Video Review (1.5 hrs)</div>
                    <div class="routine-item routine-link" onclick="showView('flashcards')"><span class="ri-time">9:00 - 9:30 AM</span><span>Flashcards: clear entire due queue</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('review')"><span class="ri-time">9:30 - 10:15 AM</span><span>Re-watch tutor videos + re-read flagged topics from the week</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item"><span class="ri-time">10:15 - 10:30 AM</span><span>Write key formulas from memory, check against notes</span></div>
                </div>
                <div class="routine-sub">Break: 10:30 AM - 1:00 PM</div>
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-practice">PM</span> Practice (1.5 hrs)</div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">1:00 - 1:45 PM</span><span>25 mixed questions across all studied topics</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-link" onclick="showView('practice')"><span class="ri-time">1:45 - 2:15 PM</span><span>Deep review of wrong answers, revisit source material</span><span class="ri-go">&#8594;</span></div>
                    <div class="routine-item routine-disabled"><span class="ri-time">2:15 - 2:30 PM</span><span>Break</span></div>
                </div>
                <div class="routine-block-group">
                    <div class="routine-block-label"><span class="rbl-icon type-read">PM</span> Planning (30 min)</div>
                    <div class="routine-item"><span class="ri-time">2:30 - 3:00 PM</span><span>Review week's progress, plan next week's modules and targets</span></div>
                </div>
            </div>
        </div>`;
    document.getElementById('planDailyRoutine').innerHTML = routineHtml;

    let scheduleHtml = '';
    STUDY_SCHEDULE.forEach(w => {
        const wStart = new Date(w.start);
        const wEnd = new Date(wStart); wEnd.setDate(wEnd.getDate() + 6);
        const startStr = wStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const endStr = wEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

        const isCurrentWeek = w.week === currentWeek;
        const isCompleted = w.week < currentWeek;
        const isFuture = w.week > currentWeek;
        const stateClass = isCurrentWeek ? 'current' : isCompleted ? 'completed' : 'future';

        const phaseLabel = w.phase === 'learn' ? 'LEARN' : w.phase === 'practice' ? 'PRACTICE' : 'REVIEW';
        const phaseColor = w.phase === 'learn' ? 'phase-learn' : w.phase === 'practice' ? 'phase-practice' : 'phase-review';

        const wKeys = getWeekModuleKeys(w);
        const wRead = wKeys.filter(k => progress.readModules[k]).length;
        const wTotal = wKeys.length;
        const wPct = wTotal > 0 ? Math.round((wRead / wTotal) * 100) : 0;

        const weekAction = buildWeekAction(w, progress);
        scheduleHtml += `
            <div class="schedule-week ${stateClass}${weekAction ? ' schedule-week-link' : ''}" ${weekAction}>
                <div class="sw-header">
                    <span class="sw-week">Week ${w.week}</span>
                    <span class="sw-phase ${phaseColor}">${phaseLabel}</span>
                </div>
                <div class="sw-dates">${startStr} - ${endStr}</div>
                <div class="sw-subject">${w.subject}</div>
                <div class="sw-detail">${w.detail}</div>
                ${wTotal > 0 ? `<div class="sw-progress"><div class="sw-progress-fill" style="width:${wPct}%"></div></div>` : ''}
                ${weekAction ? '<div class="sw-action-hint">Click to start &#8594;</div>' : ''}
            </div>`;
    });
    document.getElementById('planScheduleGrid').innerHTML = scheduleHtml;

    let weightHtml = '';
    EXAM_WEIGHTS.forEach(ew => {
        const maxW = 20;
        const barPct = (ew.weight / maxW) * 100;
        const vol = cfaData.find(v => v.volume === ew.vol);
        const volRead = vol ? vol.chapters.filter(ch => progress.readModules[`${vol.volume}-${ch.chapter}`]).length : 0;
        const volTotal = vol ? vol.chapters.length : 0;
        const volPct = volTotal > 0 ? Math.round((volRead / volTotal) * 100) : 0;
        weightHtml += `
            <div class="weight-row weight-row-link">
                <div class="weight-label" onclick="openFirstModuleOfVolume(${ew.vol})" title="Open study material">${ew.subject}</div>
                <div class="weight-bar-track">
                    <div class="weight-bar-fill" style="width:${barPct}%;background:${ew.color}">${ew.weight}%</div>
                </div>
                <div class="weight-progress-mini">${volPct}% read</div>
                <div class="weight-actions">
                    <button class="btn-sm weight-action-btn" onclick="openFirstModuleOfVolume(${ew.vol})" title="Study this subject">Study</button>
                    <button class="btn-sm weight-action-btn" onclick="startPracticeForSubject(${ew.vol})" title="Practice questions">Practice</button>
                </div>
            </div>`;
    });
    document.getElementById('planWeightChart').innerHTML = weightHtml;
}

// --- SYLLABUS ---
const WEEK_TIPS = {
    1:  { pace: '1 module/evening', focus: 'Ethics is the highest-weighted topic (15-20%) AND a tiebreaker near the pass/fail line. Read every Standard carefully. Week 15 will be your second pass.', keyTopics: 'Code of Ethics, Standards I-VII, GIPS basics', warn: '' },
    2:  { pace: '1-2 modules/evening + 2 on Saturday', focus: 'Build your quantitative foundation. TVM and statistics underpin almost every other subject. Master the calculator sequences now.', keyTopics: 'Time Value of Money, Mean/Variance/Skewness, Probability distributions', warn: '' },
    3:  { pace: '1-2 modules/evening + 2 on Saturday', focus: 'Hypothesis testing and regression are heavily tested. Focus on when to use each test and interpreting p-values and confidence intervals.', keyTopics: 'Hypothesis testing, t-tests vs z-tests, Simple linear regression, R-squared', warn: '' },
    4:  { pace: '2 modules/evening + 2-3 on Saturday', focus: 'Economics is broad but exam questions tend to be conceptual. Focus on understanding cause-and-effect chains rather than memorizing details.', keyTopics: 'Market structures, GDP components, Monetary vs fiscal policy, Exchange rate regimes', warn: '' },
    5:  { pace: '1-2 modules/evening + 2 on Saturday', focus: 'FSA is a cornerstone topic (12.5% weight). Build a rock-solid understanding of the three financial statements and how they connect.', keyTopics: 'Income statement structure, Balance sheet equation, Cash flow from operations (direct vs indirect)', warn: 'Do NOT rush FSA. If you fall behind, borrow from Derivatives/Alts — never from here.' },
    6:  { pace: '1-2 modules/evening + 2 on Saturday', focus: 'FSA Part 2 gets into the analytical techniques that examiners love to test. Reporting quality and financial modeling are high-yield topics.', keyTopics: 'Depreciation methods, Deferred taxes, Financial reporting red flags, Ratio analysis', warn: '' },
    7:  { pace: '1-2 modules/evening + 2 on Saturday', focus: 'Corporate Issuers is relatively lighter weight (7.5%) but straightforward marks. Focus on governance conflicts and capital budgeting decisions.', keyTopics: 'Agency conflicts, NPV/IRR, WACC, Capital structure theories', warn: '' },
    8:  { pace: '2 modules/evening + 2 on Saturday', focus: 'Equity Investments (12.5% weight) bridges theory and valuation. Understand market structure first, then build up to the valuation models.', keyTopics: 'Market indexes, EMH, DDM and multiples, Industry analysis frameworks', warn: '' },
    9:  { pace: '2-3 modules/evening + 3 on Saturday', focus: 'Fixed Income Part 1 is dense with new terminology. Take time with bond pricing math and yield curves — these are foundational for Part 2.', keyTopics: 'Bond features, Day-count conventions, Spot rates vs YTM, Term structure theories', warn: 'Heavy week — 10 modules. Prioritize understanding bond valuation mechanics.' },
    10: { pace: '2 modules/evening + 3 on Saturday', focus: 'Duration, convexity, and credit analysis are heavily tested. Practice the calculations until they are automatic.', keyTopics: 'Macaulay vs modified duration, Convexity adjustment, Credit spreads, ABS/MBS', warn: '' },
    11: { pace: '3-4 modules/evening + 5-6 on Saturday', focus: 'Heaviest week: 23 modules across 3 subjects. These are lower-weight topics so focus on key concepts, not exhaustive detail. Skim where needed.', keyTopics: 'Forwards/futures/options basics, Put-call parity, Real estate/hedge funds, Portfolio risk/return, CAPM', warn: 'This is a sprint week. Prioritize understanding the core concept of each module over reading every paragraph.' },
    12: { pace: '50+ questions/day', focus: 'Phase 2 begins. Stop reading new material. Your sole focus is drilling questions, identifying weak areas, and closing gaps.', keyTopics: 'All subjects — focus on areas where you score below 70%', warn: '' },
    13: { pace: '2-3 mini mocks this week', focus: 'Take 2-3 timed mini mocks (45 questions, 60 min). After each one, deep-dive your worst 2-3 subjects.', keyTopics: 'Weak areas from mock results', warn: '' },
    14: { pace: '1 full mock on Saturday', focus: 'Do at least one full 180-question mock under real exam conditions: 4.5 hours, timed, no breaks between sessions. Target 70%+.', keyTopics: 'Full exam simulation — endurance and time management', warn: 'Save the official CFA Institute mock for this week or Week 15.' },
    15: { pace: '1 Ethics module/evening', focus: 'Re-read ALL Ethics modules with fresh eyes. This is your tiebreaker topic. Also drill key formulas from every subject.', keyTopics: 'Standards of Practice, GIPS, All key formulas from Quant/FI/Equity', warn: 'This week is NON-NEGOTIABLE. Do not let mock review squeeze out Ethics.' },
    16: { pace: 'Light review only', focus: 'Taper down. One light mini mock early in the week, then flashcards only. Rest before the exam. Trust your 15 weeks of preparation.', keyTopics: 'Confidence check — skim, don\'t cram', warn: 'No new material. Sleep well. You are ready.' },
};

function renderSyllabus() {
    const progress = getProgress();
    const currentWeek = getCurrentWeek();

    const totalMods = cfaData.reduce((s, v) => s + v.chapters.length, 0);
    const readCount = Object.keys(progress.readModules).length;
    const learnWeeks = STUDY_SCHEDULE.filter(w => w.phase === 'learn');
    const learnMods = learnWeeks.reduce((s, w) => s + getWeekModuleKeys(w).length, 0);
    const learnRead = learnWeeks.reduce((s, w) => s + getWeekModuleKeys(w).filter(k => progress.readModules[k]).length, 0);

    document.getElementById('syllabusStats').innerHTML = `
        <div class="syl-stat"><span class="syl-stat-num">${totalMods}</span><span class="syl-stat-label">Total Modules</span></div>
        <div class="syl-stat"><span class="syl-stat-num">${readCount}</span><span class="syl-stat-label">Completed</span></div>
        <div class="syl-stat"><span class="syl-stat-num">${totalMods - readCount}</span><span class="syl-stat-label">Remaining</span></div>
        <div class="syl-stat"><span class="syl-stat-num">${learnMods > 0 ? Math.round((learnRead / learnMods) * 100) : 0}%</span><span class="syl-stat-label">Learn Phase</span></div>
    `;

    let walkthroughHtml = `
        <div class="syl-topnav">
            <div>
                <h2>Your Study Plan Walkthrough</h2>
                <p>Your 16-week plan is split into three phases. Here is exactly what to do and when.</p>
            </div>
            <div class="syl-topnav-links">
                <button class="btn-sm" onclick="showView('plan')">&#9776; Daily Plan &amp; Routine</button>
                <button class="btn-sm" onclick="showView('study')">&#9733; Study</button>
                <button class="btn-sm" onclick="showView('practice')">&#9998; Practice</button>
                <button class="btn-sm" onclick="showView('exam')">&#9201; Mock Exam</button>
                <button class="btn-sm" onclick="printTimetable()">&#128424; Print Timetable</button>
            </div>
        </div>
        <div class="syl-phases">
            <div class="syl-phase-card syl-phase-learn">
                <div class="syl-phase-icon">1</div>
                <div>
                    <h4>LEARN (Weeks 1-11)</h4>
                    <p>Watch tutor videos + read all 94 modules. Mon-Thu: video + 1 module/evening (~1.5h). Saturday: deep study (~4.5h, 2-3 modules). Sunday: review + practice. Friday: rest.</p>
                </div>
            </div>
            <div class="syl-phase-card syl-phase-practice">
                <div class="syl-phase-icon">2</div>
                <div>
                    <h4>PRACTICE (Weeks 12-14)</h4>
                    <p>No new reading. Drill 50+ questions/day, take mini mocks and full mocks. Target 70%+ on every subject. Deep-dive your weakest areas.</p>
                </div>
            </div>
            <div class="syl-phase-card syl-phase-review">
                <div class="syl-phase-icon">3</div>
                <div>
                    <h4>FINAL REVIEW (Weeks 15-16)</h4>
                    <p>Re-read all Ethics (tiebreaker). Memorize key formulas. One last mini mock. Then taper and rest. Trust your preparation.</p>
                </div>
            </div>
        </div>
    `;
    document.getElementById('syllabusWalkthrough').innerHTML = walkthroughHtml;

    let html = '';
    const phaseLabels = { learn: 'LEARN', practice: 'PRACTICE', review: 'REVIEW' };
    const phaseColors = { learn: '#1e40af', practice: '#92400e', review: '#065f46' };
    let lastPhase = '';

    STUDY_SCHEDULE.forEach(week => {
        if (week.phase !== lastPhase) {
            if (lastPhase) html += '</div>';
            const phaseTitle = week.phase === 'learn' ? 'Phase 1: Learn New Material' :
                               week.phase === 'practice' ? 'Phase 2: Practice & Mock Exams' :
                               'Phase 3: Final Review';
            html += `<div class="syl-phase-section">
                <div class="syl-phase-divider">
                    <span class="syl-phase-divider-badge" style="background:${phaseColors[week.phase]}">${phaseTitle}</span>
                </div>`;
            lastPhase = week.phase;
        }

        const wStart = new Date(week.start + 'T00:00:00');
        const wEnd = new Date(wStart); wEnd.setDate(wEnd.getDate() + 6);
        const startStr = wStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const endStr = wEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

        const isCurrent = week.week === currentWeek;
        const isPast = week.week < currentWeek;
        const modKeys = getWeekModuleKeys(week);
        const readKeys = modKeys.filter(k => progress.readModules[k]);
        const weekPct = modKeys.length > 0 ? Math.round((readKeys.length / modKeys.length) * 100) : 0;
        const tips = WEEK_TIPS[week.week] || {};

        const statusClass = isCurrent ? 'syl-week-current' : isPast ? 'syl-week-past' : 'syl-week-future';
        const statusLabel = isCurrent ? 'THIS WEEK' : isPast ? (weekPct === 100 ? 'COMPLETED' : `${weekPct}% DONE`) : 'UPCOMING';
        const statusColor = isCurrent ? 'var(--cfa-gold)' : isPast ? (weekPct === 100 ? 'var(--cfa-green)' : 'var(--cfa-orange)') : 'var(--text-secondary)';

        html += `<div class="syl-week ${statusClass}" id="syl-week-${week.week}">
            <div class="syl-week-header" onclick="toggleSylWeek(this)">
                <div class="syl-week-header-left">
                    <span class="syl-week-arrow">&#9654;</span>
                    <div>
                        <div class="syl-week-title">Week ${week.week}: ${week.subject}</div>
                        <div class="syl-week-dates">${startStr} &ndash; ${endStr} &middot; <span style="color:${statusColor};font-weight:600;">${statusLabel}</span></div>
                    </div>
                </div>
                <div class="syl-week-header-right">
                    ${modKeys.length > 0 ? `<span class="syl-week-count">${readKeys.length}/${modKeys.length} modules</span>` : `<span class="syl-week-count">${phaseLabels[week.phase]}</span>`}
                    ${modKeys.length > 0 ? `<div class="syl-week-minibar"><div class="syl-week-minibar-fill" style="width:${weekPct}%"></div></div>` : ''}
                </div>
            </div>
            <div class="syl-week-body${isCurrent ? ' syl-expanded' : ''}">`;

        if (tips.focus || tips.pace) {
            html += `<div class="syl-tip-card">
                <div class="syl-tip-row">
                    <div class="syl-tip-block">
                        <div class="syl-tip-label">DAILY PACE</div>
                        <div class="syl-tip-value">${tips.pace || 'N/A'}</div>
                    </div>
                    <div class="syl-tip-block syl-tip-block-wide">
                        <div class="syl-tip-label">STRATEGY</div>
                        <div class="syl-tip-value">${tips.focus || ''}</div>
                    </div>
                </div>`;
            if (tips.keyTopics) {
                html += `<div class="syl-tip-row">
                    <div class="syl-tip-block syl-tip-block-wide">
                        <div class="syl-tip-label">KEY TOPICS TO MASTER</div>
                        <div class="syl-tip-value syl-tip-topics">${tips.keyTopics}</div>
                    </div>
                </div>`;
            }
            if (tips.warn) {
                html += `<div class="syl-tip-warn">&#9888; ${tips.warn}</div>`;
            }
            html += `</div>`;
        }

        if (modKeys.length > 0) {
            html += `<div class="syl-mod-grid">`;
            let dayCounter = 0;
            const modsPerDay = week.week === 11 ? 4 : week.week === 9 ? 3 : 2;

            modKeys.forEach((key, idx) => {
                const [v, m] = key.split('-').map(Number);
                const vol = cfaData.find(vd => vd.volume === v);
                const ch = vol ? vol.chapters.find(c => c.chapter === m) : null;
                const title = ch ? ch.title : `Module ${m}`;
                const secCount = ch && ch.sections ? ch.sections.length : 0;
                const isRead = progress.readModules[key];
                const subjectName = vol ? vol.subject : '';

                if (idx % modsPerDay === 0) {
                    dayCounter++;
                    const dayLabel = getDayLabel(dayCounter, week);
                    html += `<div class="syl-day-label">${dayLabel}</div>`;
                }

                const vidCount = getVideoCount(key);
                html += `<div class="syl-mod ${isRead ? 'syl-mod-done' : ''}" onclick="openModule(${v},${m})">
                    <div class="syl-mod-status">${isRead ? '&#10003;' : '&#9675;'}</div>
                    <div class="syl-mod-info">
                        <div class="syl-mod-title">${title}</div>
                        <div class="syl-mod-meta">${subjectName} &middot; ${secCount} sections${vidCount > 0 ? ' &middot; <span style="color:#dc2626;">&#9654; ' + vidCount + ' videos</span>' : ''}</div>
                    </div>
                    <div class="syl-mod-go">&#8594;</div>
                </div>`;
            });
            html += `</div>`;
        } else {
            html += `<div class="syl-no-modules">
                <div class="syl-no-mod-detail">${week.detail}</div>
                <div class="syl-no-mod-actions">
                    ${week.phase === 'practice' ? '<button class="btn-primary" onclick="showView(\'practice\')">Start Practice</button><button class="btn-secondary" onclick="showView(\'exam\')">Mock Exam</button>' : ''}
                    ${week.phase === 'review' ? '<button class="btn-primary" onclick="showView(\'review\')">Review Queue</button><button class="btn-secondary" onclick="showView(\'flashcards\')">Flashcards</button>' : ''}
                </div>
            </div>`;
        }

        html += `<div class="syl-week-actions">
            ${modKeys.length > 0 ? `<button class="btn-sm" onclick="openModule(${modKeys[0].split('-')[0]},${modKeys[0].split('-')[1]})">Start Studying</button>` : ''}
            <button class="btn-sm" onclick="showView('practice')">Practice Questions</button>
            <button class="btn-sm" onclick="showView('flashcards')">Flashcards</button>
        </div>`;

        html += `</div></div>`;
    });
    if (lastPhase) html += '</div>';

    document.getElementById('syllabusContent').innerHTML = html;

    const currentEl = document.getElementById('syl-week-' + currentWeek);
    if (currentEl) {
        setTimeout(() => currentEl.scrollIntoView({ behavior: 'smooth', block: 'start' }), 200);
    }
}

function getDayLabel(dayNum, week) {
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Sat', 'Sun'];
    if (dayNum <= dayNames.length) return dayNames[dayNum - 1];
    return 'Day ' + dayNum;
}

function toggleSylWeek(headerEl) {
    const body = headerEl.nextElementSibling;
    const arrow = headerEl.querySelector('.syl-week-arrow');
    body.classList.toggle('syl-expanded');
    arrow.classList.toggle('syl-arrow-open');
}

function printTimetable() {
    const progress = getProgress();
    const currentWeek = getCurrentWeek();
    const daysLeft = getDaysToExam();

    let weekRows = '';
    STUDY_SCHEDULE.forEach(week => {
        const wStart = new Date(week.start + 'T00:00:00');
        const wEnd = new Date(wStart); wEnd.setDate(wEnd.getDate() + 6);
        const startStr = wStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const endStr = wEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const modKeys = getWeekModuleKeys(week);
        const readKeys = modKeys.filter(k => progress.readModules[k]);

        const phaseTag = week.phase === 'learn' ? '<span class="ph ph-learn">LEARN</span>' :
                         week.phase === 'practice' ? '<span class="ph ph-prac">PRACTICE</span>' :
                         '<span class="ph ph-rev">REVIEW</span>';

        let modList = '';
        if (modKeys.length > 0) {
            const groups = {};
            modKeys.forEach(key => {
                const [v, m] = key.split('-').map(Number);
                const vol = cfaData.find(vd => vd.volume === v);
                const ch = vol ? vol.chapters.find(c => c.chapter === m) : null;
                const subj = vol ? vol.subject : '';
                if (!groups[subj]) groups[subj] = [];
                const done = progress.readModules[key] ? '&#10003;' : '&#9675;';
                groups[subj].push(`<span class="mod-line${progress.readModules[key] ? ' done' : ''}">${done} ${ch ? ch.title : 'Module ' + m}</span>`);
            });
            for (const [subj, mods] of Object.entries(groups)) {
                if (Object.keys(groups).length > 1) {
                    modList += `<div class="subj-label">${subj}</div>`;
                }
                modList += mods.join('');
            }
        } else {
            modList = `<span class="mod-line detail">${week.detail}</span>`;
        }

        const tips = WEEK_TIPS[week.week] || {};
        const isCurrent = week.week === currentWeek;

        weekRows += `
            <tr class="${isCurrent ? 'current-row' : ''} ${week.phase}-row">
                <td class="wk-num">${week.week}</td>
                <td class="wk-dates">${startStr}<br>${endStr}</td>
                <td class="wk-phase">${phaseTag}</td>
                <td class="wk-subject">${week.subject}</td>
                <td class="wk-modules">${modList}</td>
                <td class="wk-pace">${tips.pace || '—'}</td>
                <td class="wk-focus">${tips.keyTopics || '—'}</td>
                <td class="wk-progress">${modKeys.length > 0 ? readKeys.length + '/' + modKeys.length : '—'}</td>
            </tr>`;
    });

    let weightRows = '';
    EXAM_WEIGHTS.forEach(ew => {
        const barW = (ew.weight / 20) * 100;
        weightRows += `<div class="ew-row"><span class="ew-name">${ew.subject}</span><div class="ew-track"><div class="ew-fill" style="width:${barW}%;background:${ew.color}"></div></div><span class="ew-pct">${ew.weight}%</span></div>`;
    });

    const popWin = window.open('', '_blank', 'width=1400,height=900,scrollbars=yes');
    if (!popWin) {
        showToast('Pop-up blocked. Please allow pop-ups to print.');
        return;
    }

    popWin.document.write(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CFA Level I — 16 Week Wall Timetable</title>
<style>
@page { size: landscape; margin: 12mm; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #1a1a2e; line-height: 1.35; background: white; }

.poster { padding: 16px; }

/* Header */
.header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 4px solid #002b5c; padding-bottom: 12px; margin-bottom: 14px; }
.header-left h1 { font-size: 22px; font-weight: 800; color: #002b5c; letter-spacing: -0.5px; }
.header-left p { font-size: 11px; color: #666; margin-top: 2px; }
.header-right { text-align: right; }
.header-right .exam-date { font-size: 18px; font-weight: 800; color: #002b5c; }
.header-right .days-left { font-size: 12px; color: #c5a44e; font-weight: 700; }
.print-btn { background: #002b5c; color: white; border: none; padding: 8px 28px; border-radius: 6px; cursor: pointer; font-family: inherit; font-size: 13px; font-weight: 600; margin-left: 16px; }
.print-btn:hover { background: #003d7a; }

/* Main table */
table { width: 100%; border-collapse: collapse; font-size: 10px; margin-bottom: 16px; }
th { background: #002b5c; color: white; padding: 6px 8px; text-align: left; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; }
td { padding: 5px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
tr:nth-child(even) { background: #f9fafb; }
tr.current-row { background: #fffbeb !important; outline: 2px solid #c5a44e; }
tr.current-row td:first-child { position: relative; }
tr.current-row td:first-child::before { content: '\\25B6'; color: #c5a44e; font-size: 8px; position: absolute; left: 2px; top: 50%; transform: translateY(-50%); }

.learn-row { border-left: 3px solid #1e40af; }
.practice-row { border-left: 3px solid #c5a44e; }
.review-row { border-left: 3px solid #059669; }

.wk-num { font-weight: 800; color: #002b5c; text-align: center; width: 28px; font-size: 12px; }
.wk-dates { font-size: 9px; color: #666; white-space: nowrap; width: 60px; }
.wk-phase { width: 56px; }
.wk-subject { font-weight: 700; color: #002b5c; width: 160px; font-size: 10.5px; }
.wk-modules { width: auto; line-height: 1.45; }
.wk-pace { font-size: 9px; color: #444; width: 80px; font-style: italic; }
.wk-focus { font-size: 9px; color: #1e40af; width: 160px; }
.wk-progress { text-align: center; font-weight: 700; width: 40px; font-size: 10px; }

.ph { padding: 2px 6px; border-radius: 3px; font-size: 8px; font-weight: 800; letter-spacing: 0.5px; }
.ph-learn { background: #dbeafe; color: #1e40af; }
.ph-prac { background: #fef3c7; color: #92400e; }
.ph-rev { background: #d1fae5; color: #065f46; }

.mod-line { display: block; padding: 1px 0; font-size: 9.5px; }
.mod-line.done { color: #999; text-decoration: line-through; }
.mod-line.detail { color: #666; font-style: italic; }
.subj-label { font-size: 8px; font-weight: 700; color: #1e40af; text-transform: uppercase; letter-spacing: 0.3px; margin-top: 3px; padding-top: 2px; border-top: 1px dotted #ddd; }
.subj-label:first-child { border-top: none; margin-top: 0; padding-top: 0; }

/* Bottom panels */
.bottom { display: flex; gap: 16px; margin-top: 4px; }
.panel { flex: 1; border: 1.5px solid #e5e7eb; border-radius: 8px; padding: 12px; }
.panel h3 { font-size: 11px; font-weight: 800; color: #002b5c; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #c5a44e; padding-bottom: 4px; }

/* Daily routine panel */
.day-block { margin-bottom: 8px; }
.day-name { font-size: 10px; font-weight: 800; color: #002b5c; margin-bottom: 2px; }
.day-items { font-size: 9px; color: #444; line-height: 1.5; padding-left: 8px; }
.day-off { color: #059669; font-weight: 600; font-style: italic; }

/* Exam weights panel */
.ew-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.ew-name { font-size: 9px; width: 140px; font-weight: 500; }
.ew-track { flex: 1; height: 10px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.ew-fill { height: 100%; border-radius: 3px; }
.ew-pct { font-size: 9px; font-weight: 700; width: 30px; text-align: right; }

/* Key rules panel */
.rule { font-size: 9.5px; line-height: 1.55; padding: 4px 0; border-bottom: 1px dotted #e5e7eb; color: #333; }
.rule:last-child { border-bottom: none; }
.rule strong { color: #002b5c; }
.rule-warn { color: #92400e; font-weight: 600; }

/* Checkbox row */
.checkbox-row { display: flex; gap: 4px; align-items: center; font-size: 9px; color: #666; margin-top: 8px; }
.cbox { width: 10px; height: 10px; border: 1.5px solid #999; border-radius: 2px; display: inline-block; flex-shrink: 0; }

@media print {
    .print-btn { display: none; }
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}

@media screen {
    .poster { max-width: 1400px; margin: 0 auto; }
}
</style>
</head>
<body>
<div class="poster">
    <div class="header">
        <div class="header-left">
            <h1>CFA Level I &mdash; 16 Week Study Timetable</h1>
            <p>June 22 &ndash; October 12, 2026 &nbsp;|&nbsp; 94 modules + 350+ tutor videos &nbsp;|&nbsp; Mon&ndash;Thu 1.5h &bull; Fri OFF &bull; Sat 4.5h &bull; Sun 3.5h &nbsp;|&nbsp; Videos: letmeexplain.eu</p>
        </div>
        <div class="header-right">
            <div class="exam-date">EXAM: Oct 12, 2026</div>
            <div class="days-left">${daysLeft} days remaining</div>
            <button class="print-btn" onclick="window.print()">Print This Page</button>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Wk</th>
                <th>Dates</th>
                <th>Phase</th>
                <th>Subject</th>
                <th>Modules / Topics</th>
                <th>Daily Pace</th>
                <th>Key Topics</th>
                <th>Done</th>
            </tr>
        </thead>
        <tbody>
            ${weekRows}
        </tbody>
    </table>

    <div class="bottom">
        <div class="panel">
            <h3>Weekly Routine</h3>
            <div class="day-block">
                <div class="day-name">Monday &ndash; Thursday</div>
                <div class="day-items">
                    8:15 &ndash; 8:30 PM &nbsp; Watch tutor video (letmeexplain.eu)<br>
                    8:30 &ndash; 9:15 PM &nbsp; Read module section, take notes<br>
                    9:15 &ndash; 9:45 PM &nbsp; 10 practice questions on today's reading
                </div>
            </div>
            <div class="day-block">
                <div class="day-name day-off">Friday &mdash; REST DAY</div>
                <div class="day-items day-off">No study. Recharge for the weekend.</div>
            </div>
            <div class="day-block">
                <div class="day-name">Saturday &mdash; Deep Study (4.5h)</div>
                <div class="day-items">
                    9:00 &ndash; 9:30 AM &nbsp;&nbsp; Watch tutor videos for module<br>
                    9:30 &ndash; 11:30 AM &nbsp; Read 1&ndash;2 modules in depth<br>
                    1:00 &ndash; 3:00 PM &nbsp;&nbsp; 25+ practice questions + review
                </div>
            </div>
            <div class="day-block">
                <div class="day-name">Sunday &mdash; Review + Plan (3.5h)</div>
                <div class="day-items">
                    9:00 &ndash; 10:30 AM &nbsp; Flashcards + re-watch weak topic videos<br>
                    1:00 &ndash; 3:00 PM &nbsp;&nbsp; 25 mixed questions + plan next week
                </div>
            </div>
            <div class="checkbox-row"><span class="cbox"></span> Formula sheet printed</div>
            <div class="checkbox-row"><span class="cbox"></span> Official CFA mock saved for Wk 14-15</div>
            <div class="checkbox-row"><span class="cbox"></span> Ethics second pass scheduled (Wk 15)</div>
        </div>

        <div class="panel">
            <h3>Exam Weights</h3>
            ${weightRows}
        </div>

        <div class="panel">
            <h3>Key Rules</h3>
            <div class="rule"><strong>&#9888; Ethics is a TIEBREAKER.</strong> Candidates near the minimum passing score get bumped by strong Ethics. Do not coast on it.</div>
            <div class="rule"><strong>Week 15 is non-negotiable.</strong> Full Ethics re-read + formula review. Don't let mocks squeeze it out.</div>
            <div class="rule"><strong>If you fall behind:</strong> borrow time from Derivatives/Alternatives &mdash; <span class="rule-warn">never from FSA, Fixed Income, or Ethics.</span></div>
            <div class="rule"><strong>Practice testing beats passive reading.</strong> After every module, do 10+ questions before moving on.</div>
            <div class="rule"><strong>Target: 70%+</strong> on every mock. Save the official CFA Institute mock for the final 2 weeks &mdash; full 4.5h, timed, no breaks.</div>
            <div class="rule"><strong>Review intervals expand:</strong> 2 &rarr; 4 &rarr; 8 &rarr; 16 days. Trust the spaced repetition system.</div>
            <div class="rule"><strong>Friday is sacred rest.</strong> Sustainable effort over 16 weeks beats heroic sprints that flame out.</div>
        </div>
    </div>
</div>
</body>
</html>`);
    popWin.document.close();
}

function getModuleTitle(key) {
    const [v, m] = key.split('-').map(Number);
    const vol = cfaData.find(vd => vd.volume === v);
    if (!vol) return `Vol ${v} Module ${m}`;
    const ch = vol.chapters.find(c => c.chapter === m);
    return ch ? ch.title : `Module ${m}`;
}

function buildTask(time, desc, type, modKey) {
    const typeLabels = { read: 'Read', practice: 'Practice', flashcard: 'Flashcards', mock: 'Mock Exam' };
    const typeClass = 'type-' + type;
    const onclick = modKey ? `onclick="openModule(${modKey.split('-')[0]},${modKey.split('-')[1]})"` : type === 'practice' ? `onclick="showView('practice')"` : type === 'flashcard' ? `onclick="showView('flashcards')"` : type === 'mock' ? `onclick="showView('exam')"` : '';
    return `<div class="plan-task" ${onclick}>
        <span class="task-time">${time}</span>
        <span class="task-desc">${desc}</span>
        <span class="task-type ${typeClass}">${typeLabels[type]}</span>
    </div>`;
}

function buildTaskBlock(title, type, steps, modKey) {
    const typeLabels = { read: 'Read', practice: 'Practice', flashcard: 'Flashcards', mock: 'Mock Exam', work: 'Work', break: 'Break' };
    const typeClass = 'type-' + type;
    const onclick = modKey ? `onclick="openModule(${modKey.split('-')[0]},${modKey.split('-')[1]})"` : type === 'practice' ? `onclick="showView('practice')"` : type === 'flashcard' ? `onclick="showView('flashcards')"` : type === 'mock' ? `onclick="showView('exam')"` : '';
    let stepsHtml = steps.map(s => {
        const stepAction = resolveStepAction(s, modKey, type);
        return `<div class="task-step${stepAction ? ' task-step-link' : ''}" ${stepAction}><span class="step-time">${s.time}</span><span class="step-desc">${s.desc}</span>${stepAction ? '<span class="step-go">&#8594;</span>' : ''}</div>`;
    }).join('');
    return `<div class="plan-task-block">
        <div class="plan-task-block-header" ${onclick}>
            <span class="task-desc">${title}</span>
            <span class="task-type ${typeClass}">${typeLabels[type] || ''}</span>
        </div>
        <div class="task-steps">${stepsHtml}</div>
    </div>`;
}

function resolveStepAction(step, parentModKey, parentType) {
    const d = step.desc.toLowerCase();
    if (d.includes('break') || d.includes('dinner') || d.includes('rest') || d.includes('relax') || d.includes('commute') || d.includes('work') || d.includes('sleep') || d.includes('plan tomorrow') || d.includes('mental recall') || d.includes('warm-up') || d.includes('warm up') || d.includes('log ') || d.includes('scan')) return '';
    if (d.includes('write') && !d.includes('write all') && !d.includes('write why')) return '';
    if (d.includes('skim') || d.includes('summarize') || (d.includes('note ') && !d.includes('note mistake'))) return '';

    if (d.includes('watch tutor video') || d.includes('watch all tutor') || d.includes('re-watch tutor') || d.includes('re-watch relevant tutor') || d.includes('watch videos +')) {
        if (parentModKey) return `onclick="openModule(${parentModKey.split('-')[0]},${parentModKey.split('-')[1]})"`;
        return 'onclick="showView(\'study\')"';
    }
    if (d.includes('flashcard') || d.includes('formula recall') || d.includes('formula recap') || d.includes('formula sheet') || d.includes('formula drill') || d.includes('formula flash') || d.includes('create flashcard') || d.includes('create 5-10')) return 'onclick="showView(\'flashcards\')"';
    if (d.includes('mock exam') || d.includes('session 1:') || d.includes('session 2:')) return 'onclick="showView(\'exam\')"';
    if (d.includes('review queue') || d.includes('flagged for spaced') || d.includes('re-read any topics flagged') || d.includes('update your review') || d.includes('update weak')) return 'onclick="showView(\'review\')"';

    if (d.includes('practice question') || d.includes('questions on') || d.includes('question') || d.includes('mini mock') || d.includes('mixed question') || d.includes('targeted practice') || d.includes('quiz') || d.includes('mixed practice')) return 'onclick="showView(\'practice\')"';
    if (d.includes('review wrong') || d.includes('review every wrong') || d.includes('deep review') || d.includes('score and review') || d.includes('note mistake') || d.includes('write why the correct')) return 'onclick="showView(\'practice\')"';

    if (d.includes('re-read') || d.includes('re-study') || d.includes('source material') || d.includes('go back to theory') || d.includes('weakest subject') || d.includes('weak areas') || d.includes('deep-dive') || d.includes('revisit source')) return 'onclick="showView(\'study\')"';

    if (d.includes('read module') || d.includes('read fully') || d.includes('read actively') || d.includes('read new') || d.includes('ethics module') || d.includes('take handwritten notes on key concepts') || d.includes('note formulas & definitions')) {
        if (parentModKey) return `onclick="openModule(${parentModKey.split('-')[0]},${parentModKey.split('-')[1]})"`;
        return 'onclick="showView(\'study\')"';
    }

    if (parentModKey && parentType === 'read' && (d.includes('highlight') || d.includes('underline') || d.includes('key concepts') || d.includes('concepts, notes'))) {
        return `onclick="openModule(${parentModKey.split('-')[0]},${parentModKey.split('-')[1]})"`;
    }

    return '';
}

function buildWeekAction(weekData, progress) {
    const modKeys = getWeekModuleKeys(weekData);
    if (modKeys.length > 0) {
        const unread = modKeys.filter(k => !progress.readModules[k]);
        const targetKey = unread.length > 0 ? unread[0] : modKeys[0];
        const [v, m] = targetKey.split('-').map(Number);
        return `onclick="openModule(${v},${m})"`;
    }
    if (weekData.phase === 'practice') return 'onclick="showView(\'practice\')"';
    if (weekData.phase === 'review') return 'onclick="showView(\'review\')"';
    return '';
}

function startPracticeForSubject(volNum) {
    showView('practice');
    document.getElementById('practiceSubject').value = volNum;
    updatePracticeModules();
}

function openFirstModuleOfVolume(volNum) {
    const vol = cfaData.find(v => v.volume === volNum);
    if (vol && vol.chapters.length > 0) {
        openModule(vol.volume, vol.chapters[0].chapter);
    } else {
        showView('study');
    }
}

// --- INITIALIZATION ---
async function init() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = '<div class="spinner"></div><h2>Loading CFA Tutor</h2><p>Preparing your study materials...</p>';
    document.body.appendChild(loadingOverlay);

    try {
        const response = await fetch('cfa_content.json');
        cfaData = await response.json();
    } catch (e) {
        cfaData = [];
        console.error('Could not load content:', e);
    }

    loadingOverlay.remove();
    renderDashboard();
}

init();
