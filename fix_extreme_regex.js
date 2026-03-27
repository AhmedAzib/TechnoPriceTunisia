
const fs = require('fs');
const path = 'c:/Users/USER/Documents/programmation/frontend/src/ProductsPage.jsx';
let content = fs.readFileSync(path, 'utf8');

const oldStr = `if (rule.extreme && rule.extreme.match(/\\d+\\s*MHz/i)) {`;
const newStr = `if (rule.extreme) {`;

if (content.includes(oldStr)) {
    content = content.replace(oldStr, newStr);
    fs.writeFileSync(path, content, 'utf8');
    console.log("Successfully patched Extreme Performance logic.");
} else {
    console.error("Target string not found!");
    // Debug: print similar lines
    const lines = content.split('\n');
    lines.forEach((l, i) => {
        if (l.includes("rule.extreme")) console.log(`${i+1}: ${l}`);
    });
    process.exit(1);
}
