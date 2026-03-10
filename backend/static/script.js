// API конфигурация
const API_BASE = 'http://localhost:8000/api';

// Состояние приложения
let state = {
    currentRunId: null,
    currentRunStatus: null,
    updateInterval: null,
    tests: [],
    history: [],
    selectedTests: []
};

// DOM элементы
const elements = {
    statusBar: document.getElementById('statusBar'),
    statusText: document.getElementById('statusText'),
    metricsGrid: document.getElementById('metricsGrid'),
    testSelector: document.getElementById('testSelector'),
    runAllTests: document.getElementById('runAllTests'),
    refreshTests: document.getElementById('refreshTests'),
    runSelectedTests: document.getElementById('runSelectedTests'),
    markerSelect: document.getElementById('markerSelect'),
    activeRun: document.getElementById('activeRun'),
    progressFill: document.getElementById('progressFill'),
    completedTests: document.getElementById('completedTests'),
    totalTests: document.getElementById('totalTests'),
    runStats: document.getElementById('runStats'),
    historyList: document.getElementById('historyList'),
    historySearch: document.getElementById('historySearch'),
    historyFilter: document.getElementById('historyFilter'),
    runDetails: document.getElementById('runDetails'),
    detailsContent: document.getElementById('detailsContent'),
    closeDetails: document.getElementById('closeDetails'),
    errorModal: document.getElementById('errorModal'),
    errorDetails: document.getElementById('errorDetails'),
    closeModal: document.getElementById('closeModal')
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadTests();
    loadHistory();
    loadRecentResults();
    setupEventListeners();
    updateMetrics();
});

// Настройка обработчиков
function setupEventListeners() {
    elements.runAllTests.addEventListener('click', () => runTests());
    elements.refreshTests.addEventListener('click', loadTests);
    elements.runSelectedTests.addEventListener('click', runSelectedTests);
    elements.historySearch.addEventListener('input', filterHistory);
    elements.historyFilter.addEventListener('change', filterHistory);
    elements.closeDetails.addEventListener('click', () => {
        elements.runDetails.style.display = 'none';
    });
    elements.closeModal.addEventListener('click', () => {
        elements.errorModal.style.display = 'none';
    });

    // Закрытие модалки по клику вне области
    window.addEventListener('click', (e) => {
        if (e.target === elements.errorModal) {
            elements.errorModal.style.display = 'none';
        }
        if (e.target === elements.runDetails) {
            elements.runDetails.style.display = 'none';
        }
    });
    // Кнопка наверх
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollTopBtn.classList.remove('hidden');
            } else {
                scrollTopBtn.classList.add('hidden');
            }
        });
    }
}

// Загрузка списка тестов
async function loadTests() {
    try {
        const response = await fetch(`${API_BASE}/tests/list`);
        const data = await response.json();

        state.tests = data.tests || [];

        // Обновляем селект
        elements.testSelector.innerHTML = '';
        state.tests.forEach(test => {
            const option = document.createElement('option');
            option.value = test.full_name || test.name;
            option.textContent = `${test.class ? test.class + '::' : ''}${test.name}`;
            elements.testSelector.appendChild(option);
        });

        updateStatus('Список тестов обновлен', 'success');
    } catch (error) {
        console.error('Error loading tests:', error);
        updateStatus('Ошибка загрузки тестов', 'error');
    }
}

// Загрузка истории запусков
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/tests/runs?limit=50`);
        state.history = await response.json();

        renderHistory();
        updateMetrics();
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Рендер истории
function renderHistory() {
    const filtered = filterHistoryData();
    elements.historyList.innerHTML = '';

    if (filtered.length === 0) {
        elements.historyList.innerHTML = '<div class="loading">История пуста</div>';
        return;
    }

    filtered.forEach(run => {
        const item = document.createElement('div');
        item.className = `history-item ${run.status}`;
        item.innerHTML = `
            <div class="history-info">
                <span class="history-date">${new Date(run.started_at).toLocaleString()}</span>
                <span class="history-status status-badge ${run.status}">${run.status}</span>
                <span class="history-stats">
                     ${run.passed_tests} |  ${run.failed_tests} | ${run.success_rate}%
                </span>
            </div>
            <span class="history-duration">️ ${formatDuration(run.duration)}</span>
        `;

        item.addEventListener('click', () => showRunDetails(run.id));
        elements.historyList.appendChild(item);
    });
}

// Фильтрация истории
function filterHistoryData() {
    const search = elements.historySearch.value.toLowerCase();
    const filter = elements.historyFilter.value;

    return state.history.filter(run => {
        const matchesSearch = run.id.toString().includes(search);
        const matchesFilter = filter === 'all' || run.status === filter;
        return matchesSearch && matchesFilter;
    });
}

function filterHistory() {
    renderHistory();
}

// Обновление метрик
async function updateMetrics() {
    try {
        const response = await fetch(`${API_BASE}/tests/runs?limit=100`);
        const runs = await response.json();

        const total = runs.length;
        const passed = runs.filter(r => r.status === 'completed').length;
        const failed = runs.filter(r => r.status === 'failed').length;
        const totalTests = runs.reduce((sum, r) => sum + r.total_tests, 0);
        const avgSuccess = runs.length > 0
            ? Math.round(runs.reduce((sum, r) => sum + r.success_rate, 0) / runs.length)
            : 0;

        elements.metricsGrid.innerHTML = `
            <div class="metric-card">
                <div class="metric-title">Всего запусков</div>
                <div class="metric-value">${total}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Успешных</div>
                <div class="metric-value success">${passed}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">С ошибками</div>
                <div class="metric-value danger">${failed}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Всего тестов</div>
                <div class="metric-value">${totalTests}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Ср. успешность</div>
                <div class="metric-value warning">${avgSuccess}%</div>
            </div>
        `;
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

// Запуск всех тестов
async function runTests(options = {}) {
    try {
        // Показываем индикатор загрузки
        updateStatus('Запуск тестов...', 'info');

        const response = await fetch(`${API_BASE}/tests/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                test_names: options.testNames || null,
                markers: options.markers || null,
                parallel: false, // всегда false
                workers: 1
            })
        });

        const data = await response.json();
        state.currentRunId = data.run_id;

        // Показываем активный запуск
        elements.activeRun.style.display = 'block';
        startPollingRunStatus(data.run_id);

    } catch (error) {
        console.error('Error running tests:', error);
        updateStatus('Ошибка запуска тестов', 'error');
    }
}

// Запуск выбранных тестов
function runSelectedTests() {
    const selected = Array.from(elements.testSelector.selectedOptions).map(opt => opt.value);

    if (selected.length === 0) {
        alert('Выберите хотя бы один тест');
        return;
    }

    runTests({
        testNames: selected,
        markers: elements.markerSelect.value ? [elements.markerSelect.value] : null
    });
}

// Поллинг статуса запуска
function startPollingRunStatus(runId) {
    if (state.updateInterval) {
        clearInterval(state.updateInterval);
    }

    state.updateInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/tests/run/${runId}`);
            const data = await response.json();

            updateRunProgress(data);

            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(state.updateInterval);
                state.updateInterval = null;

                // Скрываем активный запуск через 5 секунд
                setTimeout(() => {
                    elements.activeRun.style.display = 'none';
                }, 5000);

                // Обновляем историю
                loadHistory();
                updateMetrics();

                updateStatus(
                    data.status === 'completed' ? ' Тесты успешно завершены' : ' Тесты завершены с ошибками',
                    data.status === 'completed' ? 'success' : 'error'
                );
            }
        } catch (error) {
            console.error('Error polling run status:', error);
        }
    }, 2000);
}

// Обновление прогресса запуска
function updateRunProgress(data) {
    const completed = data.results ? data.results.filter(r => r.status !== 'pending').length : 0;
    const total = data.total || 0;
    const percent = total > 0 ? (completed / total) * 100 : 0;

    elements.progressFill.style.width = `${percent}%`;
    elements.completedTests.textContent = completed;
    elements.totalTests.textContent = total;

    // Обновляем статус
    let statusText = `Статус: ${data.status}`;
    if (data.passed !== undefined) {
        statusText += ` |  ${data.passed} |  ${data.failed}`;
    }
    elements.runStats.textContent = statusText;
}

// Показать детали запуска
async function showRunDetails(runId) {
    try {
        const response = await fetch(`${API_BASE}/tests/run/${runId}`);
        const data = await response.json();

        renderRunDetails(data);
        elements.runDetails.style.display = 'block';
        // Прокручиваем детали в начало
        elements.runDetails.scrollTop = 0;
    } catch (error) {
        console.error('Error loading run details:', error);
    }
}

// Рендер деталей запуска
function renderRunDetails(data) {
    const results = data.results || [];

    const html = `
        <div class="run-info">
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>Статус:</strong> <span class="status-badge ${data.status}">${data.status}</span></p>
            <p><strong>Начало:</strong> ${new Date(data.started_at).toLocaleString()}</p>
            <p><strong>Окончание:</strong> ${data.completed_at ? new Date(data.completed_at).toLocaleString() : '-'}</p>
            <p><strong>Длительность:</strong> ${formatDuration(data.duration)}</p>
            <p><strong>Всего тестов:</strong> ${data.total}</p>
            <p><strong>Пройдено:</strong>  ${data.passed}</p>
            <p><strong>Упало:</strong>  ${data.failed}</p>
        </div>

        <h3>Результаты тестов</h3>
        <table class="test-results">
            <thead>
                <tr>
                    <th>Тест</th>
                    <th>Статус</th>
                    <th>Длительность</th>
                    <th>Ошибка</th>
                    <th>Скриншот</th>
                </tr>
            </thead>
            <tbody>
                ${results.map(test => `
                    <tr>
                        <td>${test.name}</td>
                        <td class="status-${test.status}">${test.status}</td>
                        <td>${test.duration}ms</td>
                        <td class="test-error">
                            ${test.error ? `
                                <a href="#" class="view-error" onclick="showError('${escapeHtml(test.error)}')">
                                    Показать ошибку
                                </a>
                            ` : '-'}
                        </td>
                        <td>
                            ${test.screenshot ? `
                                <a href="${test.screenshot}" target="_blank" class="screenshot-link">
                                    📸 Скриншот
                                </a>
                            ` : '-'}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    elements.detailsContent.innerHTML = html;
}

// Показать ошибку
window.showError = function(error) {
    elements.errorDetails.textContent = error;
    elements.errorModal.style.display = 'flex';
};

// Обновление статуса
function updateStatus(message, type = 'info') {
    elements.statusBar.style.display = 'block';
    elements.statusText.textContent = message;

    // Меняем цвет в зависимости от типа
    const colors = {
        info: '#2563eb',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
    };

    elements.statusBar.style.borderLeftColor = colors[type] || colors.info;

    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        elements.statusBar.style.display = 'none';
    }, 5000);
}

// Форматирование длительности
function formatDuration(seconds) {
    if (!seconds) return '0с';
    if (seconds < 60) return `${seconds}с`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}м ${seconds % 60}с`;
    return `${Math.floor(seconds / 3600)}ч ${Math.floor((seconds % 3600) / 60)}м`;
}

// Экранирование HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function loadRecentResults() {
    try {
        const response = await fetch(`${API_BASE}/results/recent?hours=24`);
        const data = await response.json();

        // Добавляем виджет с последними результатами
        const recentResultsHtml = `
            <div class="recent-results">
                <h3>Результаты за 24 часа</h3>
                <div class="result-stats">
                    <span class="stat passed"> ${data.stats.passed}</span>
                    <span class="stat failed"> ${data.stats.failed}</span>
                    <span class="stat total"> ${data.stats.total}</span>
                </div>
                <div class="result-list">
                    ${data.results.slice(0, 5).map(r => `
                        <div class="result-item ${r.status}" onclick="showRunDetails(${r.test_run_id})">
                            <span class="test-name">${r.test_name}</span>
                            <span class="test-status">${r.status}</span>
                            <span class="test-time">${new Date(r.timestamp).toLocaleTimeString()}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Добавляем на страницу
        const existingRecent = document.querySelector('.recent-results');
        if (existingRecent) {
            existingRecent.remove();
        }
        document.querySelector('.metrics-grid').insertAdjacentHTML('afterend', recentResultsHtml);

    } catch (error) {
        console.error('Error loading recent results:', error);
    }
}
