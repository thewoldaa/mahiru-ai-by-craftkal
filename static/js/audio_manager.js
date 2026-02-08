export class AudioManager {
  constructor() { this.bgm = new Audio(); this.bgm.loop = true; }
  playBgm(src) { this.bgm.src = `/static/audio/bgm/${src}`; this.bgm.play().catch(()=>{}); }
  setVolume(volume) { this.bgm.volume = Number(volume); }
}
