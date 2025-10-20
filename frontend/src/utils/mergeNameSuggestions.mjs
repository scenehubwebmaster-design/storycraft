export function mergeNameSuggestions(top = {}, sd = null) {
  const combined = [];
  const pushNameEntries = (arr) => {
    if (!Array.isArray(arr)) return;
    for (const entry of arr) {
      if (typeof entry === "string")
        combined.push({ first_name: entry, _ai: true });
      else if (entry && typeof entry === "object")
        combined.push({ ...entry, _ai: true });
    }
  };

  pushNameEntries(top.name_options || []);
  pushNameEntries(top.name_suggestions || []);
  if (sd && typeof sd === "object") {
    pushNameEntries(sd.name_options || []);
    pushNameEntries(sd.name_suggestions || []);
  }
  return combined;
}
