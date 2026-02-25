// chatGPT help for selecting all elements and setting url location based on ids

const deckdivs = document.querySelectorAll('.deck')

deckdivs.forEach(deck => {
    deck.addEventListener('click', () => {
        const deckid = deck.id
        window.location.href = `flashcards/${deckid}`
    })
})