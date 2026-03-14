// for copilot generated language selection dropdown
const profileDropdown = document.querySelector('#profileDropdown');
if (profileDropdown) {
	profileDropdown.onclick = () => document.querySelector('.dropdown-menu').classList.toggle('show');
}

const openLanguageDropdown = document.querySelector('#open-language-dropdown');
const selectedLanguageLabel = document.querySelector('#selected-language-label');
const languageDropdownMenu = document.querySelector('#language-dropdown-menu');
const languageOptions = document.querySelectorAll('.language-option');

const closeLanguageDropdown = () => {
	if (languageDropdownMenu && openLanguageDropdown) {
		languageDropdownMenu.classList.remove('show');
		openLanguageDropdown.setAttribute('aria-expanded', 'false');
	}
};

const toggleLanguageDropdown = () => {
	if (!languageDropdownMenu || !openLanguageDropdown) {
		return;
	}

	const isOpen = languageDropdownMenu.classList.toggle('show');
	openLanguageDropdown.setAttribute('aria-expanded', String(isOpen));
};

if (openLanguageDropdown) {
	openLanguageDropdown.addEventListener('click', toggleLanguageDropdown);
	openLanguageDropdown.addEventListener('keydown', (event) => {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			toggleLanguageDropdown();
		}

		if (event.key === 'Escape') {
			closeLanguageDropdown();
		}
	});
}

languageOptions.forEach((option) => {
	option.addEventListener('click', () => {
		if (selectedLanguageLabel) {
			selectedLanguageLabel.textContent = option.dataset.language;
		}
		closeLanguageDropdown();
	});
});

if (languageOptions.length > 0 && selectedLanguageLabel) {
	selectedLanguageLabel.textContent = languageOptions[0].dataset.language;
}

document.addEventListener('click', (event) => {
	if (!languageDropdownMenu || !openLanguageDropdown) {
		return;
	}

	if (!languageDropdownMenu.contains(event.target) && !openLanguageDropdown.contains(event.target)) {
		closeLanguageDropdown();
	}
});

// Heatmap rendering
const heatmapContainer = document.querySelector('#heatmap-container');

if (heatmapContainer) {
	const svgUrl = heatmapContainer.dataset.svgUrl;
	const heatmapUrl = heatmapContainer.dataset.heatmapUrl;

	if (svgUrl && heatmapUrl) {
		fetch(svgUrl)
			.then((resp) => resp.text())
			.then((svgText) => {
				return fetch(heatmapUrl)
					.then((response) => response.json())
					.then((data) => ({ svgText, data }));
			})
			.then(({ svgText, data }) => {
				const config = {
					heatmapShowStreak: true,
					heatmapShowMonths: true,
					heatmapShowWeekdays: true,
					heatmapShowWeekHeader: true,
					heatmapDefaultView: 'year',
					heatmapSvgContent: svgText,
				};

				if (window.OnigiriHeatmap) {
					window.OnigiriHeatmap.render('heatmap-container', data, config);
				}
			})
			.catch((err) => console.error('Heatmap load error', err));
	}
}
