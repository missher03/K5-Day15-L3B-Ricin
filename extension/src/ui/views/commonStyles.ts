export const commonStyles = `
  :root {
    --container-padding: 16px;
    --spacing-unit: 8px;
    --border-radius: 4px;
  }
  body {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    color: var(--vscode-foreground);
    background-color: var(--vscode-editor-background);
    padding: var(--container-padding);
    margin: 0;
    line-height: 1.4;
  }
  h1, h2, h3, h4 {
    color: var(--vscode-editor-foreground);
    margin-top: 0;
  }
  button {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    background-color: var(--vscode-button-background);
    color: var(--vscode-button-foreground);
    border: 1px solid var(--vscode-contrastBorder, transparent);
    border-radius: var(--border-radius);
    padding: 6px 12px;
    cursor: pointer;
    font-weight: 500;
  }
  button:hover {
    background-color: var(--vscode-button-hoverBackground);
  }
  button.secondary {
    background-color: var(--vscode-button-secondaryBackground);
    color: var(--vscode-button-secondaryForeground);
  }
  button.secondary:hover {
    background-color: var(--vscode-button-secondaryHoverBackground);
  }
  input, textarea, select {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    background-color: var(--vscode-input-background);
    color: var(--vscode-input-foreground);
    border: 1px solid var(--vscode-input-border);
    border-radius: var(--border-radius);
    padding: 6px 8px;
    width: 100%;
    box-sizing: border-box;
    margin-top: 4px;
    margin-bottom: 8px;
  }
  input:focus, textarea:focus, select:focus {
    outline: 1px solid var(--vscode-focusBorder);
    border-color: var(--vscode-focusBorder);
  }
  pre, code {
    font-family: var(--vscode-editor-font-family);
    font-size: var(--vscode-editor-font-size);
    background-color: var(--vscode-textCodeBlock-background);
    color: var(--vscode-editor-foreground);
    border-radius: var(--border-radius);
  }
  pre {
    padding: 10px;
    overflow-x: auto;
    border: 1px solid var(--vscode-panel-border);
  }
  .card {
    background-color: var(--vscode-sideBar-background);
    border: 1px solid var(--vscode-panel-border);
    border-radius: var(--border-radius);
    padding: 12px;
    margin-bottom: 12px;
  }
  .badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
  }
  .badge-hieu { background-color: rgba(0, 200, 0, 0.2); color: var(--vscode-charts-green); }
  .badge-mot-phan { background-color: rgba(200, 200, 0, 0.2); color: var(--vscode-charts-yellow); }
  .badge-chua-hieu { background-color: rgba(200, 0, 0, 0.2); color: var(--vscode-charts-red); }
`;
