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

  const speakerBtn = document.querySelector('.speaker-btn');
    if (speakerBtn) {
      speakerBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const audio = document.getElementById('card-audio');
      if (audio) {
        audio.currentTime = 0;
        audio.play();
      } else {
        // Copilot-generated
        const wordElem = document.querySelector('.card-word');
        if (!wordElem) return;
        const word = wordElem.textContent;
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
      });
    }

  // set up card click handler once DOM is ready
  const cardElement = document.querySelector('.card.clickable-card');
  if (cardElement) {
    cardElement.addEventListener('click', flipCard);
  }

//copilot generated keyboard shortcut for flipping the card, again, hard, good, easy
//did not make the space also apply to easy, this way 1 corresponds to the first button, 2 to the second, etc., to make it easier to explain to the user
//space also flips the card backwards and forwards now
  document.addEventListener('keydown', handleFlipShortcut);
});

function handleFlipShortcut(event) {
  if (event.repeat) return;

  const target = event.target;
  const tagName = target?.tagName;
  const isInteractiveElement = target?.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON', 'A'].includes(tagName);

  if (isInteractiveElement) return;

  const isSpaceKey = event.code === 'Space' || event.key === ' ';
  if (isSpaceKey) {
    
  const card = document.querySelector('.card.clickable-card');
  if (!card) return;

  event.preventDefault();
  flipCard({ currentTarget: card });
  return;
}

  // 1=Again, 2=Hard, 3=Good, 4=Easy
  const ratingMap = { '1': 'again', '2': 'hard', '3': 'good', '4': 'easy' };
  const rating = ratingMap[event.key];
  if (!rating) return;

  const form = document.getElementById('difficulty-buttons');
  if (!form || form.classList.contains('hidden')) return;

  event.preventDefault();
  const btn = form.querySelector(`button[value="${rating}"]`);
  if (btn) btn.click();
}
// ChatGPT
// updated flipCard to allow flipping back and forth
function flipCard(event) {
  const card = event ? event.currentTarget : document.querySelector('.card.clickable-card');
  const buttons = document.getElementById('difficulty-buttons');
  if (!card) return;

  const front = card.querySelector('.card-front');
  const back = card.querySelector('.card-back');

  const isFlipped = card.classList.contains('flipped');

  if (!isFlipped) {
    // FRONT → BACK
    card.classList.add('flipped');

    if (front) front.classList.add('hidden');
    if (back) back.classList.remove('hidden');

    // Show buttons only after first flip
    if (buttons) buttons.classList.remove('hidden');

  } else {
    // BACK → FRONT
    card.classList.remove('flipped');

    if (back) back.classList.add('hidden');
    if (front) front.classList.remove('hidden');
  }
}

// ChatGPT generated code to show spacebar hint on page load, then hide it after a few seconds
document.addEventListener("DOMContentLoaded", () => {
  const hint = document.getElementById("spacebar-hint");

  if (!hint) return;

  // Show hint
  setTimeout(() => {
    hint.classList.add("show");
  }, 500);

  // Hide after a few seconds
  setTimeout(() => {
    hint.classList.remove("show");
  }, 4000);
});