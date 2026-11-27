import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(__dirname, "../src");

function getTsFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach((file) => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getTsFiles(filePath));
    } else if (file.endsWith(".ts")) {
      results.push(filePath);
    }
  });
  return results;
}

const files = getTsFiles(srcDir);
let failed = false;

files.forEach((file) => {
  const content = fs.readFileSync(file, "utf8");
  const lines = content.split("\n").length;
  const relPath = path.relative(path.join(__dirname, ".."), file);
  if (lines > 200) {
    console.error(`ERROR: ${relPath} has ${lines} lines (max allowed: 200).`);
    failed = true;
  } else {
    console.log(`OK: ${relPath} has ${lines} lines.`);
  }
});

if (failed) {
  process.exit(1);
} else {
  console.log("All source files are within the 200-line limit!");
}
