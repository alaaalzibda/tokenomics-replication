'''
"Utility helpers: array shuffle (for 7-bag randomizer) and clamp function."
'''
const __DOC__ = `
Utility helpers:
- shuffleArray: In-place Fisher-Yates shuffle
- clamp: clamps a value into [min, max]
`;
export function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}