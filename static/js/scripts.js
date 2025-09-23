document.addEventListener('DOMContentLoaded', () => {
    const toggleFormButton = document.getElementById('toggleFormButton');
    const taskForm = document.getElementById('taskForm');
    const csvContent = document.getElementById('csvContent');
    const csvContent2 = document.getElementById('csvContent2');
    const dashboardButton = document.getElementById('dashboardButton');
    const rankingButton = document.getElementById('rankingButton');
    const exportBtn = document.getElementById('exportButton');
    const confirmationModal = document.getElementById('confirmationModal');
    const selectedTasksList = document.getElementById('selectedTasksList');
    const confirmDownloadButton = document.getElementById('confirmDownloadButton');
    const cancelDownloadButton = document.getElementById('cancelDownloadButton');
    const updateTimeButton = document.getElementById('updateTimeButton');
    const updateTimeModal = document.getElementById('updateTimeModal');
    const refreshIntervalInput = document.getElementById('refreshInterval');
    const setAutoRefreshButton = document.getElementById('setAutoRefreshButton');
    const cancelAutoRefreshButton = document.getElementById('cancelAutoRefreshButton');

    // 顯示/隱藏內容區域
    const setSectionVisible = (sectionToShow) => {
        const contentSections = document.querySelectorAll('.contentSection');
        contentSections.forEach(section => {
            section.style.display = (section === sectionToShow) ? 'block' : 'none';
        });
    };

    // 從 localStorage 獲取當前顯示的頁面
    const currentPage = localStorage.getItem('currentPage') || 'taskForm';

    // 初始設定，顯示上次的頁面
    if (currentPage === 'taskForm') {
        setSectionVisible(taskForm);
    } else if (currentPage === 'csvContent') {
        setSectionVisible(csvContent);
    }

    // 點擊 Select Tasks 按鈕顯示表單
    toggleFormButton?.addEventListener('click', (e) => {
        e.preventDefault();
        setSectionVisible(taskForm);
        localStorage.setItem('currentPage', 'taskForm');
    });

    // 點擊 Dashboard 按鈕顯示 CSV 資料
    dashboardButton?.addEventListener('click', (e) => {
        e.preventDefault();
        setSectionVisible(csvContent);
        localStorage.setItem('currentPage', 'csvContent');
    });

    rankingButton?.addEventListener('click', (e) => {
        e.preventDefault();
        setSectionVisible(csvContent2);
        localStorage.setItem('currentPage', 'csvContent');
    });

    // 當勾選框變動時，保存選擇並篩選資料
    const saveSelectedTasks = () => {
        const selectedTasks = Array.from(document.querySelectorAll('.task-checkbox:checked')).map(cb => cb.value);
        localStorage.setItem('selectedTasks', JSON.stringify(selectedTasks));
        return selectedTasks;
    };

    const filterRows = (selectedTasks) => {
        const rows = document.querySelectorAll('.csvRow');
        rows.forEach(row => {
            const taskName = row.cells[2]?.innerText || ''; // 假設 CSV 的第三列是任務名稱
            row.style.display = (selectedTasks.length === 0 || selectedTasks.includes(taskName)) ? '' : 'none';
        });
    };

    const loadSelectedTasks = () => {
        const saved = JSON.parse(localStorage.getItem('selectedTasks') || '[]');
        document.querySelectorAll('.task-checkbox').forEach(cb => cb.checked = saved.includes(cb.value));
        filterRows(saved);
    };

    // 點擊 Export CSV 按鈕
    exportBtn?.addEventListener('click', (e) => {
        e.preventDefault();

        // 取得勾選的題目
        const selectedTasks = saveSelectedTasks();
        if (selectedTasks.length > 0) {
            // 顯示模態框並列出選中的題目
            selectedTasksList.innerHTML = selectedTasks.map(task => `<li>${task}</li>`).join('');
            confirmationModal.style.display = 'flex';
        } else {
            alert("Select a Tasks!");
        }
    });

    // 確認下載
    confirmDownloadButton?.addEventListener('click', () => {
        const rows = Array.from(document.querySelectorAll('.csvRow')).filter(r => r.style.display !== 'none');
        const table = document.getElementById('csvTable');
        if (!table) return;

        const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText);
        const csvRows = [headers.join(',')];
        rows.forEach(row => {
            const rowData = Array.from(row.querySelectorAll('td')).map(td => {
                const text = td.innerText.replace(/"/g, '""');
                return /[",\n]/.test(text) ? `"${text}"` : text;
            });
            csvRows.push(rowData.join(','));
        });

        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'filtered_data.csv';
        link.click();

        // 關閉模態框
        confirmationModal.style.display = 'none';
    });

    // 取消下載
    cancelDownloadButton?.addEventListener('click', () => {
        confirmationModal.style.display = 'none';
    });

    // 初始化已選任務並過濾資料
    loadSelectedTasks();

    // 當勾選框變動時，保存選擇並篩選資料
    document.querySelectorAll('.task-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
            const selected = Array.from(document.querySelectorAll('.task-checkbox:checked')).map(cb => cb.value);
            saveSelectedTasks();
            filterRows(selected);
        });
    });

    let refreshIntervalId;  // 用來存儲 setInterval ID，方便清除

    // 當頁面加載時，檢查是否有已設定的自動刷新時間
    const savedInterval = localStorage.getItem('autoRefreshInterval');
    if (savedInterval) {
        setAutoRefresh(savedInterval);
    }

    // 顯示/隱藏自動刷新設置模態框
    updateTimeButton?.addEventListener('click', (e) => {
        e.preventDefault();
        updateTimeModal.style.display = 'flex';
        clearInterval(refreshIntervalId);  // 進入模態框時停止自動刷新
    });

    // 設置自動刷新時間
    setAutoRefreshButton?.addEventListener('click', () => {
        const refreshInterval = parseInt(refreshIntervalInput.value, 10);
        if (isNaN(refreshInterval) || refreshInterval <= 0) {
            alert("Please enter a valid number greater than 0.");
            return;
        }

        // 儲存設置的自動刷新時間
        localStorage.setItem('autoRefreshInterval', refreshInterval);
        alert(`Auto-refresh set to ${refreshInterval} seconds.`);

        // 設置自動刷新
        setAutoRefresh(refreshInterval);

        // 關閉模態框
        updateTimeModal.style.display = 'none';
    });

    // 取消自動刷新設置
    cancelAutoRefreshButton?.addEventListener('click', () => {
        updateTimeModal.style.display = 'none';
    });

    // 設置定期自動刷新
    function setAutoRefresh(interval) {
        // 如果已經有 setInterval 運行，先清除它
        if (refreshIntervalId) {
            clearInterval(refreshIntervalId);
        }
        
        // 每隔設定的時間自動刷新頁面
        refreshIntervalId = setInterval(() => {
            location.reload();
        }, interval * 1000);
    }

    // 當頁面離開自動刷新模態框時，恢復自動刷新
    cancelUpdateTimeButton?.addEventListener('click', () => {
        updateTimeModal.style.display = 'none';
        const savedInterval = localStorage.getItem('autoRefreshInterval');
        if (savedInterval) {
            setAutoRefresh(savedInterval);  // 恢復設置的自動刷新時間
        }
    });

    // 點擊其它模態框時暫停自動刷新
    const otherModals = document.querySelectorAll('.modal');
    otherModals.forEach(modal => {
        modal.addEventListener('click', () => {
            clearInterval(refreshIntervalId);  // 暫停自動刷新
        });
    });
});
