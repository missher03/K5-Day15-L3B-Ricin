import * as vscode from "vscode";

const SECRET_KEY = "codeown.apiKey";

export async function getApiKey(context: vscode.ExtensionContext): Promise<string | undefined> {
  return await context.secrets.get(SECRET_KEY);
}

export async function setApiKey(context: vscode.ExtensionContext, apiKey: string): Promise<void> {
  await context.secrets.store(SECRET_KEY, apiKey);
}

export async function deleteApiKey(context: vscode.ExtensionContext): Promise<void> {
  await context.secrets.delete(SECRET_KEY);
}

export async function promptSetApiKey(context: vscode.ExtensionContext): Promise<boolean> {
  const input = await vscode.window.showInputBox({
    prompt: "Nhap API Key cho CodeOwn (Anthropic / OpenAI)",
    password: true,
    placeHolder: "sk-...",
  });
  if (input !== undefined) {
    await setApiKey(context, input.trim());
    vscode.window.showInformationMessage("Da luu API Key thanh cong.");
    return true;
  }
  return false;
}

export function buildProcessEnv(context: vscode.ExtensionContext, workspaceRoot: string, apiKey?: string): NodeJS.ProcessEnv {
  const config = vscode.workspace.getConfiguration("codeown");
  const env: NodeJS.ProcessEnv = { ...process.env };

  if (apiKey) {
    env["API_KEY"] = apiKey;
  }

  const modelProvider = config.get<string>("modelProvider");
  if (modelProvider) {
    env["MODEL_PROVIDER"] = modelProvider;
  }

  const modelSmall = config.get<string>("modelSmall");
  if (modelSmall) {
    env["CODEOWN_MODEL_SMALL"] = modelSmall;
  }

  const modelStrong = config.get<string>("modelStrong");
  if (modelStrong) {
    env["CODEOWN_MODEL_STRONG"] = modelStrong;
  }

  const corePathSetting = config.get<string>("corePath");
  const pythonPath = config.get<string>("pythonPath") || "python3";
  
  let codePath = workspaceRoot;
  if (corePathSetting && corePathSetting.trim() !== "") {
    codePath = corePathSetting.trim();
  }

  // Set PYTHONPATH to include codePath
  const existingPythonPath = env["PYTHONPATH"] || "";
  env["PYTHONPATH"] = existingPythonPath ? `${codePath}:${existingPythonPath}` : codePath;
  env["PYTHON_EXECUTABLE"] = pythonPath;

  return env;
}
