module.exports = function stable(arr, compare) {
  if (compare) {
    return arr.sort(compare);
  }
  return arr.sort();
};
