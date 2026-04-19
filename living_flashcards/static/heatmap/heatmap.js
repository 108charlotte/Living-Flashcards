/*
    Claude Generated Heatmap Renderer inspired from https://github.com/thepeacemonk/Onigiri 
    Year view: months on X axis, M/W/F labels on Y axis.
*/
 
window.Heatmap = window.Heatmap || {};
 
(function (exports) {
    "use strict";
 
    // --- HELPERS ---
 
    function getLocalDateKey(date) {
        const y = date.getFullYear();
        const m = (date.getMonth() + 1).toString().padStart(2, '0');
        const d = date.getDate().toString().padStart(2, '0');
        return `${y}-${m}-${d}`;
    }
 
    function getIntensityLevel(count, dailyAverage) {
        if (count === 0) return 0;
        const avg = Math.max(dailyAverage, 5);
        if (count < 0.4 * avg) return 1;
        if (count < 0.7 * avg) return 2;
        if (count < 1.0 * avg) return 3;
        if (count < 1.3 * avg) return 4;
        if (count < 1.6 * avg) return 5;
        if (count < 2.0 * avg) return 6;
        if (count < 2.5 * avg) return 7;
        return 8;
    }
 
    function getDueIntensityLevel(count, dailyAverage) {
        if (count === 0) return 0;
        const avg = Math.max(dailyAverage, 5);
        if (count < 0.4 * avg) return 1;
        if (count < 0.7 * avg) return 2;
        if (count < 1.0 * avg) return 3;
        if (count < 1.3 * avg) return 4;
        if (count < 1.6 * avg) return 5;
        if (count < 2.0 * avg) return 6;
        if (count < 2.5 * avg) return 7;
        return 8;
    }
 
    // --- DATA ---
 
    function prepareData(raw) {
        return {
            reviewsByDay: new Map(Object.entries(raw.calendar || {})),
            duesByDay:    new Map(Object.entries(raw.due_calendar || {})),
            todayKey:     raw.today_date_key,
            dailyAverage: raw.daily_average || 0,
            streak:       raw.streak || 0,
        };
    }
 
    // --- CELL ---
 
    function createCell(date, reviewCount, dueCount, todayKey, dailyAverage, svgContent) {
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell';
 
        const dateKey = getLocalDateKey(date);
        const dateText = date.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
 
        if (dateKey === todayKey) {
            cell.classList.add('today');
            cell.dataset.level = getIntensityLevel(reviewCount, dailyAverage);
            cell.dataset.tooltip = `${reviewCount} review${reviewCount !== 1 ? 's' : ''} done today`;
        } else if (dateKey < todayKey) {
            cell.dataset.level = getIntensityLevel(reviewCount, dailyAverage);
            cell.dataset.tooltip = `${reviewCount} review${reviewCount !== 1 ? 's' : ''} on ${dateText}`;
        } else {
            cell.classList.add('future');
            cell.dataset.dueLevel = getDueIntensityLevel(dueCount, dailyAverage);
            cell.dataset.tooltip = `${dueCount} review${dueCount !== 1 ? 's' : ''} due on ${dateText}`;
        }
 
        const shape = document.createElement('div');
        shape.className = 'cell-shape';
 
        if (svgContent) {
            const uri = `url("data:image/svg+xml,${encodeURIComponent(svgContent)}")`;
            shape.style.webkitMaskImage = uri;
            shape.style.maskImage = uri;
            shape.style.webkitMaskSize = 'contain';
            shape.style.maskSize = 'contain';
            shape.style.webkitMaskRepeat = 'no-repeat';
            shape.style.maskRepeat = 'no-repeat';
            shape.style.webkitMaskPosition = '50% 50%';
            shape.style.maskPosition = '50% 50%';
        }
 
        cell.appendChild(shape);
        return cell;
    }
 
    // --- YEAR VIEW ---
 
    function drawYear(grid, data, svgContent) {
        const year = new Date().getFullYear();
        const firstDay = new Date(year, 0, 1);
        const startOffset = (firstDay.getDay() + 6) % 7; // Monday-based offset
 
        // Month labels row
        const monthsRow = document.createElement('div');
        monthsRow.className = 'heatmap-months';
 
        // Weekday labels column (only M, W, F at rows 0, 2, 4)
        const weekdaysCol = document.createElement('div');
        weekdaysCol.className = 'heatmap-weekdays';
        // 7 slots; show label only for Mon(0), Wed(2), Fri(4)
        ['M', '', 'W', '', 'F', '', ''].forEach(label => {
            const d = document.createElement('div');
            d.textContent = label;
            weekdaysCol.appendChild(d);
        });
 
        // Cells
        const cellsGrid = document.createElement('div');
        cellsGrid.className = 'heatmap-cells';
 
        let currentMonth = -1;
        let col = 0;
 
        for (let i = 0; i < 371; i++) {
            const date = new Date(firstDay);
            date.setDate(firstDay.getDate() - startOffset + i);
 
            const isCurrentYear = date.getFullYear() === year;
 
            if (!isCurrentYear) {
                const empty = document.createElement('div');
                empty.className = 'heatmap-cell empty';
                cellsGrid.appendChild(empty);
                if (i % 7 === 6) col++;
                continue;
            }
 
            // Month label at start of each month
            if (date.getDate() === 1 && date.getMonth() !== currentMonth) {
                currentMonth = date.getMonth();
                const label = document.createElement('div');
                label.className = 'month-label';
                label.textContent = date.toLocaleString('default', { month: 'short' });
                label.style.gridColumn = Math.floor(i / 7) + 1;
                monthsRow.appendChild(label);
            }
 
            const dateKey = getLocalDateKey(date);
            const reviews = data.reviewsByDay.get(dateKey) || 0;
            const dues    = data.duesByDay.get(dateKey)    || 0;
            const cell    = createCell(date, reviews, dues, data.todayKey, data.dailyAverage, svgContent);
            cellsGrid.appendChild(cell);
 
            if (i % 7 === 6) col++;
        }
 
        grid.appendChild(monthsRow);
        grid.appendChild(weekdaysCol);
        grid.appendChild(cellsGrid);
    }
 
    // --- RENDER ---
 
    exports.render = function (containerId, raw, config) {
        const container = document.getElementById(containerId);
        if (!container) return;
 
        const data = prepareData(raw);
        const svgContent = config.svgContent || null;
 
        const streakHTML = config.showStreak && data.streak > 0
        ? `<div class="heatmap-streak">
           <svg class="streak-fire" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
               <path d="M12 23C7.03 23 3 18.97 3 14c0-3.5 2.5-6.5 4-8 0 2 1 3.5 2 4.5C9 8 10 4.5 8.5 2 11 2.5 15 6 15 10c.67-.83 1-2 1-3.5 2 2 4 5 4 7.5 0 4.97-4.03 9-8 9z"/>
           </svg>
           ${data.streak} day streak
       </div>`
    : '';
 
        container.innerHTML = `
            <div class="heatmap-header">
                <h3 class="heatmap-title">Activity</h3>
                ${streakHTML}
            </div>
            <div class="heatmap-grid"></div>
        `;
 
        drawYear(container.querySelector('.heatmap-grid'), data, svgContent);
    };
 
})(window.Heatmap);