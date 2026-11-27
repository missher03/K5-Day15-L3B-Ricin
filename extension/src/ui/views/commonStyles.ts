// CSS toi gian dung bien --vscode-* goc, tu dong an Dark va Light theme
export const commonStyles = `
  * { box-sizing: border-box; }
  body {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    color: var(--vscode-foreground);
    background-color: var(--vscode-editor-background);
    padding: 14px;
    margin: 0;
    line-height: 1.5;
  }
  body.sidebar-body {
    background-color: var(--vscode-sideBar-background);
    padding: 10px 12px;
  }
  h2, h3, h4 {
    color: var(--vscode-foreground);
    margin: 0 0 8px 0;
    font-weight: 600;
  }
  p { margin: 0 0 8px 0; }
  .muted { color: var(--vscode-descriptionForeground); font-size: 12px; }
  .card {
    border: 1px solid var(--vscode-panel-border);
    border-radius: 4px;
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  .row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .between { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  button {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    background-color: var(--vscode-button-background);
    color: var(--vscode-button-foreground);
    border: 1px solid var(--vscode-contrastBorder, transparent);
    border-radius: 3px;
    padding: 5px 10px;
    cursor: pointer;
  }
  button:hover:not(:disabled) { background-color: var(--vscode-button-hoverBackground); }
  button:disabled { opacity: 0.55; cursor: not-allowed; }
  button.secondary {
    background-color: var(--vscode-button-secondaryBackground);
    color: var(--vscode-button-secondaryForeground);
  }
  button.secondary:hover:not(:disabled) { background-color: var(--vscode-button-secondaryHoverBackground); }
  textarea {
    font-family: var(--vscode-font-family);
    font-size: var(--vscode-font-size);
    background-color: var(--vscode-input-background);
    color: var(--vscode-input-foreground);
    border: 1px solid var(--vscode-input-border);
    border-radius: 3px;
    padding: 6px 8px;
    width: 100%;
    resize: vertical;
  }
  textarea:focus { outline: 1px solid var(--vscode-focusBorder); }
  pre, code {
    font-family: var(--vscode-editor-font-family);
    font-size: var(--vscode-editor-font-size);
    background-color: var(--vscode-textCodeBlock-background);
    border-radius: 3px;
  }
  code { padding: 1px 4px; }
  pre {
    padding: 8px 10px;
    overflow-x: auto;
    border: 1px solid var(--vscode-panel-border);
    margin: 6px 0 10px 0;
  }
  .prog { display: flex; gap: 4px; margin: 8px 0 12px 0; }
  .prog span { flex: 1; height: 4px; border-radius: 2px; background: var(--vscode-panel-border); }
  .prog span.on { background: var(--vscode-button-background); }
  .split { display: flex; height: 7px; border-radius: 3px; overflow: hidden; border: 1px solid var(--vscode-panel-border); margin: 6px 0; }
  .split .ai { background: var(--vscode-testing-iconPassed, #2ea043); }
  .split .ed { background: var(--vscode-editorWarning-foreground, #d29922); }
  .split .me { background: var(--vscode-descriptionForeground); }
  .chip {
    display: inline-block;
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 3px;
    border: 1px solid currentColor;
  }
  .chip.hieu { color: var(--vscode-testing-iconPassed, #2ea043); }
  .chip.mot_phan { color: var(--vscode-editorWarning-foreground, #d29922); }
  .chip.chua_hieu { color: var(--vscode-errorForeground, #f85149); }
  .src { font-family: var(--vscode-editor-font-family); font-size: 11px; color: var(--vscode-descriptionForeground); }
  ul.clean { margin: 4px 0 8px 0; padding-left: 18px; }
  .hidden { display: none; }
`;
