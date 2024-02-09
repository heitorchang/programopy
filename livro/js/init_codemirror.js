const codemirrorOptions = {
  theme: "ambiance",
  lineNumbers: false,
  mode: {name: "python", version: 3, singleLineStringErrors: false},
  indentUnit: 4,
  matchBrackets: true,
  extraKeys: {
    "Shift-Enter": function(cm) {
      cm.save();
      sendTextarea(cm.getTextArea().id);
    },
    "Ctrl-I": function(cm) {
      term.focus();
    },
  }
};
