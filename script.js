document.addEventListener('DOMContentLoaded', function() {
    // DOM 요소 참조
    const refreshBtn = document.getElementById('refresh-btn');
    const totalStocks = document.getElementById('total-stocks');
    const avgRsi = document.getElementById('avg-rsi');
    const lastUpdate = document.getElementById('last-update');
    const refreshDate = document.getElementById('refresh-date');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const noDataMessage = document.getElementById('no-data-message');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');
    const tableHeaders = document.querySelectorAll('#results-table th');

    // 데이터 저장소
    let allData = [];
    
    // 정렬 상태 저장
    let sortConfig = {
        column: null,
        direction: 'asc'
    };

    // 초기 데이터 로드
    loadData();
    
    // 초기 새로고침 날짜 설정
    updateLastUpdated();

    // 이벤트 리스너 설정
    refreshBtn.addEventListener('click', loadData);
    
    // 테이블 헤더에 정렬 이벤트 리스너 추가
    tableHeaders.forEach((header, index) => {
        header.addEventListener('click', () => {
            sortTable(index);
        });
        // 정렬 가능 표시 추가
        header.classList.add('sortable');
    });

    // 데이터 로드 함수
    function loadData() {
        showLoading();
        
        // 코스피200 CSV 파일 로드
        const csvFile = 'results_코스피_200.csv';
        
        // 데이터 초기화
        allData = [];
        
        fetch(csvFile)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(csv => {
                allData = parseCSV(csv);
                if (allData.length > 0) {
                    renderTable();
                    updateStats();
                    updateLastUpdated();
                    showTable();
                } else {
                    showNoData();
                }
            })
            .catch(error => {
                console.log(`Error loading ${csvFile}: ${error.message}`);
                showError();
            });
    }

    // CSV 파싱 함수
    function parseCSV(csv) {
        const lines = csv.split('\n');
        const result = [];
        const headers = lines[0].split(',');
        
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === '') continue;
            
            const values = lines[i].split(',');
            const obj = {};
            
            for (let j = 0; j < headers.length; j++) {
                obj[headers[j].trim()] = values[j] ? values[j].trim() : '';
            }
            
            // 네이버증권에서 가져온 산업군 정보 사용
            // CSV에 Industry 컬럼이 없으면 기본값 설정
            if (!obj.Industry) {
                obj.Industry = '정보 없음';
            }
            
            // RSI7 차이 계산 추가
            if (obj.RSI7 && obj.Yesterday_RSI7) {
                obj.RSI7_Change = (parseFloat(obj.RSI7) - parseFloat(obj.Yesterday_RSI7)).toString();
            } else {
                obj.RSI7_Change = '0';
            }
            
            // RSI14 차이 계산 추가
            if (obj.RSI14 && obj.Yesterday_RSI14) {
                obj.RSI14_Change = (parseFloat(obj.RSI14) - parseFloat(obj.Yesterday_RSI14)).toString();
            } else {
                obj.RSI14_Change = '0';
            }
            
            result.push(obj);
        }
        
        return result;
    }

    // 테이블 정렬 함수
    function sortTable(columnIndex) {
        const columns = ['Name', 'Ticker', 'Industry', 'RSI7', 'RSI14', 'Yesterday_RSI7', 'Yesterday_RSI14', 'RSI7_Change', 'RSI14_Change'];
        const column = columns[columnIndex];
        
        // 같은 열을 다시 클릭하면 정렬 방향 전환
        const direction = sortConfig.column === column && sortConfig.direction === 'asc' ? 'desc' : 'asc';
        
        // 정렬 상태 업데이트
        sortConfig.column = column;
        sortConfig.direction = direction;
        
        // 정렬 표시 업데이트
        tableHeaders.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        tableHeaders[columnIndex].classList.add(direction === 'asc' ? 'sort-asc' : 'sort-desc');
        
        // 데이터 정렬
        allData.sort((a, b) => {
            let valueA = a[column] ? a[column] : '';
            let valueB = b[column] ? b[column] : '';
            
            // 숫자 열인 경우 숫자로 변환하여 정렬
            if (column === 'RSI7' || column === 'RSI14' || 
                column === 'Yesterday_RSI7' || column === 'Yesterday_RSI14' || 
                column === 'RSI7_Change' || column === 'RSI14_Change') {
                valueA = parseFloat(valueA) || 0;
                valueB = parseFloat(valueB) || 0;
            } else {
                // 문자열인 경우 대소문자 구분 없이 정렬
                valueA = valueA.toString().toLowerCase();
                valueB = valueB.toString().toLowerCase();
            }
            
            // 정렬 방향에 따라 비교
            if (direction === 'asc') {
                return valueA > valueB ? 1 : -1;
            } else {
                return valueA < valueB ? 1 : -1;
            }
        });
        
        // 테이블 다시 렌더링
        renderTable();
    }
    
    // 테이블 렌더링 함수
    function renderTable() {
        resultsBody.innerHTML = '';
        
        allData.forEach(item => {
            const row = document.createElement('tr');
            
            // 종목명
            const nameCell = document.createElement('td');
            nameCell.textContent = item.Name || item.Ticker || '-';
            row.appendChild(nameCell);
            
            // 티커
            const tickerCell = document.createElement('td');
            tickerCell.textContent = item.Ticker || '-';
            row.appendChild(tickerCell);
            
            // 산업군
            const industryCell = document.createElement('td');
            industryCell.textContent = item.Industry || '정보 없음';
            row.appendChild(industryCell);
            
            // RSI(7)
            const rsi7Cell = document.createElement('td');
            rsi7Cell.textContent = item.RSI7 ? parseFloat(item.RSI7).toFixed(2) : '-';
            row.appendChild(rsi7Cell);
            
            // RSI(14)
            const rsi14Cell = document.createElement('td');
            rsi14Cell.textContent = item.RSI14 ? parseFloat(item.RSI14).toFixed(2) : '-';
            row.appendChild(rsi14Cell);
            
            // RSI(7) 어제
            const yesterdayRsi7Cell = document.createElement('td');
            yesterdayRsi7Cell.textContent = item.Yesterday_RSI7 ? parseFloat(item.Yesterday_RSI7).toFixed(2) : '-';
            row.appendChild(yesterdayRsi7Cell);
            
            // RSI(14) 어제
            const yesterdayRsi14Cell = document.createElement('td');
            yesterdayRsi14Cell.textContent = item.Yesterday_RSI14 ? parseFloat(item.Yesterday_RSI14).toFixed(2) : '-';
            row.appendChild(yesterdayRsi14Cell);
            
            // RSI(7) 차이
            const rsi7ChangeCell = document.createElement('td');
            if (item.RSI7_Change) {
                const change = parseFloat(item.RSI7_Change);
                rsi7ChangeCell.textContent = change > 0 ? `+${change.toFixed(2)}` : change.toFixed(2);
                if (change > 0) {
                    rsi7ChangeCell.classList.add('positive-change');
                } else if (change < 0) {
                    rsi7ChangeCell.classList.add('negative-change');
                }
            } else {
                rsi7ChangeCell.textContent = '0.00';
            }
            row.appendChild(rsi7ChangeCell);
            
            // RSI(14) 차이
            const rsi14ChangeCell = document.createElement('td');
            if (item.RSI14_Change) {
                const change = parseFloat(item.RSI14_Change);
                rsi14ChangeCell.textContent = change > 0 ? `+${change.toFixed(2)}` : change.toFixed(2);
                if (change > 0) {
                    rsi14ChangeCell.classList.add('positive-change');
                } else if (change < 0) {
                    rsi14ChangeCell.classList.add('negative-change');
                }
            } else {
                rsi14ChangeCell.textContent = '0.00';
            }
            row.appendChild(rsi14ChangeCell);
            
            resultsBody.appendChild(row);
        });
    }

    // 통계 업데이트 함수
    function updateStats() {
        // 총 종목 수
        totalStocks.textContent = allData.length;
        
        // 평균 RSI(7) 계산 - 유효한 RSI7 값만 사용
        const validRsiData = allData.filter(item => item.RSI7 && !isNaN(parseFloat(item.RSI7)));
        const rsiSum = validRsiData.reduce((sum, item) => {
            return sum + parseFloat(item.RSI7);
        }, 0);
        
        const avgRsiValue = validRsiData.length > 0 ? rsiSum / validRsiData.length : 0;
        avgRsi.textContent = avgRsiValue.toFixed(2);
    }

    // 마지막 업데이트 시간 설정
    function updateLastUpdated() {
        const now = new Date();
        const formattedDate = now.toLocaleString('ko-KR');
        lastUpdate.textContent = formattedDate;
        refreshDate.textContent = `최종 업데이트: ${formattedDate}`;
    }

    // 날짜 포맷팅 함수
    function formatDate(dateStr) {
        if (!dateStr) return '-';
        
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('ko-KR');
        } catch (e) {
            return dateStr;
        }
    }

    // UI 상태 관리 함수들
    function showLoading() {
        loadingMessage.style.display = 'block';
        errorMessage.style.display = 'none';
        noDataMessage.style.display = 'none';
        resultsTable.style.display = 'none';
    }

    function showError() {
        loadingMessage.style.display = 'none';
        errorMessage.style.display = 'block';
        noDataMessage.style.display = 'none';
        resultsTable.style.display = 'none';
    }

    function showNoData() {
        loadingMessage.style.display = 'none';
        errorMessage.style.display = 'none';
        noDataMessage.style.display = 'block';
        resultsTable.style.display = 'none';
    }

    function showTable() {
        loadingMessage.style.display = 'none';
        errorMessage.style.display = 'none';
        noDataMessage.style.display = 'none';
        resultsTable.style.display = 'block';
    }
});