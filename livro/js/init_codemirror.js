const codemirrorOptions = {
  lineNumbers: true,
  mode: {name: "python", version: 3, singleLineStringErrors: false},
  indentUnit: 4,
  matchBrackets: true,
  extraKeys: {
    "Shift-Enter": function(cm) {
      cm.save();
      sendTextareaValue(cm.getTextArea().id);
    }
  }
};
