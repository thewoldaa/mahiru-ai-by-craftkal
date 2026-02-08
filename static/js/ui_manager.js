export class UIManager {
  setSpeaker(name) { document.getElementById('speaker').textContent = name; }
  setDialogue(text) { document.getElementById('dialog-text').textContent = text; }
  renderChoices(choices, onClick) {
    const root = document.getElementById('choices');
    root.innerHTML = '';
    choices.forEach((choice) => {
      const btn = document.createElement('button');
      btn.textContent = choice.text;
      btn.addEventListener('click', () => onClick(choice.id));
      root.appendChild(btn);
    });
  }
}
