import * as fs from "fs";
import * as path from "path";

export function readCodeSnippet(workspaceRoot: string, filePath: string, startLine: number, endLine: number): string {
  try {
    const fullPath = path.isAbsolute(filePath) ? filePath : path.join(workspaceRoot, filePath);
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, "utf8");
      const lines = content.split("\n");
      const start = Math.max(0, startLine - 1);
      const end = Math.min(lines.length, endLine);
      const sliceLines = lines.slice(start, end);
      return sliceLines.join("\n");
    }
  } catch {
    // fallback
  }
  return `# Khong the doc file ${filePath} (${startLine}-${endLine})`;
}
