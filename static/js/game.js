import { UIManager } from './ui_manager.js';
import { AudioManager } from './audio_manager.js';
import { SocketHandler } from './socket_handler.js';

const ui = new UIManager();
const audio = new AudioManager();
const socket = new SocketHandler();

let currentScene = 'ch1_scene_1';
let gameState = { stats: {}, flags: {}, inventory: [] };

async function loadScene(sceneId) {
  const res = await fetch(`/api/scene/${sceneId}`);
  const scene = await res.json();
  currentScene = scene.id;
  ui.setSpeaker(scene.speaker || 'Narator');
  ui.setDialogue(scene.dialogue || '...');
  ui.renderChoices(scene.choices || [], async (choiceId) => {
    const resp = await fetch('/api/choice', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scene_id: currentScene, choice_id: choiceId, state: gameState })
    });
    const data = await resp.json();
    gameState = data.state || gameState;
    if (data.next_scene) loadScene(data.next_scene);
  });
  if (scene.music) audio.playBgm(scene.music);
}

document.getElementById('quick-save').addEventListener('click', async () => {
  await fetch('/api/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ slot: 1, scene_id: currentScene, chapter: 1, state: gameState }) });
  alert('Quick save sukses');
});

document.getElementById('quick-load').addEventListener('click', async () => {
  const res = await fetch('/api/load/1');
  if (!res.ok) return alert('Slot kosong');
  const data = await res.json();
  gameState = data.state || gameState;
  loadScene(data.scene_id);
});

socket.init();
loadScene(currentScene);
