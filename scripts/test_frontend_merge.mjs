import { mergeNameSuggestions } from "../frontend/src/utils/mergeNameSuggestions.mjs";

const top = {
  name_options: ["TopOne"],
  name_suggestions: [{ first_name: "TopTwo" }],
};
const sd = {
  name_options: ["SDOne"],
  name_suggestions: [{ first_name: "SDTwo", origin: "Elven" }],
};

const combined = mergeNameSuggestions(top, sd);
console.log("Combined result:");
console.log(JSON.stringify(combined, null, 2));

if (combined.length !== 4) {
  console.error("Test failed: expected 4 entries");
  process.exit(1);
}
console.log("Test passed");
