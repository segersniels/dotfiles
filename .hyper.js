// Future versions of Hyper may add additional config options,
// which will not automatically be merged into this file.
// See https://hyper.is#cfg for all currently supported options.

module.exports = {
  config: {
    fontSize: 16,
    fontFamily: 'Hack, Menlo, "DejaVu Sans Mono", Consolas, "Lucida Console", monospace',
    fontWeight: "normal",
    fontWeightBold: "bold",
    lineHeight: 1,
    letterSpacing: 0,
    updateChannel: "canary",
    cursorAccentColor: "#000",
    cursorShape: "BLOCK",
    cursorBlink: true,
    foregroundColor: "#fff",
    backgroundColor: "#000",
    borderColor: "#333",
    padding: "12px 14px",
    shellArgs: ["--login"],
    env: {},
    bell: "SOUND",
    copyOnSelect: false,
    defaultSSHApp: true,
    quickEdit: false,
    macOptionSelectionMode: "vertical",
    scrollback: 5000,
    smooth: {
      variant: 'dark',
      disableAutomaticTheming: false,
    },
    hyperTabs: {
      trafficButtons: true,
      border: true,
      activityColor: 'salmon',
    }
  },
  plugins: [
    "hypercwd",
    "hyper-search",
    "hyperterm-paste",
    "hyper-smooth",
    "hyper-highlight-active-pane",
    "hyper-dark-scrollbar",
    "hyper-tabs-enhanced"
  ],
  localPlugins: [],
  keymaps: {
    "tab:next": ["command+right", "command+shift+right"],
    "tab:prev": ["command+left", "command+shift+left"],
    "editor:movePreviousWord": "alt+left",
    "editor:moveNextWord": "alt+right",
    "editor:moveEndLine": "alt+shift+right",
    "editor:moveBeginningLine": "alt+shift+left"
  }
};
