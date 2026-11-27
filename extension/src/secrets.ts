import * as path from "path";
import * as vscode from "vscode";

const SECRET_KEY = "codeown.apiKey";

// Doc API key tu SecretStorage cua VS Code
export async function getApiKey(context: vscode.ExtensionContext): Promise<string | undefined> {
  return context.secrets.get(SECRET_KEY);
}

// Luu API key vao SecretStorage (khong ghi ra file)
export async function setApiKey(context: vscode.ExtensionContext, apiKey: string): Promise<void> {
  await context.secrets.store(SECRET_KEY, apiKey);
}

// Xoa API key khoi SecretStorage
export async function deleteApiKey(context: vscode.ExtensionContext): Promise<void> {
  await context.secrets.delete(SECRET_KEY);
}

// Hien hop thoai nhap API key cho nguoi dung
export async function promptSetApiKey(context: vscode.ExtensionContext): Promise<boolean> {
  const input = await vscode.window.showInputBox({
    prompt: "Nhập API Key cho CodeOwn (lưu an toàn trong VS Code SecretStorage)",
    password: true,
    placeHolder: "sk-..."
  });
  if (input === undefined) {
    return false;
  }
  const trimmed = input.trim();
  if (!trimmed) {
    await deleteApiKey(context);
    vscode.window.showInformationMessage("Đã xoá API Key khỏi CodeOwn.");
    return true;
  }
  await setApiKey(context, trimmed);
  vscode.window.showInformationMessage("Đã lưu API Key thành công.");
  return true;
}

export interface PythonRuntimeEnv {
  pythonPath: string;
  env: NodeJS.ProcessEnv;
}

// Tao bien moi truong cho tien trinh con python -m codeown
export function buildProcessEnv(workspaceRoot: string, apiKey?: string): PythonRuntimeEnv {
  const config = vscode.workspace.getConfiguration("codeown");
  const env: NodeJS.ProcessEnv = { ...process.env };

  if (apiKey) {
    env["API_KEY"] = apiKey;
  }

  const modelProvider = config.get<string>("modelProvider")?.trim();
  if (modelProvider) {
    env["MODEL_PROVIDER"] = modelProvider;
  }

  const modelSmall = config.get<string>("modelSmall")?.trim();
  if (modelSmall) {
    env["CODEOWN_MODEL_SMALL"] = modelSmall;
  }

  const modelStrong = config.get<string>("modelStrong")?.trim();
  if (modelStrong) {
    env["CODEOWN_MODEL_STRONG"] = modelStrong;
  }

  const corePathSetting = config.get<string>("corePath")?.trim();
  const corePath = corePathSetting || path.join(workspaceRoot, "codebase");
  const existing = env["PYTHONPATH"] || "";
  env["PYTHONPATH"] = existing ? `${corePath}${path.delimiter}${existing}` : corePath;

  const pythonPath = config.get<string>("pythonPath")?.trim() || "python3";
  return { pythonPath, env };
}
