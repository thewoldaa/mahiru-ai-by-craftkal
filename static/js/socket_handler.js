export class SocketHandler {
  constructor() { this.socket = io(); }
  init() {
    this.socket.emit('join_game', { session_id: crypto.randomUUID() });
    this.socket.on('achievement_unlocked', ({ achievement }) => alert(`Achievement: ${achievement}`));
  }
}
