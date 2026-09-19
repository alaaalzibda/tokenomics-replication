'''
Utility helpers for the Match-3 game:
- sleep(ms): async delay for sequencing animations
- randomInt(min, max): inclusive random integer
- formatTime(seconds): convert seconds to mm:ss string
'''
/*
Utility helpers for the Match-3 game:
- sleep(ms): async delay for sequencing animations
- randomInt(min, max): inclusive random integer
- formatTime(seconds): convert seconds to mm:ss string
*/
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
export function formatTime(totalSeconds) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  const mm = String(m).padStart(2, '0');
  const ss = String(r).padStart(2, '0');
  return `${mm}:${ss}`;
}