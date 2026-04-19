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

// Heatmap loader — Claude Generated
const heatmapContainer = document.querySelector('#heatmap-container');
 
if (heatmapContainer) {
    const svgUrl     = heatmapContainer.dataset.svgUrl;
    const dataUrl    = heatmapContainer.dataset.heatmapUrl;
 
    if (svgUrl && dataUrl) {
        Promise.all([
            fetch(svgUrl).then(r => r.text()),
            fetch(dataUrl).then(r => r.json()),
        ])
        .then(([svgContent, data]) => {
            if (window.Heatmap) {
                window.Heatmap.render('heatmap-container', data, {
                    showStreak: true,
                    svgContent,
                });
            }
        })
        .catch(err => console.error('Heatmap load error:', err));
    }
}
 