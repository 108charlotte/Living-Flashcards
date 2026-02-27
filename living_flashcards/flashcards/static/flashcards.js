
//copilot generated code for flashcard flipping and speaker button functionality
// Speaker button lives only on the front face; stopping propagation prevents
// the click from flipping the card when the user just wants audio.
const speakerButtons = document.querySelectorAll('.speaker-btn');
speakerButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const wordElem = document.querySelector('.card-word');
      if (!wordElem) return;
      const word = wordElem.textContent;
      // Use Web Speech API to speak the word
      const utterance = new SpeechSynthesisUtterance(word);
      utterance.rate = 1;
      utterance.pitch = 1;
      window.speechSynthesis.speak(utterance);
  });
});

// copilot generated progress bar code
function updateProgressBar() {
  const progressText = document.querySelector('.progress_text');
  const progressFill = document.querySelector('.progress_fill');

  if (progressText && progressFill) {
    const text = progressText.textContent.trim();
    const [currentRaw, totalRaw] = text.split('/');
    const current = parseInt(currentRaw, 10);
    const total = parseInt(totalRaw, 10);

    if (!isNaN(current) && !isNaN(total) && total > 0) {
      const percentage = (current / total) * 100;
      progressFill.style.width = percentage + '%';
    } else {
      // no cards or invalid values -> empty bar
      progressFill.style.width = '0%';
    }
  }
}

// Run on page load
document.addEventListener('DOMContentLoaded', () => {
  updateProgressBar();

  // set up card click handler once DOM is ready
  const cardElement = document.querySelector('.card.clickable-card');
  if (cardElement) {
    cardElement.addEventListener('click', flipCard);
  }
});

// copilot code to create card "flip"
function flipCard(event) {
  console.log('flipCard called', event);
  const card = event ? event.currentTarget : document.querySelector('.card.clickable-card');
  const buttons = document.getElementById('difficulty-buttons');
  if (!card) return;

  // only flip once (show definition and controls)
  if (card.classList.contains('flipped')) return;

  card.classList.add('flipped');
  
  
  // debug info
  console.log('card classes after add:', card.className);
  console.log('computed transform:', window.getComputedStyle(card).transform);
  const back = card.querySelector('.card-back');
  if (back) back.classList.remove('hidden');
  if (buttons) buttons.classList.remove('hidden');
}