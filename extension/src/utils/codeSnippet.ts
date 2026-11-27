import * as fs from "fs";
import * as path from "path";

const MOCK_FALLBACK_LINES: Record<string, string[]> = {
  "app/routes.py": [
    "@router.delete('/todos/{todo_id}')",
    "def delete_todo(todo_id: int, db=Depends(get_db)):",
    "    todo = db.get(Todo, todo_id)",
    "    if todo is None:",
    "        raise HTTPException(404, 'Not found')",
    "    db.delete(todo)",
    "    db.commit()",
    "    return Response(status_code=204)"
  ]
};

// Doc doan code theo khoang dong [startLine, endLine] trong workspace
export function readCodeSnippet(
  workspaceRoot: string,
  filePath: string,
  linesRange: [number, number]
): string {
  const [startLine, endLine] = linesRange;
  try {
    const fullPath = path.isAbsolute(filePath) ? filePath : path.join(workspaceRoot, filePath);
    if (fs.existsSync(fullPath)) {
      const allLines = fs.readFileSync(fullPath, "utf8").split("\n");
      const start = Math.max(0, startLine - 1);
      const end = Math.min(allLines.length, Math.max(start + 1, endLine));
      return allLines.slice(start, end).join("\n");
    }
  } catch {
    // Bo qua loi doc file, dung fallback
  }
  const fallback = MOCK_FALLBACK_LINES[filePath];
  if (fallback) {
    return fallback.join("\n");
  }
  return `# Không đọc được ${filePath} (dòng ${startLine}-${endLine})`;
}
